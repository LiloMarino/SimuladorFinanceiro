from __future__ import annotations

from typing import cast

import pandas as pd
import pytest

from backend.features.technical_analysis.patterns import (
    PATTERNS,
    Occurrence,
    build_candle_patterns,
    detect,
    is_hit,
    outcome,
)

type Row = tuple[float, float, float, float]


def frame(rows: list[Row]) -> pd.DataFrame:
    """Velas (abertura, máxima, mínima, fechamento) em dias úteis seguidos."""
    return pd.DataFrame(
        rows,
        columns=["open", "high", "low", "close"],
        index=pd.bdate_range("2024-01-02", periods=len(rows)),
    )


def trend(direction: str) -> list[Row]:
    """Seis pregões de queda ou de alta, para a regra de tendência anterior."""
    rows: list[Row] = []
    for step in range(6):
        close = 20 - step if direction == "down" else 10 + step
        open_ = close + 0.5 if direction == "down" else close - 0.5
        rows.append((open_, max(open_, close) + 0.1, min(open_, close) - 0.1, close))
    return rows


def codes_at_last(rows: list[Row]) -> list[str]:
    candles = frame(rows)
    return [o.code for o in detect(candles) if o.end_pos == len(candles) - 1]


HAMMER_SHAPE: Row = (15.0, 15.25, 14.2, 15.2)
INVERTED_SHAPE: Row = (15.0, 16.2, 14.95, 15.2)


def test_hammer_after_a_fall():
    assert codes_at_last([*trend("down"), HAMMER_SHAPE]) == ["hammer"]


def test_same_shape_after_a_rise_is_the_hanging_man():
    assert codes_at_last([*trend("up"), HAMMER_SHAPE]) == ["hanging_man"]


def test_no_hammer_when_the_lower_shadow_is_short():
    short_shadow: Row = (15.0, 15.25, 14.9, 15.2)
    assert codes_at_last([*trend("down"), short_shadow]) == []


def test_inverted_hammer_after_a_fall():
    assert codes_at_last([*trend("down"), INVERTED_SHAPE]) == ["inverted_hammer"]


def test_same_shape_after_a_rise_is_the_shooting_star():
    assert codes_at_last([*trend("up"), INVERTED_SHAPE]) == ["shooting_star"]


def test_no_shooting_star_when_the_upper_shadow_is_short():
    short_shadow: Row = (15.0, 15.3, 14.95, 15.2)
    assert codes_at_last([*trend("up"), short_shadow]) == []


def test_doji_has_a_tiny_body():
    assert codes_at_last([*trend("down"), (15.0, 15.5, 14.5, 15.02)]) == ["doji"]


def test_no_doji_with_a_real_body():
    assert codes_at_last([*trend("down"), (15.0, 15.5, 14.5, 15.3)]) == []


def test_flat_candle_without_range_is_not_a_doji():
    assert codes_at_last([*trend("down"), (15.0, 15.0, 15.0, 15.0)]) == []


def test_bullish_engulfing():
    rows = [*trend("down"), (16.0, 16.1, 15.4, 15.5), (15.4, 16.4, 15.3, 16.2)]
    assert codes_at_last(rows) == ["bullish_engulfing"]


def test_no_bullish_engulfing_when_the_body_does_not_cover_the_previous():
    rows = [*trend("down"), (16.0, 16.1, 15.4, 15.5), (15.6, 16.0, 15.5, 15.9)]
    assert codes_at_last(rows) == []


def test_bearish_engulfing():
    rows = [*trend("up"), (15.0, 15.6, 14.9, 15.5), (15.6, 15.7, 14.6, 14.8)]
    assert codes_at_last(rows) == ["bearish_engulfing"]


def test_no_bearish_engulfing_when_the_previous_candle_is_bearish():
    rows = [*trend("up"), (15.5, 15.6, 14.9, 15.0), (15.6, 15.7, 14.6, 14.8)]
    assert codes_at_last(rows) == []


MORNING_START: list[Row] = [(20.0, 20.1, 16.9, 17.0), (16.5, 16.7, 16.4, 16.6)]
EVENING_START: list[Row] = [(17.0, 20.1, 16.9, 20.0), (20.5, 20.6, 20.3, 20.4)]


def test_morning_star():
    rows = [*trend("down"), *MORNING_START, (16.7, 19.0, 16.6, 18.8)]
    assert codes_at_last(rows) == ["morning_star"]


def test_no_morning_star_when_the_third_candle_stays_below_the_middle():
    rows = [*trend("down"), *MORNING_START, (16.7, 18.2, 16.6, 18.0)]
    assert codes_at_last(rows) == []


def test_evening_star():
    rows = [*trend("up"), *EVENING_START, (20.3, 20.4, 17.7, 17.8)]
    assert codes_at_last(rows) == ["evening_star"]


def test_no_evening_star_when_the_middle_candle_has_a_big_body():
    big_middle: Row = (19.0, 21.0, 18.9, 20.9)
    rows = [*trend("up"), EVENING_START[0], big_middle, (20.3, 20.4, 17.7, 17.8)]
    assert codes_at_last(rows) == []


def test_three_white_soldiers():
    rows = [
        *trend("up"),
        (10.0, 11.05, 9.98, 11.0),
        (10.5, 12.05, 10.48, 12.0),
        (11.5, 13.05, 11.48, 13.0),
    ]
    assert codes_at_last(rows) == ["three_white_soldiers"]
    assert detect(frame(rows))[-1].start == frame(rows).index[-3]


def test_no_three_white_soldiers_when_the_third_closes_lower():
    rows = [
        *trend("up"),
        (10.0, 11.05, 9.98, 11.0),
        (10.5, 12.05, 10.48, 12.0),
        (11.5, 12.05, 11.48, 11.8),
    ]
    assert "three_white_soldiers" not in codes_at_last(rows)


def test_three_black_crows():
    rows = [
        *trend("down"),
        (13.0, 13.02, 11.95, 12.0),
        (12.5, 12.52, 10.95, 11.0),
        (11.5, 11.52, 9.95, 10.0),
    ]
    assert codes_at_last(rows) == ["three_black_crows"]


def test_no_three_black_crows_when_one_candle_is_bullish():
    rows = [
        *trend("down"),
        (13.0, 13.02, 11.95, 12.0),
        (11.0, 12.05, 10.95, 12.0),
        (11.5, 11.52, 9.95, 10.0),
    ]
    assert "three_black_crows" not in codes_at_last(rows)


def test_each_pregao_ends_at_most_one_pattern():
    rows = [
        *trend("up"),
        (10.0, 11.05, 9.98, 11.0),
        (10.5, 12.05, 10.48, 12.0),
        (11.5, 13.05, 11.48, 13.0),
        (13.0, 13.5, 12.0, 13.02),
    ]
    ends = [o.end_pos for o in detect(frame(rows))]
    assert len(ends) == len(set(ends))


def test_empty_history_has_no_patterns():
    assert detect(frame([])) == []


def occurrence(candles: pd.DataFrame, pos: int) -> Occurrence:
    day = cast(pd.Timestamp, candles.index[pos])
    return Occurrence("hammer", day, day, pos)


def test_outcome_is_the_move_to_the_fifth_session_after():
    closes = [10.0, 10.2, 10.4, 10.1, 10.6, 10.7, 11.0]
    candles = frame([(c, c, c, c) for c in closes])

    assert outcome(candles, occurrence(candles, 1)) == pytest.approx(11.0 / 10.2 - 1)


def test_outcome_waits_for_five_sessions():
    candles = frame([(10, 10, 10, 10)] * 6)

    assert outcome(candles, occurrence(candles, 0)) is not None
    assert outcome(candles, occurrence(candles, 1)) is None


@pytest.mark.parametrize(
    ("direction", "change", "expected"),
    [
        ("up", 0.02, True),
        ("up", -0.02, False),
        ("down", -0.02, True),
        ("down", 0.02, False),
        ("up", 0.0, None),
        ("down", 0.0, None),
        ("up", None, None),
        ("neutral", 0.05, None),
    ],
)
def test_hit_follows_the_suggested_side(direction, change, expected):
    assert is_hit(direction, change) is expected


def flat(*closes: float) -> list[Row]:
    return [(c, c, c, c) for c in closes]


def test_stats_count_only_checked_occurrences():
    # Três martelos: um com o preço subindo depois (acerta), um com o preço caindo
    # (erra) e o último sem os 5 pregões seguintes (fica fora da conta)
    rows = [
        *trend("down"),
        HAMMER_SHAPE,
        *flat(16, 17, 18, 19, 20),
        *flat(19, 18, 17, 16, 15),
        HAMMER_SHAPE,
        *flat(14, 13, 12, 11, 10),
        *flat(9, 8, 7, 6),
        HAMMER_SHAPE,
    ]
    result = build_candle_patterns(frame(rows))

    hammers = [p for p in result.patterns if p.code == "hammer"]
    assert [p.hit for p in hammers] == [True, False, None]
    stats = {s.code: s for s in result.stats}
    assert (stats["hammer"].checked, stats["hammer"].hits) == (2, 1)
    assert set(stats) == set(PATTERNS)


def test_neutral_patterns_never_count_as_checked():
    rows = [
        *trend("down"),
        (15.0, 15.5, 14.5, 15.02),
        *[(15.0, 15.0, 15.0, 15.0 + i) for i in range(6)],
    ]
    result = build_candle_patterns(frame(rows))

    doji = next(s for s in result.stats if s.code == "doji")
    assert doji.checked == 0
    assert any(p.code == "doji" and p.change_5d is not None for p in result.patterns)
