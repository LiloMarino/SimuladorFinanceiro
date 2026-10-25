"""Resumo técnico: a leitura de cada indicador, a nota e as faixas."""

from __future__ import annotations

from typing import cast

import pandas as pd
import pytest

from backend.core.dto.technical_indicators import (
    IndicatorParamsDTO,
    IndicatorsRequestDTO,
    MovingAverageDTO,
)
from backend.features.technical_analysis.summary import (
    build_summary,
    build_technical_indicators,
    summary_average,
    verdict_for,
)
from tests.strategy_helpers import closes


def rising(days: int = 60):
    """Sobe 1% por pregão, com volume constante: a alta acelera em reais."""
    return closes([round(100 * 1.01**i, 2) for i in range(days)])


def test_a_steady_rise_reads_each_indicator_by_its_rule():
    summary = build_summary(rising(), IndicatorParamsDTO())

    signals = {r.key: (r.signal, r.reason) for r in summary.readings}
    assert signals == {
        "sma": ("buy", "preço acima da média"),
        "ema": ("buy", "preço acima da média"),
        "bollinger": ("neutral", "dentro da faixa"),
        "rsi": ("sell", "acima de 70: sobrecomprado"),
        "macd": ("buy", "linha acima do sinal"),
        "stochastic": ("sell", "acima de 80: sobrecomprado"),
        "atr": ("none", "quanto o preço anda por dia"),
        "obv": ("buy", "5 dias: mais volume nas altas"),
    }


def test_the_score_counts_buys_minus_sells_over_the_sided_indicators():
    summary = build_summary(rising(), IndicatorParamsDTO())

    # 4 compras - 2 vendas sobre 7 indicadores com lado (o ATR não entra)
    assert (summary.buys, summary.sells, summary.counted, summary.sided) == (4, 2, 7, 7)
    assert summary.score == pytest.approx(2 / 7, abs=1e-4)
    assert summary.verdict == "buy"


@pytest.mark.parametrize(
    ("score", "verdict"),
    [
        (1.0, "strong_buy"),
        (0.5, "strong_buy"),
        (0.43, "buy"),
        (0.2, "buy"),
        (0.0, "neutral"),
        (-0.2, "neutral"),
        (-0.3, "sell"),
        (-0.5, "sell"),
        (-0.6, "strong_sell"),
    ],
)
def test_the_score_falls_in_one_of_five_bands(score, verdict):
    assert verdict_for(score) == verdict


def test_with_little_history_each_indicator_says_how_many_sessions_are_missing():
    summary = build_summary(rising(9), IndicatorParamsDTO())

    sma = next(r for r in summary.readings if r.key == "sma")
    obv = next(r for r in summary.readings if r.key == "obv")
    assert (sma.value, sma.needed_sessions, sma.missing_sessions) == (None, 20, 11)
    assert obv.value is not None
    assert obv.missing_sessions == 0


def test_without_a_majority_of_indicators_the_summary_has_no_score():
    summary = build_summary(rising(9), IndicatorParamsDTO())

    assert summary.counted == 1
    assert summary.score is None
    assert summary.verdict is None


def test_edited_parameters_change_the_reading_and_the_label():
    params = IndicatorParamsDTO(rsi_period=9, rsi_overbought=95)

    rsi = next(r for r in build_summary(rising(), params).readings if r.key == "rsi")

    assert rsi.label == "IFR 9"
    assert rsi.reason == "acima de 95: sobrecomprado"


def test_the_summary_reads_the_first_average_of_each_kind_or_the_default():
    params = IndicatorParamsDTO(
        averages=[
            MovingAverageDTO(kind="sma", period=9),
            MovingAverageDTO(kind="sma", period=50),
        ]
    )

    assert summary_average(params, "sma").period == 9
    assert summary_average(params, "ema").period == 50


def test_only_the_requested_series_come_back():
    request = IndicatorsRequestDTO(series=["rsi", "averages"])

    result = build_technical_indicators(rising(), request)

    assert result.series.rsi
    assert [(a.kind, a.period) for a in result.series.averages or []] == [
        ("sma", 20),
        ("ema", 50),
    ]
    assert result.series.macd is None
    assert result.series.bollinger is None


def test_series_start_at_the_first_session_with_a_value():
    request = IndicatorsRequestDTO(series=["averages"])

    [sma, _] = build_technical_indicators(rising(), request).series.averages or []

    assert len(sma.points) == 60 - 19
    assert sma.points[0].date == cast(pd.Timestamp, rising().index[19]).date()


def test_an_empty_history_has_no_readings_with_value():
    summary = build_summary(closes([]), IndicatorParamsDTO())

    assert summary.date is None
    assert all(r.value is None for r in summary.readings)
