from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import cast

import pandas as pd
import pytest

from backend.core import repository
from backend.core.dto.candle_challenge import ChallengeDirection, ChallengeRecordDTO
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    ForbiddenError,
    UnprocessableEntityError,
)
from backend.features.achievements.metrics import METRICS, Context
from backend.features.candle_challenge import service
from backend.features.technical_analysis.assistance import ensure_chart_hints
from tests.fakes import client, simulation_settings
from tests.test_achievements import SETTINGS, snapshot
from tests.test_candle_patterns import HAMMER_SHAPE, Row, flat, frame, trend

TICKER = "PETR4"

# Um martelo no último pregão, depois de uma queda
HAMMER_TODAY: list[Row] = [*trend("down"), HAMMER_SHAPE]
DOJI_TODAY: list[Row] = [*trend("down"), (15.0, 15.5, 14.5, 15.02)]


@pytest.fixture
def match(database: object) -> tuple[int, int]:
    """Um jogador e uma partida no banco; devolve `(user_id, simulation_id)`."""
    user = repository.user.create_user(client("Ana"), "Ana")
    simulation_id = repository.simulation.create_simulation(simulation_settings())
    return user.id, simulation_id


def session_day(rows: list[Row], position: int = -1) -> date:
    return cast(pd.Timestamp, frame(rows).index[position]).date()


def current(match: tuple[int, int], rows: list[Row]):
    user_id, simulation_id = match
    return service.current(simulation_id, user_id, TICKER, frame(rows))


def answer(
    match: tuple[int, int], rows: list[Row], direction: ChallengeDirection = "up"
):
    user_id, simulation_id = match
    return service.answer(simulation_id, user_id, TICKER, direction, frame(rows))


def settle(match: tuple[int, int], rows: list[Row]) -> None:
    _, simulation_id = match
    service.settle(simulation_id, lambda _: frame(rows))


def test_pattern_today_opens_the_question(match: tuple[int, int]):
    result = current(match, HAMMER_TODAY)

    assert result.open is not None
    assert result.open.pattern_code == "hammer"
    assert result.open.pattern_date == session_day(HAMMER_TODAY)
    assert result.last is None
    assert (result.score.hits, result.score.answered) == (0, 0)


def test_doji_does_not_open_a_question(match: tuple[int, int]):
    assert current(match, DOJI_TODAY).open is None


def test_answering_closes_the_question_and_waits_for_five_sessions(
    match: tuple[int, int],
):
    result = answer(match, HAMMER_TODAY, "up")

    assert result.open is None
    assert result.last is not None
    assert result.last.status == "waiting"
    assert result.last.direction == "up"
    assert result.last.sessions_left == 5
    assert result.last.price == pytest.approx(15.2)


def test_waiting_counts_the_sessions_left(match: tuple[int, int]):
    answer(match, HAMMER_TODAY, "up")

    result = current(match, [*HAMMER_TODAY, *flat(15.6, 15.8)])

    assert result.last is not None
    assert result.last.sessions_left == 3
    assert result.last.current_price == pytest.approx(15.8)
    assert result.last.change == pytest.approx(15.8 / 15.2 - 1)


def test_second_answer_to_the_same_pattern_is_refused(match: tuple[int, int]):
    answer(match, HAMMER_TODAY, "up")

    with pytest.raises(ConflictError):
        answer(match, HAMMER_TODAY, "down")


def test_answer_needs_a_pattern_in_the_last_session(match: tuple[int, int]):
    with pytest.raises(UnprocessableEntityError):
        answer(match, [*HAMMER_TODAY, *flat(15.6)])
    with pytest.raises(UnprocessableEntityError):
        answer(match, DOJI_TODAY)


@pytest.mark.parametrize(
    ("direction", "closes", "status", "score"),
    [
        ("up", (16, 17, 18, 19, 20), "hit", (1, 1)),
        ("down", (16, 17, 18, 19, 20), "miss", (0, 1)),
        ("down", (14, 13, 12, 11, 10), "hit", (1, 1)),
        ("up", (14, 13, 12, 11, 15.2), "void", (0, 0)),
    ],
)
def test_settle_checks_the_close_of_the_fifth_session(
    match: tuple[int, int], direction, closes, status, score
):
    answer(match, HAMMER_TODAY, direction)

    later = [*HAMMER_TODAY, *flat(*closes)]
    settle(match, later)
    result = current(match, later)

    assert result.last is not None
    assert result.last.status == status
    assert result.last.current_price == pytest.approx(closes[-1])
    assert (result.score.hits, result.score.answered) == score


def test_settle_waits_while_there_are_fewer_than_five_sessions(
    match: tuple[int, int],
):
    answer(match, HAMMER_TODAY, "up")

    settle(match, [*HAMMER_TODAY, *flat(16, 17, 18, 19)])

    _, simulation_id = match
    assert len(repository.candle_challenge.waiting(simulation_id)) == 1


def test_unanswered_pattern_expires_the_next_session(match: tuple[int, int]):
    result = current(match, [*HAMMER_TODAY, *flat(15.4)])

    assert result.open is None
    assert result.last is not None
    assert result.last.status == "expired"
    assert result.last.direction is None


def test_expired_disappears_one_session_later(match: tuple[int, int]):
    result = current(match, [*HAMMER_TODAY, *flat(15.4, 15.5)])

    assert result.last is None


def test_stats_come_with_the_answer(match: tuple[int, int]):
    result = answer(match, HAMMER_TODAY, "up")

    assert result.last is not None
    assert result.last.stats.code == "hammer"


def test_ranking_orders_by_hits_then_by_rate(match: tuple[int, int]):
    ana, simulation_id = match
    bia = repository.user.create_user(client("Bia"), "Bia")
    caio = repository.user.create_user(client("Caio"), "Caio")
    # Bia e Caio empatam em 2 acertos; Caio acertou todas e passa na frente
    plan = {
        ana: ["hit"],
        bia.id: ["hit", "hit", "miss", "miss"],
        caio.id: ["hit", "hit"],
    }
    for user_id, results in plan.items():
        for offset, result in enumerate(results):
            day = date(2020, 3, 2 + offset)
            record = ChallengeRecordDTO(
                simulation_id=simulation_id,
                user_id=user_id,
                ticker=TICKER,
                pattern_date=day,
                pattern_code="hammer",
                direction="up",
                answered_on=day,
                result=None,
                settled_on=None,
            )
            repository.candle_challenge.create(record)
            repository.candle_challenge.settle(record, result, day)

    ranking = service.ranking([simulation_id])

    assert [(p.player_nickname, p.hits, p.answered) for p in ranking.players] == [
        ("Caio", 2, 2),
        ("Bia", 2, 4),
        ("Ana", 1, 1),
    ]
    assert [p.position for p in ranking.players] == [1, 2, 3]


def test_ranking_is_empty_when_nobody_was_checked(match: tuple[int, int]):
    answer(match, HAMMER_TODAY, "up")

    assert service.ranking([match[1]]).players == []


def test_rewind_drops_later_answers_and_reopens_later_settlements(
    match: tuple[int, int],
):
    user_id, simulation_id = match
    answer(match, HAMMER_TODAY, "up")
    later = [*HAMMER_TODAY, *flat(16, 17, 18, 19, 20)]
    settle(match, later)
    pattern_day = session_day(HAMMER_TODAY)

    # Parou antes da conferência: a resposta fica esperando de novo
    repository.candle_challenge.rewind(simulation_id, session_day(later, -2))
    record = repository.candle_challenge.get(
        simulation_id, user_id, TICKER, pattern_day
    )
    assert record is not None
    assert record.result is None

    # Parou antes da resposta: ela sai
    repository.candle_challenge.rewind(simulation_id, date(2020, 1, 1))
    assert (
        repository.candle_challenge.get(simulation_id, user_id, TICKER, pattern_day)
        is None
    )


def test_candle_hits_metric_counts_the_checked_hits(
    match: tuple[int, int], monkeypatch: pytest.MonkeyPatch
):
    user_id, simulation_id = match
    answer(match, HAMMER_TODAY, "up")
    settle(match, [*HAMMER_TODAY, *flat(16, 17, 18, 19, 20)])
    settings = SETTINGS.model_copy(update={"id": simulation_id})

    context = Context(user_id, settings, snapshot())

    assert METRICS["candle_challenge_hits"].compute(context) == Decimal(1)


def test_hints_off_refuses_patterns_and_challenge():
    off = simulation_settings().model_copy(update={"show_chart_hints": False})

    with pytest.raises(ForbiddenError):
        ensure_chart_hints(off)
    ensure_chart_hints(simulation_settings())
