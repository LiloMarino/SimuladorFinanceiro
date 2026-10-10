from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.events.base_event import BaseEventDTO
from backend.core.dto.events.cashflow import CashflowEventDTO
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.events.fixed_income import FixedIncomeEventDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.dto.sector import StockSegmentDTO
from backend.core.dto.stock import StockDTO
from backend.core.enum import (
    AssetClass,
    CashflowEventType,
    EquityEventType,
    FixedIncomeEventType,
    FixedIncomeType,
    RateIndexType,
)
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
        repository.user,
        "get_total_cashflow",
        lambda _user_id, event_type: {
            CashflowEventType.CONTRIBUTION: Decimal("600"),
            CashflowEventType.TAX: Decimal("0"),
        }[event_type],
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
