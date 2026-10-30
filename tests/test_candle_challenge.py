from __future__ import annotations

import random
from datetime import date
from typing import cast

import pandas as pd
import pytest

from backend.core import repository
from backend.core.dto.candle_challenge import (
    CandleBarDTO,
    ChallengeDirection,
    ChallengeNoticeKind,
)
from backend.core.dto.candle_patterns import PatternStatsDTO
from backend.core.dto.user import UserDTO
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    ForbiddenError,
    UnprocessableEntityError,
)
from backend.core.runtime.user_manager import UserManager
from backend.features.achievements.evaluator import unlock_from_lobby
from backend.features.achievements.metrics import METRICS, Context
from backend.features.candle_challenge import game as game_module
from backend.features.candle_challenge.game import CandleGame
from backend.features.candle_challenge.question import (
    WINDOW,
    NoQuestionError,
    Question,
    QuestionSource,
)
from backend.features.technical_analysis.assistance import ensure_chart_hints
from backend.features.technical_analysis.patterns import detect
from tests.fakes import client, simulation_settings
from tests.test_achievements import SETTINGS, snapshot
from tests.test_candle_patterns import HAMMER_SHAPE, Row, frame

# =========================
# Perguntas
# =========================


def slope(start: float, step: float, count: int) -> list[Row]:
    """Velas em linha reta; com `step` negativo é queda, e a tendência anterior sai dela."""
    rows: list[Row] = []
    for i in range(count):
        close = start + step * i
        open_ = close - step
        rows.append((open_, max(open_, close) + 0.3, min(open_, close) - 0.3, close))
    return rows


def hammer_market(after: list[float]) -> pd.DataFrame:
    """35 velas de queda, um martelo (padrão de alta) e as velas seguintes."""
    rows = [*slope(30, -0.4, 35), HAMMER_SHAPE]
    rows += [(c, c + 0.1, c - 0.1, c) for c in after]
    return frame(rows)


def hanging_man_market(after: list[float]) -> pd.DataFrame:
    """Alta seguida de um enforcado (padrão de baixa) e as velas seguintes."""
    rows = [*slope(5, 0.3, 35), (15.0, 15.25, 14.2, 15.2)]
    rows += [(c, c + 0.1, c - 0.1, c) for c in after]
    return frame(rows)


class FakeMarket:
    def __init__(self, frames: dict[str, pd.DataFrame]) -> None:
        self.frames = frames

    def tickers(self) -> list[str]:
        return list(self.frames)

    def frame(self, ticker: str) -> pd.DataFrame:
        return self.frames[ticker]


FALLING = [15.5, 15.8, 16.0, 16.2, 16.6]


def test_the_fixture_markets_end_in_the_expected_patterns():
    hammer = hammer_market(FALLING)
    assert "hammer" in [o.code for o in detect(hammer) if o.end_pos == 35]
    hanging = hanging_man_market(FALLING)
    assert "hanging_man" in [o.code for o in detect(hanging) if o.end_pos == 35]


def test_question_is_a_window_that_ends_at_the_pattern_with_five_hidden_candles():
    source = QuestionSource(FakeMarket({"AAAA3": hammer_market(FALLING)}))

    question = source.draw()

    assert question.pattern_code == "hammer"
    assert question.ticker == "AAAA3"
    assert len(question.bars) == WINDOW
    assert len(question.bars_after) == 5
    assert question.outcome == "up"
    assert question.change == pytest.approx(16.6 / 15.2 - 1)
    assert question.end > question.start


def test_axis_is_percent_from_the_first_candle_open_not_a_price():
    source = QuestionSource(FakeMarket({"AAAA3": hammer_market(FALLING)}))

    first = source.draw().bars[0]

    # A escala de preço não aparece: a primeira abertura vale 0%
    assert first.open == 0
    assert all(abs(bar.high) < 100 for bar in source.draw().bars)


def test_price_that_closes_equal_voids_the_question():
    flat_after = [15.2] * 5
    source = QuestionSource(FakeMarket({"AAAA3": hammer_market(flat_after)}))

    question = source.draw()

    assert question.outcome == "void"
    assert question.change == 0


def test_down_move_is_recorded_as_down():
    source = QuestionSource(
        FakeMarket({"AAAA3": hammer_market([15.0, 14.8, 14.6, 14.4, 14.0])})
    )

    assert source.draw().outcome == "down"


def test_doji_never_becomes_a_question():
    rows = [*slope(30, -0.4, 35), (15.0, 15.5, 14.5, 15.02)]
    rows += [(c, c + 0.1, c - 0.1, c) for c in FALLING]
    source = QuestionSource(FakeMarket({"AAAA3": frame(rows)}))

    with pytest.raises(NoQuestionError):
        source.draw()


def test_pattern_too_early_for_a_full_window_is_skipped():
    rows = [*slope(30, -0.4, 8), HAMMER_SHAPE]
    rows += [(c, c + 0.1, c - 0.1, c) for c in FALLING]
    source = QuestionSource(FakeMarket({"AAAA3": frame(rows)}))

    with pytest.raises(NoQuestionError):
        source.draw()


def test_questions_balance_rising_and_falling_patterns():
    source = QuestionSource(
        FakeMarket(
            {
                "UP": hammer_market(FALLING),
                "DOWN": hanging_man_market([14.8, 14.5, 14.2, 14.0, 13.6]),
            }
        ),
        random.Random(7),
    )

    sides = [source.draw().pattern_code for _ in range(40)]

    assert 10 <= sides.count("hammer") <= 30
    assert "hanging_man" in sides


def test_questions_already_asked_are_not_repeated():
    source = QuestionSource(
        FakeMarket({"A": hammer_market(FALLING), "B": hammer_market(FALLING)})
    )
    first = source.draw()

    second = source.draw([first.key])

    assert second.key != first.key


def test_pattern_stats_sum_the_whole_base():
    source = QuestionSource(
        FakeMarket({"A": hammer_market(FALLING), "B": hammer_market(FALLING)})
    )

    stats = source.stats("hammer")

    assert stats.checked >= 2
    assert stats.hits >= 2


# =========================
# Jogo da sala
# =========================


def user(user_id: int, name: str) -> UserDTO:
    return UserDTO(id=user_id, client_id=client(name), nickname=name)


ANA, BIA, CAIO = user(1, "Ana"), user(2, "Bia"), user(3, "Caio")


def make_question(outcome: str = "up", ticker: str = "PETR4", day: int = 2) -> Question:
    bar = CandleBarDTO(open=0, high=1, low=-1, close=0.5)
    return Question(
        ticker=ticker,
        pattern_code="hammer",
        bars=[bar] * WINDOW,
        bars_after=[bar] * 5,
        start=date(2015, 2, day),
        pattern_end=date(2015, 3, day),
        end=date(2015, 3, day),
        change=0.04 if outcome == "up" else -0.04 if outcome == "down" else 0.0,
        outcome=cast("object", outcome),  # pyright: ignore[reportArgumentType]
    )


class StubSource:
    def draw(self, exclude=()) -> Question:
        return make_question()

    def stats(self, code) -> PatternStatsDTO:
        return PatternStatsDTO(code=code, checked=1240, hits=720)


class FakeStore:
    def __init__(self, record: tuple[int, date | None] = (0, None)) -> None:
        self.hits: list[str] = []
        self.saved: list[tuple[str, int]] = []
        self._record = record

    def hit(self, user: UserDTO) -> None:
        self.hits.append(user.nickname)

    def record(self, user: UserDTO) -> tuple[int, date | None]:
        return self._record

    def save_record(self, user: UserDTO, streak: int) -> None:
        self.saved.append((user.nickname, streak))


class Room:
    def __init__(self, monkeypatch: pytest.MonkeyPatch, humans: list[UserDTO]):
        self.events: list[tuple[str, object]] = []
        self.people = {u.nickname: u for u in humans}
        monkeypatch.setattr(
            game_module,
            "notify",
            lambda event, payload, to=None: self.events.append((event, payload)),
        )
        monkeypatch.setattr(UserManager, "list_active_players", lambda: humans)
        monkeypatch.setattr(UserManager, "room_colors", lambda: {})
        self.store = FakeStore()
        self.game = CandleGame(
            cast("object", StubSource()),  # pyright: ignore[reportArgumentType]
            self.store,
            autorun=False,
        )

    def notices(self) -> list[ChallengeNoticeKind]:
        return [
            cast(dict, payload)["kind"]
            for event, payload in self.events
            if event == "candle_challenge_notice"
        ]

    def play(
        self,
        outcome: str = "up",
        answers: dict[str, ChallengeDirection] | None = None,
    ):
        """Abre uma pergunta, registra as respostas e fecha."""
        rnd = self.game._round
        assert rnd is not None
        assert self.game._open(rnd, make_question(outcome))
        for nickname, direction in (answers or {}).items():
            self.game.answer(self.people[nickname], direction)
        self.game._close(rnd)

    def state(self):
        return self.game.view(ANA).state


@pytest.fixture
def room(monkeypatch: pytest.MonkeyPatch) -> Room:
    return Room(monkeypatch, [ANA, BIA, CAIO])


def test_starter_opens_the_round_alone_and_the_others_get_the_invite(room: Room):
    room.game.start(ANA)

    state = room.state()
    assert state.status == "running"
    assert state.starter == "Ana"
    assert [p.nickname for p in state.players] == ["Ana"]
    assert not state.solo
    assert room.game.is_active()


def test_alone_in_the_room_is_solo(monkeypatch: pytest.MonkeyPatch):
    solo = Room(monkeypatch, [ANA])

    solo.game.start(ANA)

    assert solo.state().solo


def test_cannot_start_over_a_running_round(room: Room):
    room.game.start(ANA)

    with pytest.raises(ConflictError):
        room.game.start(BIA)


def test_answer_needs_an_open_question(room: Room):
    room.game.start(ANA)

    with pytest.raises(UnprocessableEntityError):
        room.game.answer(ANA, "up")


def test_open_question_hides_the_asset_the_date_and_the_next_candles(room: Room):
    room.game.start(ANA)
    rnd = room.game._round
    assert rnd is not None
    room.game._open(rnd, make_question())

    state = room.state()
    payload = state.model_dump_json()

    assert state.phase == "question"
    assert state.question is not None
    assert state.question.stats.checked == 1240
    assert state.reveal is None
    assert "PETR4" not in payload
    assert "2015" not in payload


def test_others_only_see_who_replied_never_the_side(room: Room):
    room.game.start(ANA)
    room.game.join(BIA)
    rnd = room.game._round
    assert rnd is not None
    room.game._open(rnd, make_question())
    # A entrada foi antes da pergunta abrir, então Bia joga esta
    rnd.players[BIA.id].from_seq = 1

    room.game.answer(BIA, "down")

    state = room.state()
    assert {p.nickname: p.replied for p in state.players} == {"Ana": False, "Bia": True}
    assert "down" not in state.model_dump_json()
    assert room.game.view(BIA).direction == "down"
    assert room.game.view(ANA).direction is None


def test_answer_can_be_changed_until_the_question_closes(room: Room):
    room.game.start(ANA)
    rnd = room.game._round
    assert rnd is not None
    room.game._open(rnd, make_question("up"))

    room.game.answer(ANA, "down")
    room.game.answer(ANA, "up")
    room.game._close(rnd)

    player = room.state().players[0]
    assert player.last == "hit"
    assert room.store.hits == ["Ana"]


def test_reveal_shows_the_asset_the_votes_and_marks_each_player(room: Room):
    room.game.start(ANA)
    room.game.join(BIA)
    room.game.join(CAIO)
    rnd = room.game._round
    assert rnd is not None
    for p in rnd.players.values():
        p.from_seq = 1

    room.play("up", {"Ana": "up", "Bia": "down"})

    state = room.state()
    assert state.phase == "reveal"
    assert state.reveal is not None
    assert state.reveal.ticker == "PETR4"
    assert state.reveal.outcome == "up"
    assert {v.nickname: v.direction for v in state.reveal.votes} == {
        "Ana": "up",
        "Bia": "down",
    }
    marks = {p.nickname: p.last for p in state.players}
    assert marks == {"Ana": "hit", "Bia": "miss", "Caio": "none"}
    assert state.number == 1


def test_positions_share_a_rank_on_ties(room: Room):
    room.game.start(ANA)
    room.game.join(BIA)
    room.game.join(CAIO)
    rnd = room.game._round
    assert rnd is not None
    for p in rnd.players.values():
        p.from_seq = 1

    room.play("up", {"Ana": "up", "Bia": "up"})

    positions = {p.nickname: p.position for p in room.state().players}
    assert positions == {"Ana": 1, "Bia": 1, "Caio": 3}


def test_joining_mid_question_plays_from_the_next_one(room: Room):
    room.game.start(ANA)
    rnd = room.game._round
    assert rnd is not None
    room.game._open(rnd, make_question())

    room.game.join(BIA)

    with pytest.raises(UnprocessableEntityError):
        room.game.answer(BIA, "up")
    assert room.notices() == ["joined"]
    room.game._close(rnd)
    bia = next(p for p in room.state().players if p.nickname == "Bia")
    assert bia.answered == 0
    assert bia.last is None
    assert bia.joined_at == 2

    room.play("up", {"Bia": "up"})

    bia = next(p for p in room.state().players if p.nickname == "Bia")
    assert (bia.hits, bia.answered, bia.joined_at) == (1, 1, 2)
    assert bia.marks == [None, "hit"]


def test_void_question_counts_for_nobody_and_keeps_the_number(room: Room):
    room.game.start(ANA)

    room.play("void", {"Ana": "up"})

    state = room.state()
    assert state.reveal is not None
    assert state.reveal.outcome == "void"
    assert state.reveal.votes == []
    assert state.players[0].answered == 0
    assert state.players[0].hits == 0
    assert room.store.hits == []
    assert state.number == 1

    room.play("up", {"Ana": "up"})

    assert room.state().number == 1
    assert room.state().players[0].hits == 1


def test_round_ends_after_ten_questions_with_the_winner_and_the_room_wins(room: Room):
    room.game.start(ANA)
    room.game.join(BIA)
    rnd = room.game._round
    assert rnd is not None
    for p in rnd.players.values():
        p.from_seq = 1
    for _ in range(10):
        room.play("up", {"Ana": "up", "Bia": "down"})

    assert rnd.closed == 10
    room.game._finish(rnd)

    state = room.state()
    assert state.status == "finished"
    assert state.phase is None
    assert state.final is not None
    assert state.final.winners == ["Ana"]
    assert [(w.nickname, w.wins) for w in state.wins] == [("Ana", 1)]
    assert state.rounds == 1
    assert not room.game.is_active()


def test_tie_splits_the_victory(room: Room):
    room.game.start(ANA)
    room.game.join(BIA)
    rnd = room.game._round
    assert rnd is not None
    for p in rnd.players.values():
        p.from_seq = 1
    room.play("up", {"Ana": "up", "Bia": "up"})

    room.game._finish(rnd)

    final = room.state().final
    assert final is not None
    assert final.winners == ["Ana", "Bia"]
    assert {w.nickname: w.wins for w in room.state().wins} == {"Ana": 1, "Bia": 1}


def test_nobody_wins_with_zero_hits(room: Room):
    room.game.start(ANA)
    room.game.join(BIA)
    rnd = room.game._round
    assert rnd is not None
    for p in rnd.players.values():
        p.from_seq = 1
    room.play("up", {"Ana": "down", "Bia": "down"})

    room.game._finish(rnd)

    final = room.state().final
    assert final is not None
    assert final.winners == []


def test_play_again_starts_a_new_round_after_the_end(room: Room):
    room.game.start(ANA)
    rnd = room.game._round
    assert rnd is not None
    room.game._finish(rnd)

    room.game.start(BIA)

    state = room.state()
    assert state.status == "running"
    assert state.starter == "Bia"
    assert state.rounds == 1


def test_solo_keeps_the_streak_and_beats_the_record(monkeypatch: pytest.MonkeyPatch):
    solo = Room(monkeypatch, [ANA])
    solo.store._record = (2, date(2026, 10, 24))
    solo.game.start(ANA)
    rnd = solo.game._round
    assert rnd is not None

    solo.play("up", {"Ana": "up"})
    solo.play("up", {"Ana": "up"})
    assert solo.store.saved == []
    solo.play("up", {"Ana": "up"})
    solo.play("up", {"Ana": "down"})
    solo.game._finish(rnd)

    state = solo.state()
    assert solo.store.saved[-1] == ("Ana", 3)
    assert state.streak == 0
    assert state.final is not None
    assert state.final.new_record
    assert state.final.best_streak == 3
    assert state.final.previous_record == 2
    assert state.final.previous_record_on == date(2026, 10, 24)
    assert state.final.winners == []


def test_starting_the_match_discards_the_round_and_keeps_the_hits(room: Room):
    room.game.start(ANA)
    room.play("up", {"Ana": "up"})

    room.game.abort()

    assert room.state().status == "idle"
    assert not room.game.is_active()
    assert room.notices() == ["ended_by_match"]
    assert room.store.hits == ["Ana"]
    assert room.state().rounds == 0


def test_round_empties_when_the_last_player_leaves(room: Room):
    room.game.start(ANA)

    room.game.leave(ANA.id)

    assert room.state().status == "idle"


def test_players_cannot_join_without_a_running_round(room: Room):
    with pytest.raises(ConflictError):
        room.game.join(BIA)


# =========================
# Banco: acertos totais, recorde e conquistas
# =========================


@pytest.fixture
def player(database: object) -> int:
    return repository.user.create_user(client("Ana"), "Ana").id


def test_hits_add_up_across_rounds(player: int):
    assert repository.candle_challenge.total_hits(player) == 0

    repository.candle_challenge.add_hits(player, 1)
    total = repository.candle_challenge.add_hits(player, 1)

    assert total == 2
    assert repository.candle_challenge.total_hits(player) == 2


def test_record_only_moves_up(player: int):
    assert repository.candle_challenge.record(player) == (0, None)

    repository.candle_challenge.save_record(player, 5, date(2026, 10, 1))
    repository.candle_challenge.save_record(player, 3, date(2026, 10, 2))
    repository.candle_challenge.save_record(player, 7, date(2026, 10, 3))

    assert repository.candle_challenge.record(player) == (7, date(2026, 10, 3))


def test_record_and_hits_do_not_overwrite_each_other(player: int):
    repository.candle_challenge.add_hits(player, 4)
    repository.candle_challenge.save_record(player, 2, date(2026, 10, 1))

    assert repository.candle_challenge.total_hits(player) == 4
    assert repository.candle_challenge.record(player) == (2, date(2026, 10, 1))


def test_first_hit_unlocks_first_reading_in_the_lobby(player: int):
    repository.candle_challenge.add_hits(player, 1)

    unlocked = unlock_from_lobby(player)

    assert [a.code for a in unlocked] == ["first_candle_read"]
    assert unlock_from_lobby(player) == []


def test_ten_hits_unlock_candle_reader_and_keep_progress(player: int):
    repository.candle_challenge.add_hits(player, 4)
    unlock_from_lobby(player)
    assert repository.achievements.best_progress(player)["candle_reader"] == 4

    repository.candle_challenge.add_hits(player, 6)
    unlocked = unlock_from_lobby(player)

    assert [a.code for a in unlocked] == ["candle_reader"]


def test_metric_reads_the_total_hits_of_the_player(player: int):
    repository.candle_challenge.add_hits(player, 3)
    context = Context(player, SETTINGS, snapshot())

    assert METRICS["candle_challenge_hits"].compute(context) == 3


def test_hints_off_refuses_patterns():
    off = simulation_settings().model_copy(update={"show_chart_hints": False})

    with pytest.raises(ForbiddenError):
        ensure_chart_hints(off)
    ensure_chart_hints(simulation_settings())
