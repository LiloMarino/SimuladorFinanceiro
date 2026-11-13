"""Eventos de caixa e de renda variável gravados e lidos de volta do banco."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.events.cashflow import CashflowEventDTO
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.enum import AssetClass, CashflowEventType, EquityEventType
from tests.fakes import client, simulation_settings

DAY = date(2020, 1, 6)


@pytest.fixture
def match(database: object) -> tuple[int, int]:
    """Um jogador, uma ação e uma partida no banco; devolve `(portfolio_id, simulation_id)`."""
    user = repository.user.create_user(client("Ana"), "Ana")
    repository.stock.add_stock("ABCD", "ABCD", AssetClass.STOCK)
    simulation_id = repository.simulation.create_simulation(simulation_settings())
    portfolio_id = repository.portfolio.create(simulation_id, [user.id])[user.id]
    return portfolio_id, simulation_id


def test_dividend_keeps_the_stock_it_came_from(match: tuple[int, int]):
    portfolio_id, simulation_id = match
    dividend = CashflowEventDTO(
        simulation_id=simulation_id,
        portfolio_id=portfolio_id,
        event_date=DAY,
        event_type=CashflowEventType.DIVIDEND,
        amount=Decimal("67.50"),
        ticker="ABCD",
    )
    deposit = CashflowEventDTO(
        simulation_id=simulation_id,
        portfolio_id=portfolio_id,
        event_date=DAY,
        event_type=CashflowEventType.DEPOSIT,
        amount=Decimal(100),
    )

    repository.event.insert_many([dividend, deposit])

    read = repository.event.get_cashflow_events(simulation_id, portfolio_id)
    assert [(e.event_type, e.amount, e.ticker) for e in read] == [
        (CashflowEventType.DIVIDEND, Decimal("67.50"), "ABCD"),
        (CashflowEventType.DEPOSIT, Decimal("100.00"), None),
    ]


def test_split_and_fraction_sale_are_not_market_flow(match: tuple[int, int]):
    portfolio_id, simulation_id = match

    def equity(kind: EquityEventType, quantity: str) -> EquityEventDTO:
        return EquityEventDTO(
            simulation_id=simulation_id,
            portfolio_id=portfolio_id,
            event_date=DAY,
            ticker="ABCD",
            event_type=kind,
            quantity=Decimal(quantity),
            price=Decimal(0),
        )

    repository.event.insert_many(
        [
            equity(EquityEventType.BUY, "10"),
            equity(EquityEventType.SPLIT, "10"),
            equity(EquityEventType.FRACTION_SELL, "0.5"),
        ]
    )

    flow = repository.event.get_daily_equity_flow(simulation_id)

    # Só a compra de 10 é pressão de mercado; o desdobramento e a fração ficam de fora
    assert [(f.ticker, f.quantity) for f in flow] == [("ABCD", Decimal(10))]
