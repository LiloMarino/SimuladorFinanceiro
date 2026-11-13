"""A renda variável por tipo no snapshot, gravada e lida pelo histórico da carteira."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import Engine

from backend.core import repository
from backend.core.enum import AssetClass
from backend.core.runtime.simulation_manager import SimulationManager
from tests.fakes import client, simulation_settings

DAY = date(2020, 1, 6)
NEXT_DAY = date(2020, 1, 7)


@pytest.fixture
def match(database: Engine, monkeypatch: pytest.MonkeyPatch) -> int:
    """Um jogador numa partida ativa; devolve o `portfolio_id`."""
    user = repository.user.create_user(client("Ana"), "Ana")
    simulation_id = repository.simulation.create_simulation(simulation_settings())
    monkeypatch.setattr(SimulationManager, "_active_simulation", object())
    monkeypatch.setattr(SimulationManager, "_simulation_id", simulation_id)
    return repository.portfolio.create(simulation_id, [user.id])[user.id]


def test_history_returns_the_equity_by_class_that_was_recorded(match: int):
    by_class = {AssetClass.STOCK: Decimal("120.5"), AssetClass.FII: Decimal("190")}
    repository.snapshot.create_snapshot(
        match, DAY, Decimal("310.5"), Decimal(0), Decimal(0), by_class
    )
    repository.snapshot.create_snapshot(
        match, NEXT_DAY, Decimal(0), Decimal(0), Decimal(0), {}
    )

    history = repository.portfolio.get_patrimonial_history(match)

    # Um dia sem renda variável é `{}`, não nulo: a divisão foi gravada e está vazia
    assert [point.equity_by_class for point in history] == [by_class, {}]
