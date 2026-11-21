"""O dado incremental do aviso, somado ao que a tela já tinha, é o recálculo inteiro."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from backend.core.dto.candle_patterns import CandlePatternDTO, CandlePatternsDTO
from backend.core.dto.technical_indicators import (
    IndicatorPointDTO,
    IndicatorSeriesDTO,
    IndicatorsRequestDTO,
)
from backend.features.technical_analysis.patterns import (
    build_candle_patterns,
    build_candle_patterns_update,
)
from backend.features.technical_analysis.summary import (
    build_indicators_update,
    build_technical_indicators,
)

DAYS = 160


@pytest.fixture(scope="module")
def prices() -> pd.DataFrame:
    """Passeio aleatório com semente fixa: velas de todos os formatos, com gaps e sombras."""
    rng = np.random.default_rng(42)
    close = 30 + np.cumsum(rng.normal(0, 0.8, DAYS))
    open_ = close + rng.normal(0, 0.5, DAYS)
    high = np.maximum(open_, close) + rng.uniform(0, 0.8, DAYS)
    low = np.minimum(open_, close) - rng.uniform(0, 0.8, DAYS)
    volume = rng.integers(1_000, 5_000, DAYS).astype(float)
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=pd.bdate_range("2023-01-02", periods=DAYS),
    )


def merge_patterns(
    current: CandlePatternsDTO, from_date, patterns: list[CandlePatternDTO], stats
) -> CandlePatternsDTO:
    """A mesma regra do front: troca os padrões que terminam de `from_date` em diante."""
    kept = [p for p in current.patterns if from_date is not None and p.end < from_date]
    return CandlePatternsDTO(patterns=[*kept, *patterns], stats=stats)


def test_the_incremental_patterns_equal_the_full_recalculation_every_day(
    prices: pd.DataFrame,
):
    screen = build_candle_patterns(prices.iloc[:10])
    for day in range(11, DAYS + 1):
        frame = prices.iloc[:day]
        update = build_candle_patterns_update(frame)
        screen = merge_patterns(screen, update.from_date, update.patterns, update.stats)

        assert screen == build_candle_patterns(frame), f"dia {day}"


def test_the_pattern_update_carries_only_the_recent_window(prices: pd.DataFrame):
    frame = prices.iloc[:100]
    full = build_candle_patterns(frame)

    update = build_candle_patterns_update(frame)

    from_date = update.from_date
    assert from_date == frame.index[-6].date()
    assert 0 < len(update.patterns) < len(full.patterns)
    assert from_date is not None and all(p.end >= from_date for p in update.patterns)


def points(series: IndicatorSeriesDTO) -> dict[str, list[IndicatorPointDTO]]:
    """Cada série pedida como lista de pontos, com um nome."""
    named: dict[str, list[IndicatorPointDTO]] = {}
    for average in series.averages or []:
        named[f"{average.kind}{average.period}"] = average.points
    if series.bollinger:
        named["bollinger.upper"] = series.bollinger.upper
        named["bollinger.middle"] = series.bollinger.middle
        named["bollinger.lower"] = series.bollinger.lower
    if series.macd:
        named["macd.line"] = series.macd.line
        named["macd.signal"] = series.macd.signal
        named["macd.histogram"] = series.macd.histogram
    if series.stochastic:
        named["stochastic.k"] = series.stochastic.k
        named["stochastic.d"] = series.stochastic.d
    for name in ("rsi", "atr", "obv"):
        if (value := getattr(series, name)) is not None:
            named[name] = value
    return named


REQUEST = IndicatorsRequestDTO(
    series=["averages", "bollinger", "rsi", "macd", "stochastic", "atr", "obv"]
)


def test_the_indicator_point_sent_each_day_extends_the_series_to_the_full_one(
    prices: pd.DataFrame,
):
    screen = points(build_technical_indicators(prices.iloc[:60], REQUEST).series)
    assert screen

    for day in range(61, DAYS + 1):
        frame = prices.iloc[:day]
        update = build_indicators_update(frame, REQUEST)
        for name, new_points in points(update.series).items():
            assert len(new_points) <= 1
            screen[name] = [*screen[name], *new_points]

        full = build_technical_indicators(frame, REQUEST)
        assert screen == points(full.series), f"dia {day}"
        assert update.summary == full.summary


def test_the_update_sends_a_series_only_when_it_was_requested(prices: pd.DataFrame):
    update = build_indicators_update(
        prices.iloc[:80], IndicatorsRequestDTO(series=["rsi"])
    )

    assert update.series.rsi is not None and len(update.series.rsi) == 1
    assert update.series.macd is None
    assert update.series.averages is None
