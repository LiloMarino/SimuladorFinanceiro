"""Eventos de crédito e dívida do snapshot no banco."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from backend.core import repository
from backend.core.dto.events.cashflow import CashflowEventDTO
from backend.core.dto.events.credit import CreditEventDTO
from backend.core.enum import (
    CashflowEventType,
    CreditEventType,
    CreditGrade,
    PrepaymentMode,
)
from backend.core.runtime.simulation_manager import SimulationManager
from tests.fakes import client, simulation_settings

DAY = date(2020, 1, 6)


@pytest.fixture
def match(database: object, monkeypatch: pytest.MonkeyPatch) -> tuple[int, int]:
    """Um jogador numa partida ativa; devolve `(user_id, simulation_id)`."""
    user = repository.user.create_user(client("Ana"), "Ana")
    simulation_id = repository.simulation.create_simulation(simulation_settings())
    monkeypatch.setattr(SimulationManager, "_active_simulation", object())
    monkeypatch.setattr(SimulationManager, "_simulation_id", simulation_id)
    return user.id, simulation_id


def credit_event(
    user_id: int,
    simulation_id: int,
    loan_id,
    kind: CreditEventType,
    amount: str,
    **fields,
) -> CreditEventDTO:
    return CreditEventDTO(
        simulation_id=simulation_id,
        user_id=user_id,
        loan_id=loan_id,
        event_type=kind,
        amount=Decimal(amount),
        event_date=DAY,
        **fields,
    )


def test_credit_events_come_back_in_order_with_every_field(match: tuple[int, int]):
    user_id, simulation_id = match
    loan_id = uuid4()
    repository.event.insert_many(
        [
            credit_event(
                user_id,
                simulation_id,
                loan_id,
                CreditEventType.CONTRACT,
                "5000",
                annual_rate=Decimal("0.0925"),
                term_months=24,
                grade=CreditGrade.A,
            ),
            credit_event(
                user_id,
                simulation_id,
                loan_id,
                CreditEventType.PREPAYMENT,
                "800",
                prepayment_mode=PrepaymentMode.SHORTEN_TERM,
            ),
            credit_event(
                user_id,
                simulation_id,
                loan_id,
                CreditEventType.INSTALLMENT_PAID,
                "228.15",
                installment_number=1,
            ),
        ]
    )

    events = repository.credit.get_events(simulation_id, user_id)

    assert [e.event_type for e in events] == [
        CreditEventType.CONTRACT,
        CreditEventType.PREPAYMENT,
        CreditEventType.INSTALLMENT_PAID,
    ]
    assert events[0].grade is CreditGrade.A
    assert events[0].annual_rate == Decimal("0.0925")
    assert events[0].term_months == 24
    assert events[1].prepayment_mode is PrepaymentMode.SHORTEN_TERM
    assert events[2].installment_number == 1
    assert {e.loan_id for e in events} == {loan_id}
    assert repository.event.get_last_event_date(simulation_id) == DAY


def test_snapshot_networth_discounts_the_debt(match: tuple[int, int]):
    user_id, simulation_id = match
    repository.event.insert_many(
        [
            CashflowEventDTO(
                simulation_id=simulation_id,
                user_id=user_id,
                event_type=CashflowEventType.DEPOSIT,
                amount=Decimal(10000),
                event_date=DAY,
            ),
            CashflowEventDTO(
                simulation_id=simulation_id,
                user_id=user_id,
                event_type=CashflowEventType.LOAN_PROCEEDS,
                amount=Decimal(5000),
                event_date=DAY,
            ),
        ]
    )

    snapshot = repository.snapshot.create_snapshot(
        user_id, DAY, Decimal(0), Decimal(0), Decimal(5000)
    )

    # Caixa de 15.000 menos a dívida de 5.000: tomar o empréstimo não muda o patrimônio
    assert snapshot.total_cash == Decimal(15000)
    assert snapshot.total_debt == Decimal(5000)
    assert snapshot.total_networth == Decimal(10000)
