"""Totais de proventos e somas do retorno lidos do banco."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.events.cashflow import CashflowEventDTO
from backend.core.dto.snapshot import SnapshotDTO
from backend.core.enum import AssetClass, CashflowEventType
from backend.core.runtime.simulation_manager import SimulationManager
from tests.fakes import client, simulation_settings


@pytest.fixture
def match(database: object, monkeypatch: pytest.MonkeyPatch) -> tuple[int, int]:
    """Um jogador, uma ação e uma partida ativa no banco; devolve `(user_id, simulation_id)`."""
    user = repository.user.create_user(client("Ana"), "Ana")
    repository.stock.add_stock("ABCD", "ABCD", AssetClass.STOCK)
    simulation_id = repository.simulation.create_simulation(simulation_settings())
    monkeypatch.setattr(SimulationManager, "_simulation_id", simulation_id)
    return user.id, simulation_id


def _cashflow(
    match: tuple[int, int],
    day: date,
    event_type: CashflowEventType,
    amount: str,
    ticker: str | None = None,
) -> CashflowEventDTO:
    user_id, simulation_id = match
    return CashflowEventDTO(
        simulation_id=simulation_id,
        user_id=user_id,
        event_date=day,
        event_type=event_type,
        amount=Decimal(amount),
        ticker=ticker,
    )


def test_dividend_totals_split_the_match_from_the_recent_window(
    match: tuple[int, int],
):
    user_id, _simulation_id = match
    repository.event.insert_many(
        [
            _cashflow(
                match, date(2020, 1, 6), CashflowEventType.DIVIDEND, "40", "ABCD"
            ),
            _cashflow(
                match, date(2020, 8, 3), CashflowEventType.DIVIDEND, "25.50", "ABCD"
            ),
            _cashflow(match, date(2020, 8, 3), CashflowEventType.DEPOSIT, "999"),
        ]
    )

    totals = repository.portfolio.get_dividend_totals(user_id, date(2020, 7, 1))

    # O depósito não é provento; a janela recente só pega o de agosto
    assert totals["ABCD"].total == Decimal("65.50")
    assert totals["ABCD"].recent == Decimal("25.50")


def test_dividend_payments_come_in_date_order_with_the_asset(match: tuple[int, int]):
    user_id, _simulation_id = match
    repository.event.insert_many(
        [
            _cashflow(
                match, date(2020, 8, 3), CashflowEventType.DIVIDEND, "25", "ABCD"
            ),
            _cashflow(
                match, date(2020, 1, 6), CashflowEventType.DIVIDEND, "40", "ABCD"
            ),
        ]
    )

    payments = repository.portfolio.get_dividend_payments(user_id)

    assert [(p.ticker, p.event_date, p.amount) for p in payments] == [
        ("ABCD", date(2020, 1, 6), Decimal("40")),
        ("ABCD", date(2020, 8, 3), Decimal("25")),
    ]


def test_return_flows_stop_at_the_last_snapshot(match: tuple[int, int]):
    user_id, simulation_id = match
    last_day = date(2020, 3, 2)
    repository.snapshot.create_many(
        simulation_id,
        [
            SnapshotDTO(
                user_id=user_id,
                snapshot_date=last_day,
                total_equity=Decimal(0),
                total_fixed=Decimal(0),
                total_cash=Decimal(0),
                total_contribution=Decimal(0),
                total_debt=Decimal(0),
                total_networth=Decimal(0),
                equity_by_class=None,
                created_at=datetime.now(UTC),
            )
        ],
    )
    repository.event.insert_many(
        [
            _cashflow(match, last_day, CashflowEventType.DIVIDEND, "10", "ABCD"),
            _cashflow(match, last_day, CashflowEventType.LOAN_PAYMENT, "300"),
            _cashflow(match, last_day, CashflowEventType.CAMPAIGN_DONATION, "20"),
            _cashflow(match, last_day, CashflowEventType.CAMPAIGN_ACTION, "5"),
            _cashflow(
                match, date(2020, 3, 3), CashflowEventType.DIVIDEND, "999", "ABCD"
            ),
        ]
    )

    flows = repository.statistics.get_players_return_flows([simulation_id])

    [flow] = flows.values()
    assert flow.dividends == Decimal(10)
    assert flow.loan_payment == Decimal(300)
    assert flow.campaign == Decimal(25)
