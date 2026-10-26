"""As abas da partida em andamento montadas uma vez por mês e as séries afinadas em partida longa."""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest
from pydantic import BaseModel
from sqlalchemy import Engine

from backend.core import repository
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.player_history import PlayerHistoryDTO
from backend.core.dto.simulation import SimulationDTO
from backend.core.enum import PlayerGrouping, TeamNaming
from backend.core.player_colors import PLAYER_COLORS
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.utils import next_business_day
from backend.features.simulation.simulation import Simulation
from backend.features.statistics.cache import ReportCache, match_cache
from backend.features.statistics.report import build_risk_report
from backend.features.statistics.sampling import chart_period, thin
from backend.features.statistics.score import score_history
from backend.routes.statistics import get_overview
from tests.conftest import SetIndicator
from tests.fakes import simulation_settings


class Report(BaseModel):
    label: str


def report(label: str) -> Report:
    return Report(label=label)


def test_report_is_built_once_until_cleared():
    cache = ReportCache()
    builds = []

    def build() -> Report:
        builds.append(1)
        return report("a")

    first = cache.report("overview", build)
    assert cache.report("overview", build) is first
    assert len(builds) == 1

    cache.clear()
    assert cache.report("overview", build) is not first
    assert len(builds) == 2


def test_report_built_across_a_clear_serves_only_its_request():
    """O mês virou enquanto montava: quem pediu leva o montado, o próximo monta de novo."""
    cache = ReportCache()

    def build_while_month_turns() -> Report:
        cache.clear()
        return report("antes da virada")

    stale = cache.report("overview", build_while_month_turns)
    fresh = cache.report("overview", lambda: report("depois da virada"))

    assert stale is not fresh


def test_cache_is_only_for_the_running_match(monkeypatch: pytest.MonkeyPatch):
    match = SimpleNamespace(
        settings=SimpleNamespace(id=7), backtest=None, statistics=ReportCache()
    )
    monkeypatch.setattr(SimulationManager, "_active_simulation", None)
    assert match_cache([7]) is None

    monkeypatch.setattr(SimulationManager, "_active_simulation", match)
    assert match_cache([7]) is match.statistics
    assert match_cache([3]) is None
    assert match_cache([7, 3]) is None

    monkeypatch.setattr(match, "backtest", object())
    assert match_cache([7]) is None


def test_chart_period_grows_with_the_match():
    start = date(2020, 1, 1)

    assert chart_period(start, start + timedelta(days=366)) == "day"
    assert chart_period(start, start + timedelta(days=367)) == "week"
    assert chart_period(start, start + timedelta(days=5 * 366)) == "week"
    assert chart_period(start, start + timedelta(days=5 * 366 + 1)) == "month"


def test_thin_keeps_the_first_day_and_the_close_of_each_period():
    days = [date(2020, 1, 1) + timedelta(days=i) for i in range(70)]

    assert thin(days, lambda d: d, "month") == [
        date(2020, 1, 1),
        date(2020, 1, 31),
        date(2020, 2, 29),
        date(2020, 3, 10),
    ]
    assert thin(days, lambda d: d, "day") == days
    # Semana ISO: segunda a domingo; 05/01/2020 é domingo
    assert thin(days, lambda d: d, "week")[:3] == [
        date(2020, 1, 1),
        date(2020, 1, 5),
        date(2020, 1, 12),
    ]


def history(networths: list[str], start: date = date(2020, 1, 1)):
    return [
        PatrimonialHistoryDTO(
            snapshot_date=start + timedelta(days=i),
            total_networth=Decimal(value),
            total_equity=Decimal(0),
            total_fixed=Decimal(0),
            total_cash=Decimal(value),
            total_contribution=Decimal(0),
        )
        for i, value in enumerate(networths)
    ]


def oscillating(days: int) -> list[str]:
    return [str(10000 + (i % 7) * 37 + i * 3) for i in range(days)]


def test_score_history_reuses_closed_months_and_recomputes_today(
    indicators: SetIndicator,
):
    """150 dias desde 01/01/2020: março e abril fecharam; 29/05 é hoje e muda a cada dia."""
    days = history(oscillating(150))
    closed: dict[date, Decimal | None] = {}

    assert score_history(days, closed) == score_history(days)
    assert set(closed) == {
        date(2020, 1, 31),
        date(2020, 2, 29),
        date(2020, 3, 31),
        date(2020, 4, 30),
    }
    assert closed[date(2020, 1, 31)] is None

    closed[date(2020, 3, 31)] = Decimal(42)
    points = score_history(days, closed)

    assert points[0].value == Decimal(42)
    assert points[-1].date == date(2020, 5, 29)
    assert date(2020, 5, 29) not in closed


def test_long_match_sends_weekly_series_and_comparison_keeps_every_day(
    monkeypatch: pytest.MonkeyPatch, indicators: SetIndicator
):
    """Dois anos de snapshots: a partida sozinha recebe uma semana por ponto; entre duas, um pregão por ponto."""
    days = history(oscillating(731))
    players = [
        PlayerHistoryDTO(
            player_nickname=name,
            color="chart-1",
            simulation_id=simulation_id,
            simulation_name=f"Simulação #{simulation_id}",
            starting_cash=Decimal(10000),
            goal_net_worth=Decimal(100000),
            history=days,
        )
        for simulation_id, name in [(1, "Ana"), (2, "Bia")]
    ]
    monkeypatch.setattr(
        repository.statistics,
        "get_players_history",
        lambda ids: [p for p in players if p.simulation_id in ids],
    )
    monkeypatch.setattr(repository.statistics, "get_players_credit", lambda _ids: {})
    monkeypatch.setattr(
        repository.simulation,
        "get_simulation",
        lambda _id: SimpleNamespace(
            is_backtest=False,
            team_naming=TeamNaming.COLOR,
            player_grouping=PlayerGrouping.INDIVIDUAL,
        ),
    )

    alone = build_risk_report([1]).players[0]
    compared = build_risk_report([1, 2]).players[0]

    assert len(compared.drawdown) == 730
    assert 100 < len(alone.drawdown) < 110
    assert alone.drawdown[-1] == compared.drawdown[-1]
    assert alone.max_drawdown == compared.max_drawdown


@pytest.fixture
def running_match(
    market: Engine, monkeypatch: pytest.MonkeyPatch
) -> Iterator[Simulation]:
    user = repository.user.create_user(uuid.uuid4(), "Ana")
    monkeypatch.setattr(SimulationManager, "_active_simulation", None)
    monkeypatch.setattr(SimulationManager, "_simulation_id", None)
    monkeypatch.setattr(EventManager, "_events", [])
    monkeypatch.setattr(EventManager, "_touched_users", set())
    monkeypatch.setattr(
        RealtimeBrokerManager,
        "get_broker",
        lambda: SimpleNamespace(notify=lambda *_a, **_kw: None),
    )
    settings = simulation_settings().model_copy(
        update={"start_date": date(2003, 3, 27), "end_date": date(2003, 6, 30)}
    )
    simulation_id = repository.simulation.create_simulation(settings)
    repository.simulation_player.save(simulation_id, {user.id: PLAYER_COLORS[0]})
    repository.user.seed_simulation_users(
        simulation_id, [user.id], settings.start_date, settings.starting_cash
    )
    SimulationManager.set_simulation_id(simulation_id)
    sim = Simulation(
        SimulationDTO(id=simulation_id, **settings.model_dump()), random_seed=7
    )
    SimulationManager.register_simulation(sim)
    yield sim


def days_played(simulation: Simulation) -> int:
    return get_overview([simulation.settings.id]).players[0].days


def test_overview_waits_for_the_month_turn_and_resume_starts_fresh(
    running_match: Simulation,
):
    """27/03 a 31/03 servem o relatório do primeiro pedido; 01/04 vira o mês e monta outro."""
    sim = running_match
    assert days_played(sim) == 1

    sim.next_tick()  # 28/03
    sim.next_tick()  # 31/03
    assert days_played(sim) == 1

    sim.next_tick()  # 01/04: virada do mês
    assert days_played(sim) == 4

    sim.next_tick()  # 02/04
    assert days_played(sim) == 4

    # A retomada parte do último dia gravado com um cache novo
    resumed = Simulation(
        sim.settings, resume_from=sim.get_current_date(), random_seed=7
    )
    SimulationManager.register_simulation(resumed)
    assert resumed.get_current_date() == next_business_day(date(2003, 4, 2))
    assert days_played(resumed) == 6
