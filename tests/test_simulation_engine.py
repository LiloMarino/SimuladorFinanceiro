from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import cast

import pytest

from backend.core import repository
from backend.core.dto.events.base_event import BaseEventDTO
from backend.core.dto.events.cashflow import CashflowEventDTO
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.events.fixed_income import FixedIncomeEventDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.dto.sector import StockSegmentDTO
from backend.core.dto.simulation import SimulationDTO
from backend.core.dto.stock import StockDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import (
    AssetClass,
    CashflowEventType,
    EquityEventType,
    FixedIncomeEventType,
    FixedIncomeType,
    OrderAction,
    RateIndexType,
)
from backend.core.runtime.event_manager import EventManager
from backend.features.simulation.simulation import Simulation
from backend.features.simulation.simulation_engine import SimulationEngine
from backend.features.variable_income.entities.candle import Candle
from backend.features.variable_income.entities.position import Position
from tests.fakes import USER_ID, client

PLAYER = client("player")
TODAY = date(2020, 1, 6)
STARTING_CASH = Decimal("1000")
FIXED_ASSET = FixedIncomeAssetDTO(
    name="CDB Teste",
    issuer="Banco Teste",
    investment_type=FixedIncomeType.CDB,
    rate_index=RateIndexType.PREFIXADO,
    maturity_date=date(2021, 1, 6),
    interest_rate=Decimal("0.12"),
)


@pytest.fixture
def player_book(monkeypatch: pytest.MonkeyPatch, captured_events: list[BaseEventDTO]):
    """
    Carteira persistida do jogador: R$ 880 em caixa, R$ 600 de aportes,
    10 ações compradas a R$ 10 e R$ 1.000 num CDB aplicado hoje.
    """
    monkeypatch.setattr(
        repository.user, "get_user_balance", lambda _client_id: Decimal("880")
    )
    monkeypatch.setattr(
        repository.user, "get_total_contribution", lambda _user_id: Decimal("600")
    )
    monkeypatch.setattr(
        repository.user,
        "get_total_cashflow",
        lambda _user_id, event_type: {CashflowEventType.TAX: Decimal("0")}[event_type],
    )
    monkeypatch.setattr(
        repository.credit, "get_events", lambda _simulation_id, _user_id: []
    )
    monkeypatch.setattr(
        repository.portfolio, "get_patrimonial_history", lambda _user_id: []
    )
    monkeypatch.setattr(
        repository.stock,
        "get_stocks",
        lambda: [
            StockDTO(id=1, ticker="ABCD", name="Abcd", asset_class=AssetClass.STOCK)
        ],
    )
    monkeypatch.setattr(
        repository.stock,
        "get_classification",
        lambda: {"ABCD": StockSegmentDTO(sector="Financeiro", segment="Bancos")},
    )
    monkeypatch.setattr(
        repository.portfolio,
        "get_equity_events",
        lambda _user_id: [
            EquityEventDTO(
                simulation_id=1,
                user_id=USER_ID,
                event_date=TODAY,
                ticker="ABCD",
                event_type=EquityEventType.BUY,
                quantity=10,
                price=Decimal("10"),
            )
        ],
    )
    monkeypatch.setattr(
        repository.fixed_income,
        "get_events",
        lambda _simulation_id, _user_id: [
            (
                FIXED_ASSET,
                FixedIncomeEventDTO(
                    simulation_id=1,
                    user_id=USER_ID,
                    asset_id=1,
                    event_type=FixedIncomeEventType.BUY,
                    amount=Decimal("1000"),
                    event_date=TODAY,
                ),
            )
        ],
    )


def _engine() -> SimulationEngine:
    return SimulationEngine(TODAY, STARTING_CASH, simulation_id=1)


def _cashflows(events: list[BaseEventDTO]) -> list[tuple[CashflowEventType, Decimal]]:
    return [(e.event_type, e.amount) for e in events if isinstance(e, CashflowEventDTO)]


def test_portfolio_values_and_shares(player_book):
    """Patrimônio soma caixa, ações a preço de mercado e renda fixa; frações saem dele."""
    engine = _engine()
    engine.matching_engine.market_data.add_candle(
        Candle("ABCD", TODAY, open=11, high=12.5, low=10.5, close=12, volume=100)
    )

    portfolio = engine.get_portfolio(PLAYER)

    # 880 em caixa + 10 x R$ 12 + R$ 1.000 em CDB
    assert portfolio.cash == Decimal("880")
    assert portfolio.variable_income_value == Decimal("120")
    assert portfolio.fixed_income_value == Decimal("1000")
    assert portfolio.invested_value == Decimal("1120")
    assert portfolio.total_networth == Decimal("2000")
    assert portfolio.invested_pct == Decimal("0.56")
    assert portfolio.variable_income_pct == Decimal(120) / Decimal(1120)
    assert portfolio.fixed_income_pct == Decimal(1000) / Decimal(1120)
    # Aportes não contam como retorno: (2000 - (1000 + 600)) / 1600
    assert portfolio.total_return_pct == Decimal("0.25")
    assert portfolio.variable_income[0].return_value == Decimal("20")
    assert portfolio.fixed_income[0].return_value == 0
    assert [(s.sector, s.value, s.fraction) for s in portfolio.sectors] == [
        ("Financeiro", Decimal("120"), Decimal("1"))
    ]


def test_current_price_without_candle_is_average_price(player_book):
    """Sem candle no buffer, o preço atual da posição é o preço médio."""
    position = Position("WXYZ")
    position.update_buy(Decimal("7.5"), 2)

    assert _engine().get_current_price(position) == Decimal("7.5")


def test_stock_catalog_is_reused_and_reloaded_for_a_new_simulation(
    player_book, monkeypatch: pytest.MonkeyPatch
):
    get_stocks = repository.stock.get_stocks
    calls = []

    def load():
        calls.append(True)
        return get_stocks()

    monkeypatch.setattr(repository.stock, "get_stocks", load)
    engine = _engine()
    first = engine.get_portfolio(PLAYER)
    assert engine.get_portfolio(PLAYER) == first
    engine.assess_income_tax(USER_ID)
    engine.preview_order(PLAYER, "ABCD", OrderAction.SELL, 1, 12)
    assert calls == [True]

    # O catálogo não é global: uma nova partida vê o que a Central alterou.
    _engine().assess_income_tax(USER_ID)
    assert calls == [True, True]


def test_add_cash_records_deposit_or_withdraw(player_book, captured_events):
    """Entrada de caixa vira DEPOSIT, saída vira WITHDRAW pelo valor absoluto."""
    engine = _engine()

    engine.add_cash(PLAYER, Decimal("120"))
    engine.add_cash(PLAYER, Decimal("-50"))

    assert engine.get_cash(PLAYER) == Decimal("950")
    assert _cashflows(captured_events) == [
        (CashflowEventType.DEPOSIT, Decimal("120")),
        (CashflowEventType.WITHDRAW, Decimal("50")),
    ]


def test_contribution_is_recorded_apart_from_deposit(player_book, captured_events):
    """Aporte mensal entra no caixa como CONTRIBUTION, separado de depósito."""
    engine = _engine()

    engine.add_contribution(PLAYER, Decimal("300"))

    assert engine.get_cash(PLAYER) == Decimal("1180")
    assert _cashflows(captured_events) == [
        (CashflowEventType.CONTRIBUTION, Decimal("300"))
    ]


def test_income_tax_payment_is_recorded_as_tax(player_book, captured_events):
    """O DARF sai do caixa como TAX, separado de um saque comum."""
    engine = _engine()

    engine.pay_income_tax(PLAYER, Decimal("750"))

    assert engine.get_cash(PLAYER) == Decimal("130")
    assert _cashflows(captured_events) == [(CashflowEventType.TAX, Decimal("750"))]


def test_preview_buy_uses_limit_price_and_cash(player_book):
    """Compra limitada: total pelo limite, caixa depois e o máximo que o caixa paga."""
    preview = _engine().preview_order(PLAYER, "ABCD", OrderAction.BUY, 10, 12.0)

    assert preview.price == Decimal("12.0")
    assert preview.total == Decimal("120.0")
    assert preview.cash_after == Decimal("760.0")
    assert preview.max_quantity == 73  # 880 // 12
    assert preview.tax is None


def _next_day_engine() -> SimulationEngine:
    """Um pregão depois da compra: a venda não é day trade."""
    return SimulationEngine(date(2020, 1, 7), STARTING_CASH, simulation_id=1)


def test_preview_sell_within_exemption_has_no_tax(player_book):
    """Venda que deixa o mês abaixo de R$ 20 mil em ações: lucro sem IR."""
    preview = _next_day_engine().preview_order(
        PLAYER, "ABCD", OrderAction.SELL, 10, 15.0
    )

    assert preview.max_quantity == 10
    assert preview.profit == Decimal("50.0")
    assert preview.month_stock_sales_after == Decimal("150.0")
    assert preview.tax == 0


def test_preview_sell_above_exemption_pays_fifteen_percent(player_book):
    """Venda que passa dos R$ 20 mil no mês: 15% sobre o lucro."""
    preview = _next_day_engine().preview_order(
        PLAYER, "ABCD", OrderAction.SELL, 10, 2500.0
    )

    # Lucro (2500 - 10) x 10 = 24.900; 15% = 3.735
    assert preview.profit == Decimal("24900.0")
    assert preview.tax == Decimal("3735.00")
    assert preview.tax_due_date is not None


def test_player_joining_mid_match_gets_the_starting_deposit_and_the_day_snapshot(
    player_book, captured_events, monkeypatch: pytest.MonkeyPatch
):
    """Quem entra com a partida em andamento recebe o depósito inicial datado de hoje e o snapshot do dia."""
    sim = object.__new__(Simulation)
    sim._engine = _engine()
    sim.settings = cast("SimulationDTO", SimpleNamespace(starting_cash=Decimal("500")))
    snapshots = []
    monkeypatch.setattr(
        Simulation, "_snapshot_user", lambda _, user: snapshots.append(user)
    )
    monkeypatch.setattr(EventManager, "flush", lambda: None)
    user = UserDTO(id=USER_ID, client_id=PLAYER, nickname="Duda")

    sim.add_player(user)

    assert _cashflows(captured_events) == [(CashflowEventType.DEPOSIT, Decimal("500"))]
    assert [e.event_date for e in captured_events] == [TODAY]
    assert snapshots == [user]
