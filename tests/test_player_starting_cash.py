"""O capital colocado de cada jogador parte do capital com que a carteira dele abriu."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import Engine

from backend.core import repository
from backend.core.dto.snapshot import DayBalanceDTO
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.statistics.ranking import build_overview
from tests.fakes import client, simulation_settings

DAY = date(2020, 1, 6)
HEIR_CASH = Decimal(500000)
GRADUATE_CASH = Decimal(0)


@pytest.fixture
def room(database: Engine, monkeypatch: pytest.MonkeyPatch) -> int:
    """Partida com o Herdeiro (R$ 500 mil) e o Recém-formado (sem caixa); devolve o `simulation_id`."""
    heir = repository.user.create_user(client("Herdeiro"), "Herdeiro")
    graduate = repository.user.create_user(client("Formado"), "Formado")
    simulation_id = repository.simulation.create_simulation(simulation_settings())
    repository.simulation_player.save(
        simulation_id, {heir.id: "chart-1", graduate.id: "chart-2"}
    )
    portfolios = repository.portfolio.open(
        simulation_id,
        [heir.id, graduate.id],
        DAY,
        Decimal(10000),
        {heir.id: HEIR_CASH, graduate.id: GRADUATE_CASH},
    )
    monkeypatch.setattr(SimulationManager, "_active_simulation", object())
    monkeypatch.setattr(SimulationManager, "_simulation_id", simulation_id)
    repository.snapshot.create_snapshots(
        DAY,
        {
            portfolios[heir.id]: _balance(Decimal(0)),
            portfolios[graduate.id]: _balance(Decimal(3000)),
        },
    )
    return simulation_id


def _balance(equity: Decimal):
    return DayBalanceDTO(equity, Decimal(0), Decimal(0), {})


def test_portfolio_keeps_the_starting_cash_of_each_player(room: int):
    portfolios = repository.portfolio.ids(room)

    cash = repository.portfolio.starting_cash(list(portfolios.values()))

    assert sorted(cash.values()) == [GRADUATE_CASH, HEIR_CASH]


def test_players_history_carries_the_own_starting_cash(room: int):
    history = {
        p.player_nickname: p for p in repository.statistics.get_players_history([room])
    }

    assert history["Herdeiro"].starting_cash == HEIR_CASH
    assert history["Formado"].starting_cash == GRADUATE_CASH


def test_ranking_measures_each_player_over_the_own_capital(room: int):
    """Herdeiro e Recém-formado entram no ranking com o capital colocado de cada um."""
    report = build_overview(repository.statistics.get_players_history([room]))

    entries = {p.player_nickname: p for p in report.players}
    # Herdeiro: patrimônio igual ao capital, retorno zero
    assert entries["Herdeiro"].return_value == Decimal(0)
    assert entries["Herdeiro"].return_percent == Decimal(0)
    # Recém-formado: sem capital colocado o retorno percentual é zero, sem divisão por zero
    assert entries["Formado"].return_percent == Decimal(0)
