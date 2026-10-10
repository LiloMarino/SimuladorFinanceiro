from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import AssetClass, EquityEventType
from backend.features.import_data.importer_service import infer_asset_class
from backend.features.simulation.simulation import Simulation
from backend.features.variable_income.income_tax import (
    LossPool,
    MonthlyTax,
    assess,
    darf_due_date,
)
from tests.fakes import USER_ID, client

CLASSES = {
    "ABCD3": AssetClass.STOCK,
    "WXYZ3": AssetClass.STOCK,
    "EFGH11": AssetClass.FII,
    "IJKL11": AssetClass.ETF,
    "MNOP34": AssetClass.BDR,
}


def _event(
    event_type: EquityEventType, ticker: str, day: date, quantity: int, price: str
) -> EquityEventDTO:
    return EquityEventDTO(
        simulation_id=1,
        user_id=USER_ID,
        event_date=day,
        ticker=ticker,
        event_type=event_type,
        quantity=quantity,
        price=Decimal(price),
    )


def _buy(ticker: str, day: date, quantity: int, price: str) -> EquityEventDTO:
    return _event(EquityEventType.BUY, ticker, day, quantity, price)


def _sell(ticker: str, day: date, quantity: int, price: str) -> EquityEventDTO:
    return _event(EquityEventType.SELL, ticker, day, quantity, price)


def _assess(*events: EquityEventDTO) -> dict[tuple[int, int], MonthlyTax]:
    """Apura até o último evento e indexa os meses por (ano, mês)."""
    ordered = sorted(events, key=lambda e: e.event_date)
    months = assess(ordered, CLASSES, ordered[-1].event_date)
    return {(m.year, m.month): m for m in months}


def test_selling_30k_with_5k_profit_debits_750_next_month():
    """Aceite: R$ 30.000 vendidos com R$ 5.000 de lucro geram DARF de R$ 750."""
    months = _assess(
        _buy("ABCD3", date(2024, 1, 10), 1000, "25"),
        _sell("ABCD3", date(2024, 2, 5), 1000, "30"),
    )

    assert months[(2024, 2)].darf_amount == Decimal("750.00")
    assert months[(2024, 2)].due_date == date(2024, 3, 29)


def test_selling_15k_with_profit_debits_nothing():
    """Aceite: vendas de ações até R$ 20.000 no mês são isentas."""
    months = _assess(
        _buy("ABCD3", date(2024, 1, 10), 500, "25"),
        _sell("ABCD3", date(2024, 2, 5), 500, "30"),
    )

    assert months[(2024, 2)].tax == 0
    assert months[(2024, 2)].darf_amount is None
    assert months[(2024, 2)].exempt_profit == Decimal("2500")


def test_month_nets_every_sale_before_taxing():
    """Lucro de um ativo e prejuízo de outro no mesmo mês se anulam."""
    months = _assess(
        _buy("ABCD3", date(2024, 1, 10), 1000, "30"),
        _buy("WXYZ3", date(2024, 1, 10), 1000, "30"),
        _sell("ABCD3", date(2024, 3, 5), 1000, "40"),
        _sell("WXYZ3", date(2024, 3, 5), 1000, "20"),
    )

    march = months[(2024, 3)]
    assert march.tax == 0
    assert march.pools[LossPool.COMMON].loss_after == 0


def test_etf_gain_is_compensated_by_stock_loss():
    """Ação, ETF e BDR compensam prejuízo entre si, nos meses seguintes."""
    months = _assess(
        _buy("ABCD3", date(2024, 1, 10), 1000, "30"),
        _sell("ABCD3", date(2024, 2, 5), 1000, "20"),
        _buy("IJKL11", date(2024, 3, 1), 100, "100"),
        _sell("IJKL11", date(2024, 3, 5), 100, "150"),
    )

    assert months[(2024, 2)].pools[LossPool.COMMON].loss_after == Decimal("10000")
    assert months[(2024, 3)].tax == 0
    assert months[(2024, 3)].pools[LossPool.COMMON].loss_after == Decimal("5000")


def test_fii_loss_only_offsets_fii_gains():
    """Prejuízo de FII não abate ETF; abate o ganho de FII, que paga 20%."""
    months = _assess(
        _buy("EFGH11", date(2024, 1, 10), 100, "100"),
        _buy("IJKL11", date(2024, 1, 10), 100, "100"),
        _sell("EFGH11", date(2024, 2, 5), 100, "80"),
        _sell("IJKL11", date(2024, 2, 5), 100, "150"),
        _buy("EFGH11", date(2024, 4, 1), 100, "100"),
        _sell("EFGH11", date(2024, 4, 5), 100, "130"),
    )

    assert months[(2024, 2)].tax == Decimal("750.00")
    assert months[(2024, 2)].pools[LossPool.FII].loss_after == Decimal("2000")
    assert months[(2024, 4)].pools[LossPool.FII].taxable == Decimal("1000")
    assert months[(2024, 4)].tax == Decimal("200.00")


def test_day_trade_pairs_same_day_trades_and_pays_twenty_percent():
    """Compra e venda no mesmo dia viram day trade, fora do preço médio da posição."""
    months = _assess(
        _buy("ABCD3", date(2024, 1, 10), 100, "10"),
        _buy("ABCD3", date(2024, 2, 5), 100, "20"),
        _sell("ABCD3", date(2024, 2, 5), 100, "25"),
    )

    february = months[(2024, 2)]
    assert february.pools[LossPool.DAY_TRADE].taxable == Decimal("500")
    assert february.pools[LossPool.COMMON].taxable == 0
    assert february.tax == Decimal("100.00")


def test_day_trade_loss_only_offsets_day_trade_gains():
    """Prejuízo de day trade fica no conjunto dele e não abate operação comum."""
    months = _assess(
        _buy("IJKL11", date(2024, 1, 10), 100, "100"),
        _buy("ABCD3", date(2024, 2, 5), 100, "20"),
        _sell("ABCD3", date(2024, 2, 5), 100, "10"),
        _sell("IJKL11", date(2024, 2, 6), 100, "150"),
    )

    february = months[(2024, 2)]
    assert february.tax == Decimal("750.00")
    assert february.pools[LossPool.DAY_TRADE].loss_after == Decimal("1000")


def test_stock_gain_is_exempt_up_to_twenty_thousand_in_sales():
    """R$ 20.000,00 vendidos é isento; R$ 20.010,00 tributa o ganho inteiro."""
    months = _assess(
        _buy("ABCD3", date(2024, 1, 10), 2000, "5"),
        _sell("ABCD3", date(2024, 2, 5), 1000, "20"),
        _sell("ABCD3", date(2024, 3, 5), 1000, "20.01"),
    )

    assert months[(2024, 2)].tax == 0
    assert months[(2024, 2)].exempt_profit == Decimal("15000")
    assert months[(2024, 3)].exempt_profit == 0
    assert months[(2024, 3)].tax == Decimal("2251.50")


def test_stock_loss_in_exempt_month_is_compensable():
    """Prejuízo com ações num mês abaixo de R$ 20.000 de vendas ainda se acumula."""
    months = _assess(
        _buy("ABCD3", date(2024, 1, 10), 100, "50"),
        _sell("ABCD3", date(2024, 2, 5), 100, "40"),
    )

    assert months[(2024, 2)].pools[LossPool.COMMON].loss_after == Decimal("1000")


def test_etf_and_bdr_have_no_exemption():
    """A isenção dos R$ 20.000 cobre só ações."""
    months = _assess(
        _buy("IJKL11", date(2024, 1, 10), 10, "100"),
        _buy("MNOP34", date(2024, 1, 10), 10, "100"),
        _sell("IJKL11", date(2024, 2, 5), 10, "200"),
        _sell("MNOP34", date(2024, 2, 5), 10, "200"),
    )

    assert months[(2024, 2)].exempt_profit == 0
    assert months[(2024, 2)].tax == Decimal("300.00")


def test_tax_below_minimum_is_carried_until_it_reaches_it():
    """Imposto abaixo de R$ 10,00 não gera DARF e soma ao do mês seguinte."""
    months = _assess(
        _buy("IJKL11", date(2024, 1, 10), 20, "100"),
        _sell("IJKL11", date(2024, 2, 5), 10, "104"),
        _sell("IJKL11", date(2024, 3, 5), 10, "104"),
    )

    assert months[(2024, 2)].tax == Decimal("6.00")
    assert months[(2024, 2)].darf_amount is None
    assert months[(2024, 3)].darf_amount == Decimal("12.00")
    assert months[(2024, 3)].due_date == date(2024, 4, 30)


def test_december_loss_offsets_next_year_gain():
    """O prejuízo atravessa a virada do ano."""
    months = _assess(
        _buy("IJKL11", date(2023, 11, 10), 100, "100"),
        _sell("IJKL11", date(2023, 12, 5), 100, "50"),
        _buy("IJKL11", date(2023, 12, 11), 100, "100"),
        _sell("IJKL11", date(2024, 1, 10), 100, "150"),
    )

    assert months[(2024, 1)].tax == 0
    assert months[(2024, 1)].pools[LossPool.COMMON].loss_after == 0


@pytest.mark.parametrize(
    ("year", "month", "due"),
    [
        (2024, 2, date(2024, 3, 29)),
        (2024, 5, date(2024, 6, 28)),
        (2024, 12, date(2025, 1, 31)),
    ],
)
def test_darf_is_due_on_last_business_day_of_next_month(year, month, due):
    """Vencimento no último dia de semana do mês seguinte, o calendário do tick."""
    assert darf_due_date(year, month) == due


@pytest.mark.parametrize(
    ("ticker", "asset_class"),
    [
        ("PETR4.SA", AssetClass.STOCK),
        ("HGLG11.SA", AssetClass.FII),
        ("AAPL34.SA", AssetClass.BDR),
        ("VALE3", AssetClass.STOCK),
    ],
)
def test_asset_class_is_inferred_from_ticker_suffix(ticker, asset_class):
    """34 é BDR, 11 é FII e o resto é ação, com ou sem o `.SA` do yfinance."""
    assert infer_asset_class(ticker) == asset_class


class _TaxEngine:
    """Motor mínimo para o débito no tick: apura os eventos dados e anota o DARF."""

    def __init__(self, events: list[EquityEventDTO], today: date):
        self.events = events
        self.today = today
        self.paid: list[Decimal] = []

    def assess_income_tax(self, _user_id: int) -> list[MonthlyTax]:
        return assess(self.events, CLASSES, self.today)

    def pay_income_tax(self, _client_id, amount: Decimal) -> None:
        self.paid.append(amount)


@pytest.mark.parametrize(
    ("today", "paid"),
    [(date(2024, 3, 28), []), (date(2024, 3, 29), [Decimal("750.00")])],
)
def test_tick_pays_darf_only_on_due_date(today, paid):
    """O DARF de fevereiro sai do caixa no último dia útil de março, e só nele."""
    simulation = object.__new__(Simulation)
    simulation._current_date = today
    engine = _TaxEngine(
        [
            _buy("ABCD3", date(2024, 1, 10), 1000, "25"),
            _sell("ABCD3", date(2024, 2, 5), 1000, "30"),
        ],
        today,
    )
    simulation._engine = engine  # type: ignore[assignment]

    simulation._collect_income_tax(
        [UserDTO(id=USER_ID, client_id=client("player"), nickname="player")]
    )

    assert engine.paid == paid
