"""Cada indicador contra uma série curta com os valores calculados à mão."""

from __future__ import annotations

import math

import pandas as pd
import pytest

from backend.features.technical_analysis import indicators
from tests.strategy_helpers import closes


def values(series: pd.Series) -> list[float | None]:
    return [None if math.isnan(v) else round(v, 4) for v in series.tolist()]


def candles() -> pd.DataFrame:
    """Três pregões com máxima, mínima e fechamento diferentes."""
    return closes([9.0, 11.0, 10.0], highs=[10.0, 12.0, 11.0], lows=[8.0, 9.0, 7.0])


def test_sma_is_the_mean_of_the_last_period_closes():
    close = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])

    assert values(indicators.sma(close, 3)) == [None, None, 2.0, 3.0, 4.0]


def test_ema_starts_at_the_simple_mean_and_then_weights_two_over_period_plus_one():
    # Peso 2/(3+1) = 0,5: semente (2+4+6)/3 = 4; depois (4+8)/2 = 6 e (6+12)/2 = 9
    close = pd.Series([2.0, 4.0, 6.0, 8.0, 12.0])

    assert values(indicators.ema(close, 3)) == [None, None, 4.0, 6.0, 9.0]


def test_ema_without_enough_values_is_empty():
    assert values(indicators.ema(pd.Series([1.0, 2.0]), 3)) == [None, None]


def test_macd_is_short_ema_minus_long_ema_with_its_own_signal():
    # MME 2 (peso 2/3): 3, 5, 7, 10,333; MME 3 (peso 0,5): 4, 6, 9
    # Linha: 1, 1, 1,333; sinal (MME 2 da linha): semente 1, depois 1 + 0,333 x 2/3
    result = indicators.macd(pd.Series([2.0, 4.0, 6.0, 8.0, 12.0]), 2, 3, 2)

    assert values(result.line) == [None, None, 1.0, 1.0, 1.3333]
    assert values(result.signal) == [None, None, None, 1.0, 1.2222]
    assert values(result.histogram) == [None, None, None, 0.0, 0.1111]


def test_rsi_compares_the_average_gain_with_the_average_loss():
    # Variações +1, -1, +2 com peso 1/2: ganho 0,5 e 1,25; perda 0,5 e 0,25
    # IFR: 100 - 100/(1 + 1) = 50; 100 - 100/(1 + 5) = 83,33
    result = indicators.rsi(pd.Series([10.0, 11.0, 10.0, 12.0]), 2)

    assert values(result) == [None, None, 50.0, 83.3333]


def test_rsi_of_a_flat_price_is_neutral():
    assert values(indicators.rsi(pd.Series([5.0] * 4), 2))[-1] == 50.0


def test_bollinger_is_the_mean_plus_and_minus_population_deviations():
    # Média 2 e desvio populacional √(2/3) = 0,8165; ± 2 desvios
    bands = indicators.bollinger(pd.Series([1.0, 2.0, 3.0]), 3, 2)

    assert values(bands.middle)[-1] == 2.0
    assert values(bands.upper)[-1] == pytest.approx(3.633, abs=1e-3)
    assert values(bands.lower)[-1] == pytest.approx(0.367, abs=1e-3)


def test_stochastic_places_the_close_between_the_low_and_the_high():
    # Mínima 7 e máxima 12 dos 3 pregões: (10 - 7) / (12 - 7) = 60%
    result = indicators.stochastic(candles(), 3, 2)

    assert values(result.k) == [None, None, 60.0]
    assert values(result.d) == [None, None, None]


def test_stochastic_of_a_range_with_no_height_is_in_the_middle():
    result = indicators.stochastic(closes([5.0, 5.0]), 2, 1)

    assert values(result.k) == [None, 50.0]


def test_atr_takes_the_true_range_and_smooths_it_by_wilder():
    # Amplitudes verdadeiras: 2 (só máxima - mínima), 3 e 4 (|7 - 11|)
    # Semente (2 + 3)/2 = 2,5; depois 2,5 + (4 - 2,5)/2 = 3,25
    assert values(indicators.atr(candles(), 2)) == [None, 2.5, 3.25]


def test_obv_adds_the_volume_of_up_days_and_subtracts_the_down_days():
    frame = closes([10.0, 11.0, 10.0, 10.0], volumes=[100, 200, 300, 400])

    assert values(indicators.obv(frame)) == [0.0, 200.0, -100.0, -100.0]
