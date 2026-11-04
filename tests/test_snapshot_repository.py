"""A renda variável por tipo no snapshot, gravada e lida pelo histórico da carteira."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import Engine, update
from sqlalchemy.orm import Session

from backend.core import repository
from backend.core.enum import AssetClass
from backend.core.models.models import Snapshots
from backend.core.runtime.simulation_manager import SimulationManager
from tests.fakes import client, simulation_settings

DAY = date(2020, 1, 6)
NEXT_DAY = date(2020, 1, 7)


@pytest.fixture
def match(database: Engine, monkeypatch: pytest.MonkeyPatch) -> int:
    """Um jogador numa partida ativa; devolve o `user_id`."""
    user = repository.user.create_user(client("Ana"), "Ana")
    simulation_id = repository.simulation.create_simulation(simulation_settings())
    monkeypatch.setattr(SimulationManager, "_active_simulation", object())
    monkeypatch.setattr(SimulationManager, "_simulation_id", simulation_id)
    return user.id


def forget_equity_by_class(database: Engine, user_id: int, day: date) -> None:
    """Deixa o snapshot do dia como os gravados antes da divisão por tipo."""
    with Session(database) as session, session.begin():
        session.execute(
            update(Snapshots)
            .where(Snapshots.user_id == user_id, Snapshots.snapshot_date == day)
            .values(equity_by_class=None)
        )


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


def test_history_of_a_day_recorded_before_the_split_has_no_equity_by_class(
    match: int, database: Engine
):
    repository.snapshot.create_snapshot(
        match, DAY, Decimal(100), Decimal(0), Decimal(0), {AssetClass.ETF: Decimal(100)}
    )
    forget_equity_by_class(database, match, DAY)

    [point] = repository.portfolio.get_patrimonial_history(match)

    assert point.equity_by_class is None
    assert point.total_equity == Decimal(100)
