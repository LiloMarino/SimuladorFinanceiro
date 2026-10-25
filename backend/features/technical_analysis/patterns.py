"""
Padrões de vela sobre o histórico OHLC, do mais antigo ao mais novo.

Cada padrão é uma regra fixa sobre abertura, máxima, mínima e fechamento. Nas
regras, "corpo" é a distância entre abertura e fechamento, "sombra de cima" e
"sombra de baixo" são o que passa do corpo até a máxima e a mínima, e "amplitude"
é a máxima menos a mínima da vela. A tendência anterior é o fechamento da vela
que vem antes do padrão contra a média dos 5 fechamentos até ela: abaixo da média
é queda, acima é alta.

O gráfico, o desafio da vela e o "E se ele acertou?" leem estas mesmas regras, então
o padrão marcado na tela é o padrão conferido depois.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import cast

import numpy as np
import numpy.typing as npt
import pandas as pd

from backend.core.dto.candle_patterns import (
    CandlePatternCode,
    CandlePatternDTO,
    CandlePatternsDTO,
    PatternDirection,
    PatternStatsDTO,
)

# Pregões depois do fim do padrão em que o desfecho é medido
OUTCOME_SESSIONS = 5
# Pregões que compõem a tendência anterior
TREND_SESSIONS = 5
# Corpo até esta fração da amplitude é doji
DOJI_BODY_SHARE = 0.1
# Corpo grande: pelo menos esta fração da amplitude
LARGE_BODY_SHARE = 0.5
# Nas velas dos soldados e dos corvos, o corpo ocupa quase toda a amplitude
SOLID_BODY_SHARE = 0.6

type Mask = npt.NDArray[np.bool_]


@dataclass(frozen=True)
class Pattern:
    code: CandlePatternCode
    candles: int
    direction: PatternDirection


@dataclass(frozen=True)
class Occurrence:
    code: CandlePatternCode
    start: pd.Timestamp
    end: pd.Timestamp
    # Posição da última vela do padrão na tabela
    end_pos: int


@dataclass(frozen=True)
class _Candles:
    """As colunas da tabela como vetores, com o que as regras medem de cada vela."""

    open: npt.NDArray[np.float64]
    close: npt.NDArray[np.float64]
    range: npt.NDArray[np.float64]
    body: npt.NDArray[np.float64]
    upper: npt.NDArray[np.float64]
    lower: npt.NDArray[np.float64]
    top: npt.NDArray[np.float64]
    bottom: npt.NDArray[np.float64]
    bull: Mask
    bear: Mask
    downtrend: Mask
    uptrend: Mask

    @staticmethod
    def of(frame: pd.DataFrame) -> _Candles:
        o = frame["open"].to_numpy(dtype=float)
        h = frame["high"].to_numpy(dtype=float)
        low = frame["low"].to_numpy(dtype=float)
        c = frame["close"].to_numpy(dtype=float)
        top, bottom = np.maximum(o, c), np.minimum(o, c)
        previous = frame["close"].shift(1)
        average = previous.rolling(TREND_SESSIONS).mean()
        return _Candles(
            open=o,
            close=c,
            range=h - low,
            body=np.abs(c - o),
            upper=h - top,
            lower=bottom - low,
            top=top,
            bottom=bottom,
            bull=c > o,
            bear=c < o,
            downtrend=(previous < average).to_numpy(dtype=bool),
            uptrend=(previous > average).to_numpy(dtype=bool),
        )


def _back(values: npt.NDArray[np.float64], n: int) -> npt.NDArray[np.float64]:
    """O vetor deslocado: a posição i traz a vela `n` pregões antes (NaN no começo)."""
    out = np.full_like(values, np.nan)
    out[n:] = values[: len(values) - n]
    return out


def _back_mask(mask: Mask, n: int) -> Mask:
    out = np.zeros_like(mask)
    out[n:] = mask[: len(mask) - n]
    return out


def _doji(k: _Candles) -> Mask:
    """Amplitude com algo e corpo de até 10% dela: abriu e fechou quase no mesmo preço."""
    return (k.range > 0) & (k.body <= DOJI_BODY_SHARE * k.range)


def _long_lower_shadow(k: _Candles) -> Mask:
    return (
        (k.body > DOJI_BODY_SHARE * k.range)
        & (k.lower >= 2 * k.body)
        & (k.upper <= k.body)
    )


def _long_upper_shadow(k: _Candles) -> Mask:
    return (
        (k.body > DOJI_BODY_SHARE * k.range)
        & (k.upper >= 2 * k.body)
        & (k.lower <= k.body)
    )


def _hammer(k: _Candles) -> Mask:
    """Depois de uma queda: corpo pequeno no alto e sombra de baixo de pelo menos 2 corpos."""
    return _long_lower_shadow(k) & k.downtrend


def _hanging_man(k: _Candles) -> Mask:
    """O formato do martelo depois de uma alta."""
    return _long_lower_shadow(k) & k.uptrend


def _inverted_hammer(k: _Candles) -> Mask:
    """Depois de uma queda: corpo pequeno embaixo e sombra de cima de pelo menos 2 corpos."""
    return _long_upper_shadow(k) & k.downtrend


def _shooting_star(k: _Candles) -> Mask:
    """O formato do martelo invertido depois de uma alta."""
    return _long_upper_shadow(k) & k.uptrend


def _bullish_engulfing(k: _Candles) -> Mask:
    """Vela de alta com corpo maior que cobre por inteiro o corpo da vela de baixa anterior."""
    return (
        _back_mask(k.bear, 1)
        & k.bull
        & (k.open <= _back(k.close, 1))
        & (k.close >= _back(k.open, 1))
        & (k.body > _back(k.body, 1))
    )


def _bearish_engulfing(k: _Candles) -> Mask:
    """Vela de baixa com corpo maior que cobre por inteiro o corpo da vela de alta anterior."""
    return (
        _back_mask(k.bull, 1)
        & k.bear
        & (k.open >= _back(k.close, 1))
        & (k.close <= _back(k.open, 1))
        & (k.body > _back(k.body, 1))
    )


def _first_body_middle(k: _Candles) -> npt.NDArray[np.float64]:
    """O meio do corpo da primeira vela de um padrão de três velas (a posição i traz a de i-2)."""
    return (_back(k.open, 2) + _back(k.close, 2)) / 2


def _large_body(k: _Candles, n: int) -> Mask:
    """A vela `n` pregões antes tem corpo de pelo menos metade da amplitude."""
    return _back(k.body, n) >= LARGE_BODY_SHARE * _back(k.range, n)


def _morning_star(k: _Candles) -> Mask:
    """
    Vela de baixa grande, vela pequena (corpo de até um terço do da primeira, na
    metade de baixo dela) e vela de alta que fecha acima do meio da primeira.
    """
    middle = _first_body_middle(k)
    return (
        _back_mask(k.bear, 2)
        & _large_body(k, 2)
        & (_back(k.body, 1) <= _back(k.body, 2) / 3)
        & (_back(k.top, 1) <= middle)
        & k.bull
        & (k.close > middle)
    )


def _evening_star(k: _Candles) -> Mask:
    """
    Vela de alta grande, vela pequena (corpo de até um terço do da primeira, na
    metade de cima dela) e vela de baixa que fecha abaixo do meio da primeira.
    """
    middle = _first_body_middle(k)
    return (
        _back_mask(k.bull, 2)
        & _large_body(k, 2)
        & (_back(k.body, 1) <= _back(k.body, 2) / 3)
        & (_back(k.bottom, 1) >= middle)
        & k.bear
        & (k.close < middle)
    )


def _solid(k: _Candles, n: int) -> Mask:
    """A vela `n` pregões antes tem corpo de pelo menos 60% da amplitude."""
    return _back(k.body, n) >= SOLID_BODY_SHARE * _back(k.range, n)


def _three_white_soldiers(k: _Candles) -> Mask:
    """
    Três velas de alta com corpo cheio, cada uma abrindo dentro do corpo da anterior e
    fechando mais alto que ela.
    """
    mask = np.ones(len(k.close), dtype=bool)
    for n in (2, 1, 0):
        mask &= _back_mask(k.bull, n) & _solid(k, n)
    for n in (1, 0):
        mask &= (_back(k.close, n) > _back(k.close, n + 1)) & (
            _back(k.open, n) >= _back(k.open, n + 1)
        )
        mask &= _back(k.open, n) <= _back(k.close, n + 1)
    return mask


def _three_black_crows(k: _Candles) -> Mask:
    """
    Três velas de baixa com corpo cheio, cada uma abrindo dentro do corpo da anterior e
    fechando mais baixo que ela.
    """
    mask = np.ones(len(k.close), dtype=bool)
    for n in (2, 1, 0):
        mask &= _back_mask(k.bear, n) & _solid(k, n)
    for n in (1, 0):
        mask &= (_back(k.close, n) < _back(k.close, n + 1)) & (
            _back(k.open, n) <= _back(k.open, n + 1)
        )
        mask &= _back(k.open, n) >= _back(k.close, n + 1)
    return mask


# Dos padrões de mais velas para os de menos: quando dois terminam no mesmo pregão,
# vale o que conta mais velas
_RULES: list[tuple[Pattern, Callable[[_Candles], Mask]]] = [
    (Pattern("three_white_soldiers", 3, "up"), _three_white_soldiers),
    (Pattern("three_black_crows", 3, "down"), _three_black_crows),
    (Pattern("morning_star", 3, "up"), _morning_star),
    (Pattern("evening_star", 3, "down"), _evening_star),
    (Pattern("bullish_engulfing", 2, "up"), _bullish_engulfing),
    (Pattern("bearish_engulfing", 2, "down"), _bearish_engulfing),
    (Pattern("hammer", 1, "up"), _hammer),
    (Pattern("inverted_hammer", 1, "up"), _inverted_hammer),
    (Pattern("hanging_man", 1, "down"), _hanging_man),
    (Pattern("shooting_star", 1, "down"), _shooting_star),
    (Pattern("doji", 1, "neutral"), _doji),
]

PATTERNS: dict[CandlePatternCode, Pattern] = {p.code: p for p, _ in _RULES}


def detect(frame: pd.DataFrame) -> list[Occurrence]:
    """Os padrões do histórico, do mais antigo ao mais novo, no máximo um por pregão final."""
    if len(frame) == 0:
        return []
    candles = _Candles.of(frame)
    claimed = np.zeros(len(frame), dtype=bool)
    found: list[Occurrence] = []
    for pattern, rule in _RULES:
        ends = np.flatnonzero(rule(candles) & ~claimed)
        claimed[ends] = True
        found.extend(
            Occurrence(
                code=pattern.code,
                start=cast(pd.Timestamp, frame.index[end - pattern.candles + 1]),
                end=cast(pd.Timestamp, frame.index[end]),
                end_pos=int(end),
            )
            for end in ends
            if end >= pattern.candles - 1
        )
    return sorted(found, key=lambda o: o.end_pos)


def outcome(frame: pd.DataFrame, occurrence: Occurrence) -> float | None:
    """
    Variação do fechamento do 5º pregão depois do fim do padrão, em fração (0,028 é
    +2,8%); None enquanto ainda não houve 5 pregões depois dele.
    """
    target = occurrence.end_pos + OUTCOME_SESSIONS
    if target >= len(frame):
        return None
    close = frame["close"]
    return float(close.iloc[target] / close.iloc[occurrence.end_pos] - 1)


def is_hit(direction: PatternDirection, change: float | None) -> bool | None:
    """Se o preço foi para o lado sugerido; sem desfecho, sem lado ou sem variação, nada a dizer."""
    if change is None or change == 0 or direction == "neutral":
        return None
    return change > 0 if direction == "up" else change < 0


def build_candle_patterns(frame: pd.DataFrame) -> CandlePatternsDTO:
    patterns: list[CandlePatternDTO] = []
    checked = dict.fromkeys(PATTERNS, 0)
    hits = dict.fromkeys(PATTERNS, 0)
    for occurrence in detect(frame):
        direction = PATTERNS[occurrence.code].direction
        change = outcome(frame, occurrence)
        hit = is_hit(direction, change)
        if hit is not None:
            checked[occurrence.code] += 1
            hits[occurrence.code] += hit
        patterns.append(
            CandlePatternDTO(
                code=occurrence.code,
                start=occurrence.start.date(),
                end=occurrence.end.date(),
                direction=direction,
                change_5d=round(change, 4) if change is not None else None,
                hit=hit,
            )
        )
    return CandlePatternsDTO(
        patterns=patterns,
        stats=[
            PatternStatsDTO(code=code, checked=checked[code], hits=hits[code])
            for code in PATTERNS
        ],
    )
