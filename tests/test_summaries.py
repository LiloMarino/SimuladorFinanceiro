"""A retrospectiva do ano, entregue a cada jogador na virada do ano."""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest
from sqlalchemy import Engine

from backend.core import repository
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.simulation import SimulationDTO
from backend.core.dto.summaries import YearReviewDTO
from backend.core.dto.user import UserDTO
from backend.core.player_colors import PLAYER_COLORS
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.simulation.simulation import Simulation
from backend.features.summaries.summary import year_review
from tests.conftest import SetIndicator
from tests.fakes import simulation_settings


def snapshot(day: date, networth: int, contribution: int = 0) -> PatrimonialHistoryDTO:
    return PatrimonialHistoryDTO(
        snapshot_date=day,
        total_networth=Decimal(networth),
        total_equity=Decimal(0),
        total_fixed=Decimal(0),
        total_cash=Decimal(networth),
        total_contribution=Decimal(contribution),
    )


def test_year_review_compounds_the_months_and_starts_from_the_last_snapshot_before_the_year(
    indicators: SetIndicator,
):
    """O aporte entra no patrimônio, mas não na rentabilidade: dezembro rende -5%, não +0,5%."""
    history = [
        snapshot(date(2001, 12, 31), 10000),
        snapshot(date(2002, 11, 4), 11000),
        # 10.950 - 500 de aporte = 10.450: o dia rendeu -5% sobre 11.000
        snapshot(date(2002, 12, 30), 10950, contribution=500),
    ]

    review = year_review(2002, history, Decimal(1), Decimal("0.02"))

    assert isinstance(review, YearReviewDTO)
    assert review.networth_start == 10000
    assert review.networth_end == 10950
    # 1,10 x 0,95 - 1
    assert review.return_pct == Decimal("0.045")
    assert review.cdi_pct == 0
    assert review.ibov_pct == Decimal("0.02")
    assert review.contributions == 500
    assert [(m.month.month, m.networth_end) for m in review.months] == [
        (11, 11000),
        (12, 10950),
    ]
    assert review.best_month is not None
    assert review.best_month.month == date(2002, 11, 1)
    assert review.worst_month is not None
    assert review.worst_month.month == date(2002, 12, 1)


def test_first_year_starts_from_the_starting_cash_and_one_month_has_no_worst(
    indicators: SetIndicator,
):
    history = [
        snapshot(date(2002, 11, 26), 10000),
        snapshot(date(2002, 11, 27), 10100),
    ]

    review = year_review(2002, history, Decimal(10000), None)

    assert review is not None
    assert review.networth_start == 10000
    assert review.return_pct == Decimal("0.01")
    assert review.ibov_pct is None
    assert review.best_month is not None
    assert review.worst_month is None


def test_year_without_measured_return_has_no_rate(indicators: SetIndicator):
    review = year_review(
        2002, [snapshot(date(2002, 11, 26), 10000)], Decimal(10000), None
    )

    assert review is not None
    assert review.return_pct is None
    assert review.months == []
    assert review.best_month is None


def test_year_without_snapshot_has_no_review():
    history = [snapshot(date(2001, 12, 31), 10000)]

    assert year_review(2002, history, Decimal(10000), None) is None


@pytest.fixture
def match_of_ana(
    market: Engine, monkeypatch: pytest.MonkeyPatch
) -> Iterator[tuple[Simulation, UserDTO, list[tuple[str, object, object]]]]:
    """Partida de Ana de 26/11/2002 a 10/01/2003, com os avisos guardados."""
    user = repository.user.create_user(uuid.uuid4(), "Ana")
    sent: list[tuple[str, object, object]] = []
    monkeypatch.setattr(SimulationManager, "_active_simulation", None)
    monkeypatch.setattr(SimulationManager, "_simulation_id", None)
    monkeypatch.setattr(SimulationManager, "_portfolios", {})
    monkeypatch.setattr(EventManager, "_events", [])
    monkeypatch.setattr(EventManager, "_touched_portfolios", set())
    monkeypatch.setattr(
        RealtimeBrokerManager,
        "get_broker",
        lambda: SimpleNamespace(
            notify=lambda event, payload, to=None: sent.append((event, payload, to))
        ),
    )
    settings = simulation_settings().model_copy(
        update={"start_date": date(2002, 11, 26), "end_date": date(2003, 1, 10)}
    )
    simulation_id = repository.simulation.create_simulation(settings)
    repository.simulation_player.save(simulation_id, {user.id: PLAYER_COLORS[0]})
    portfolios = repository.portfolio.open(
        simulation_id, [user.id], settings.start_date, settings.starting_cash
    )
    SimulationManager.set_simulation_id(simulation_id, portfolios)
    sim = Simulation(
        SimulationDTO(id=simulation_id, **settings.model_dump()), random_seed=7
    )
    SimulationManager.register_simulation(sim)
    yield sim, user, sent


def test_only_the_year_turn_delivers_the_review(
    match_of_ana: tuple[Simulation, UserDTO, list[tuple[str, object, object]]],
):
    sim, ana, sent = match_of_ana
    simulation_id = sim.settings.id

    # Os meses viram em dezembro, mas só o ano que vira traz retrospectiva
    while sim.get_current_date() < date(2002, 12, 20):
        sim.next_tick()
    assert repository.summaries.of_player(simulation_id, ana.id) == []

    while sim.get_current_date() < date(2003, 1, 6):
        sim.next_tick()

    entries = repository.summaries.of_player(simulation_id, ana.id)
    assert [(e.content.kind, e.game_date.month) for e in entries] == [
        ("YEAR_REVIEW", 1)
    ]
    review = entries[0].content
    assert review.year == 2002
    assert review.networth_start == sim.settings.starting_cash
    assert [m.month.month for m in review.months] == [11, 12]

    delivered = [to for event, _, to in sent if event == "summary_delivered"]
    assert delivered == [ana.client_id]


def test_each_player_sees_only_the_own_reviews(
    match_of_ana: tuple[Simulation, UserDTO, list[tuple[str, object, object]]],
):
    sim, ana, _ = match_of_ana
    simulation_id = sim.settings.id
    bia = repository.user.create_user(uuid.uuid4(), "Bia")
    content = year_review(
        2002, [snapshot(date(2002, 11, 26), 10000)], Decimal(10000), None
    )
    assert content is not None
    older = repository.summaries.create(
        simulation_id, ana.id, date(2003, 1, 2), content
    )
    newer = repository.summaries.create(
        simulation_id, ana.id, date(2004, 1, 2), content
    )
    repository.summaries.create(simulation_id, bia.id, date(2003, 1, 2), content)

    summaries = repository.summaries.of_player(simulation_id, ana.id)

    assert [s.id for s in summaries] == [newer.id, older.id]
