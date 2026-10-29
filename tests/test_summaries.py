"""O resumo do mês e a retrospectiva do ano, entregues a cada jogador na virada."""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest
from sqlalchemy import Engine

from backend.core import repository
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.simulation import SimulationDTO
from backend.core.dto.summaries import (
    MonthSummaryDTO,
    PositionResultDTO,
    RankingMoveDTO,
    YearReviewDTO,
)
from backend.core.dto.user import UserDTO
from backend.core.enum import CashflowEventType, EquityEventType
from backend.core.player_colors import PLAYER_COLORS
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.simulation.simulation import Simulation
from backend.features.summaries.summary import (
    month_summary,
    position_results,
    ranking_move,
    year_review,
)
from tests.conftest import SetIndicator
from tests.fakes import simulation_settings

NOVEMBER = date(2002, 11, 1)


def snapshot(day: date, networth: int, contribution: int = 0) -> PatrimonialHistoryDTO:
    return PatrimonialHistoryDTO(
        snapshot_date=day,
        total_networth=Decimal(networth),
        total_equity=Decimal(0),
        total_fixed=Decimal(0),
        total_cash=Decimal(networth),
        total_contribution=Decimal(contribution),
    )


def position(ticker: str, result: int) -> PositionResultDTO:
    return PositionResultDTO(
        ticker=ticker, name=ticker, result=Decimal(result), result_pct=None
    )


def test_month_summary_starts_from_the_last_snapshot_before_the_month(
    indicators: SetIndicator,
):
    """O aporte entra no patrimônio, mas não na rentabilidade: a cota só sobe 1% no mês."""
    history = [
        snapshot(date(2002, 10, 31), 10000),
        snapshot(date(2002, 11, 4), 10100),
        # 10.600 - 500 de aporte = 10.100: o dia rendeu zero
        snapshot(date(2002, 11, 29), 10600, contribution=500),
    ]
    ranking = RankingMoveDTO(position=2, players=3, change=1)

    summary = month_summary(
        NOVEMBER,
        history,
        Decimal(10000),
        {CashflowEventType.TAX: Decimal(30), CashflowEventType.DIVIDEND: Decimal(12)},
        [position("VALE3", -30), position("PETR4", 55), position("ITUB4", 5)],
        Decimal("0.02"),
        ranking,
    )

    assert summary is not None
    assert summary.networth_start == 10000
    assert summary.networth_end == 10600
    assert summary.return_pct == Decimal("0.01")
    assert summary.cdi_pct == 0
    assert summary.ibov_pct == Decimal("0.02")
    assert summary.contributions == 500
    assert summary.income_tax == 30
    assert summary.dividends == 12
    assert summary.best_position is not None
    assert summary.best_position.ticker == "PETR4"
    assert summary.worst_position is not None
    assert summary.worst_position.ticker == "VALE3"
    assert summary.ranking == ranking


def test_first_month_starts_from_the_starting_cash_and_one_position_has_no_worst():
    summary = month_summary(
        NOVEMBER,
        [snapshot(date(2002, 11, 26), 10000)],
        Decimal(10000),
        {},
        [position("PETR4", 10)],
        None,
        None,
    )

    assert summary is not None
    assert summary.networth_start == 10000
    assert summary.return_pct is None
    assert summary.worst_position is None
    assert summary.dividends == 0


def test_month_without_snapshot_has_no_summary():
    assert (
        month_summary(
            NOVEMBER,
            [snapshot(date(2002, 10, 31), 10000)],
            Decimal(10000),
            {},
            [],
            None,
            None,
        )
        is None
    )


def trade(ticker: str, kind: EquityEventType, day: date, quantity: int, price: int):
    return EquityEventDTO(
        simulation_id=1,
        user_id=1,
        event_date=day,
        ticker=ticker,
        event_type=kind,
        quantity=Decimal(quantity),
        price=Decimal(price),
    )


def test_position_result_counts_the_value_change_and_the_trades_of_the_month():
    buy, sell = EquityEventType.BUY, EquityEventType.SELL
    events = [
        trade("ITUB4", buy, date(2002, 9, 2), 10, 30),
        trade("ITUB4", sell, date(2002, 9, 20), 10, 31),
        trade("PETR4", buy, date(2002, 10, 10), 10, 20),
        trade("VALE3", buy, date(2002, 10, 10), 10, 50),
        trade("PETR4", buy, date(2002, 11, 5), 5, 22),
        trade("VALE3", sell, date(2002, 11, 10), 10, 45),
        # Depois do mês: fica de fora
        trade("PETR4", buy, date(2002, 12, 2), 100, 25),
    ]

    results = position_results(
        events,
        NOVEMBER,
        date(2002, 11, 30),
        {"PETR4": Decimal(21), "VALE3": Decimal(48), "ITUB4": Decimal(30)},
        {"PETR4": Decimal(25), "VALE3": Decimal(44), "ITUB4": Decimal(30)},
        {"PETR4": "Petrobras"},
    )

    by_ticker = {r.ticker: r for r in results}
    assert set(by_ticker) == {"PETR4", "VALE3"}
    # 15 x 25 - 10 x 21 - 5 x 22 = 375 - 210 - 110 = 55, sobre 210 + 110 = 320
    assert by_ticker["PETR4"].result == 55
    assert by_ticker["PETR4"].result_pct == Decimal(55) / Decimal(320)
    assert by_ticker["PETR4"].name == "Petrobras"
    # 0 - 10 x 48 + 10 x 45 = -30, sobre 480
    assert by_ticker["VALE3"].result == -30
    assert by_ticker["VALE3"].result_pct == Decimal("-0.0625")
    assert by_ticker["VALE3"].name == "VALE3"


def test_ranking_move_compares_with_the_previous_summary():
    previous = MonthSummaryDTO(
        month=date(2002, 10, 1),
        networth_start=Decimal(1),
        networth_end=Decimal(1),
        return_pct=None,
        cdi_pct=Decimal(0),
        ibov_pct=None,
        best_position=None,
        worst_position=None,
        dividends=Decimal(0),
        income_tax=Decimal(0),
        contributions=Decimal(0),
        ranking=RankingMoveDTO(position=3, players=4, change=None),
    )

    assert ranking_move(1, 4, previous).change == 2
    assert ranking_move(4, 4, previous).change == -1
    assert ranking_move(1, 4, None).change is None


def summary_of(
    month: date, value: str | None, ibov: str | None, start: int, end: int
) -> MonthSummaryDTO:
    return MonthSummaryDTO(
        month=month,
        networth_start=Decimal(start),
        networth_end=Decimal(end),
        return_pct=Decimal(value) if value is not None else None,
        cdi_pct=Decimal("0.01"),
        ibov_pct=Decimal(ibov) if ibov is not None else None,
        best_position=None,
        worst_position=None,
        dividends=Decimal(0),
        income_tax=Decimal(0),
        contributions=Decimal(100),
        ranking=None,
    )


def test_year_review_compounds_the_months_of_the_year():
    months = [
        summary_of(date(2001, 12, 1), "0.5", "0.5", 1, 1),
        summary_of(date(2002, 10, 1), None, "0.03", 10000, 10000),
        summary_of(date(2002, 11, 1), "0.10", "0.05", 10000, 11000),
        summary_of(date(2002, 12, 1), "-0.05", "0.02", 11000, 10450),
    ]

    review = year_review(2002, months)

    assert isinstance(review, YearReviewDTO)
    assert review.networth_start == 10000
    assert review.networth_end == 10450
    # 1,10 x 0,95 - 1
    assert review.return_pct == Decimal("0.045")
    # 1,01³ - 1: o mês sem rentabilidade também teve CDI
    assert review.cdi_pct == Decimal("1.01") ** 3 - 1
    # 1,03 x 1,05 x 1,02 - 1
    assert review.ibov_pct == Decimal("1.03") * Decimal("1.05") * Decimal("1.02") - 1
    assert review.contributions == 300
    assert [m.month.month for m in review.months] == [11, 12]
    assert review.best_month is not None
    assert review.best_month.month == date(2002, 11, 1)
    assert review.worst_month is not None
    assert review.worst_month.month == date(2002, 12, 1)
    assert year_review(2003, months) is None


@pytest.fixture
def match_of_ana(
    market: Engine, monkeypatch: pytest.MonkeyPatch
) -> Iterator[tuple[Simulation, UserDTO, list[tuple[str, object, object]]]]:
    """Partida de Ana de 26/11/2002 a 10/01/2003, com os avisos guardados."""
    user = repository.user.create_user(uuid.uuid4(), "Ana")
    sent: list[tuple[str, object, object]] = []
    monkeypatch.setattr(SimulationManager, "_active_simulation", None)
    monkeypatch.setattr(SimulationManager, "_simulation_id", None)
    monkeypatch.setattr(EventManager, "_events", [])
    monkeypatch.setattr(EventManager, "_touched_users", set())
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
    repository.user.seed_simulation_users(
        simulation_id, [user.id], settings.start_date, settings.starting_cash
    )
    SimulationManager.set_simulation_id(simulation_id)
    sim = Simulation(
        SimulationDTO(id=simulation_id, **settings.model_dump()), random_seed=7
    )
    SimulationManager.register_simulation(sim)
    yield sim, user, sent


def test_month_turns_deliver_the_summaries_and_the_year_review(
    match_of_ana: tuple[Simulation, UserDTO, list[tuple[str, object, object]]],
):
    sim, ana, sent = match_of_ana
    simulation_id = sim.settings.id
    # O 1º pregão também vira o mês, mas novembro só tinha começado
    assert repository.summaries.of_player(simulation_id, ana.id) == []

    while sim.get_current_date() < date(2003, 1, 6):
        sim.next_tick()

    entries = repository.summaries.of_player(simulation_id, ana.id)
    kinds = [(e.content.kind, e.game_date.month) for e in entries]
    assert kinds == [("YEAR_REVIEW", 1), ("MONTH_SUMMARY", 1), ("MONTH_SUMMARY", 12)]
    review, december, november = (e.content for e in entries)
    assert isinstance(november, MonthSummaryDTO)
    assert isinstance(december, MonthSummaryDTO)
    assert isinstance(review, YearReviewDTO)
    assert november.month == NOVEMBER
    assert november.networth_start == sim.settings.starting_cash
    assert november.ranking == RankingMoveDTO(position=1, players=1, change=None)
    assert december.networth_start == november.networth_end
    assert december.ranking == RankingMoveDTO(position=1, players=1, change=0)
    assert review.year == 2002
    assert review.networth_end == december.networth_end

    delivered = [to for event, _, to in sent if event == "summary_delivered"]
    assert delivered == [ana.client_id] * 3


def test_each_player_sees_only_the_own_summaries(
    match_of_ana: tuple[Simulation, UserDTO, list[tuple[str, object, object]]],
):
    sim, ana, _ = match_of_ana
    simulation_id = sim.settings.id
    bia = repository.user.create_user(uuid.uuid4(), "Bia")
    content = summary_of(NOVEMBER, "0.01", None, 1, 1)
    older = repository.summaries.create(
        simulation_id, ana.id, date(2002, 12, 2), content
    )
    newer = repository.summaries.create(
        simulation_id, ana.id, date(2003, 1, 2), content
    )
    repository.summaries.create(simulation_id, bia.id, date(2002, 12, 2), content)

    summaries = repository.summaries.of_player(simulation_id, ana.id)

    assert [s.id for s in summaries] == [newer.id, older.id]
