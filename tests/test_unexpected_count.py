"""Contagem dos imprevistos de vida de cada jogador, lida dos eventos de caixa."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.events.cashflow import CashflowEventDTO
from backend.core.enum import CashflowEventType
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.statistics.report import _unexpected_counts
from tests.fakes import client, simulation_settings


def cashflow(
    user_id: int,
    simulation_id: int,
    event_type: CashflowEventType,
    amount: str,
    key: str | None = None,
) -> CashflowEventDTO:
    return CashflowEventDTO(
        simulation_id=simulation_id,
        user_id=user_id,
        event_type=event_type,
        amount=Decimal(amount),
        event_date=date(2020, 1, 6),
        life_event_key=key,
    )


def test_counts_each_players_unexpected_expenses_and_skips_the_layoff(
    database: object, monkeypatch: pytest.MonkeyPatch
):
    ana = repository.user.create_user(client("Ana"), "Ana")
    bia = repository.user.create_user(client("Bia"), "Bia")
    simulation_id = repository.simulation.create_simulation(simulation_settings())
    monkeypatch.setattr(SimulationManager, "_active_simulation", object())
    monkeypatch.setattr(SimulationManager, "_simulation_id", simulation_id)
    unexpected = CashflowEventType.UNEXPECTED_EXPENSE
    repository.event.insert_many(
        [
            cashflow(ana.id, simulation_id, unexpected, "5000", "REPAIR"),
            cashflow(ana.id, simulation_id, unexpected, "10000", "HEALTH"),
            cashflow(ana.id, simulation_id, unexpected, "5000", "REPAIR"),
            cashflow(ana.id, simulation_id, unexpected, "0", "LAYOFF"),
            cashflow(ana.id, simulation_id, CashflowEventType.SALARY, "8000"),
            cashflow(bia.id, simulation_id, unexpected, "5000", "REPAIR"),
        ]
    )

    counts = _unexpected_counts([simulation_id])

    assert counts == {(simulation_id, "Ana"): 3, (simulation_id, "Bia"): 1}
