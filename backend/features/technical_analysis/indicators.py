"""
Indicadores técnicos sobre o histórico OHLCV, do mais antigo ao mais novo.

Cada função devolve séries alinhadas ao índice de entrada, com NaN nos pregões em
que ainda não há histórico suficiente. O gráfico, o Resumo técnico e as estratégias
leem estas mesmas funções, então o número da tela é o número da decisão.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Macd:
    line: pd.Series
    signal: pd.Series
    histogram: pd.Series


@dataclass(frozen=True)
class Bands:
    upper: pd.Series
    middle: pd.Series
    lower: pd.Series


@dataclass(frozen=True)
class Stochastic:
    k: pd.Series
    d: pd.Series


def sma(values: pd.Series, period: int = 20) -> pd.Series:
    """Média simples dos últimos `period` pregões."""
    return cast(pd.Series, values.rolling(period).mean())


def ema(values: pd.Series, period: int = 50) -> pd.Series:
    """
    Média exponencial com peso 2/(período+1), semeada pela média simples dos
    primeiros `period` valores. Os NaN do começo (de outra série) são pulados.
    """
    return _seeded_ewm(values, period, alpha=2 / (period + 1))


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Macd:
    """Linha = MME curta - MME longa; sinal = MME da linha; histograma = linha - sinal."""
    line = cast(pd.Series, ema(close, fast) - ema(close, slow))
    signal_line = ema(line, signal)
    return Macd(
        line=line,
        signal=signal_line,
        histogram=cast(pd.Series, line - signal_line),
    )


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """IFR de Wilder: média exponencial dos ganhos e das perdas com peso 1/período."""
    change = close.diff()
    alpha = 1 / period
    gain = cast(pd.Series, change.clip(lower=0))
    loss = cast(pd.Series, -change.clip(upper=0))
    avg_gain = gain.ewm(alpha=alpha, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=alpha, adjust=False, min_periods=period).mean()
    value = cast(pd.Series, 100 - 100 / (1 + avg_gain / avg_loss))
    # Sem nenhuma variação o preço não tem força para nenhum lado
    return value.where(~((avg_gain == 0) & (avg_loss == 0)), 50.0)


def bollinger(close: pd.Series, period: int = 20, deviations: float = 2) -> Bands:
    """Média simples ± `deviations` desvios-padrão populacionais da mesma janela."""
    middle = sma(close, period)
    spread = cast(pd.Series, close.rolling(period).std(ddof=0)) * deviations
    return Bands(
        upper=cast(pd.Series, middle + spread),
        middle=middle,
        lower=cast(pd.Series, middle - spread),
    )


def stochastic(
    frame: pd.DataFrame, k_period: int = 14, d_period: int = 3
) -> Stochastic:
    """
    %K: onde o fechamento ficou entre a mínima e a máxima dos últimos `k_period`
    pregões (0 = na mínima, 100 = na máxima); %D: média simples do %K.
    """
    low = cast(pd.Series, frame["low"].rolling(k_period).min())
    high = cast(pd.Series, frame["high"].rolling(k_period).max())
    span = high - low
    k = cast(pd.Series, (frame["close"] - low) / span * 100)
    # Faixa de altura zero: o fechamento está no meio dela
    k = k.where(span != 0, 50.0).where(span.notna())
    return Stochastic(k=k, d=sma(k, d_period))


def atr(frame: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Média de Wilder da amplitude verdadeira: o maior entre máxima - mínima e a
    distância de cada uma ao fechamento anterior. O primeiro pregão usa só a amplitude.
    """
    previous = frame["close"].shift(1)
    true_range = pd.concat(
        [
            frame["high"] - frame["low"],
            (frame["high"] - previous).abs(),
            (frame["low"] - previous).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return _seeded_ewm(cast(pd.Series, true_range), period, alpha=1 / period)


def obv(frame: pd.DataFrame) -> pd.Series:
    """Saldo de volume: soma o volume dos dias de alta e tira o dos de baixa, a partir de 0."""
    direction = np.sign(frame["close"].diff().fillna(0))
    return cast(pd.Series, (direction * frame["volume"]).cumsum())


def _seeded_ewm(values: pd.Series, period: int, alpha: float) -> pd.Series:
    """Média exponencial que nasce no `period`-ésimo valor válido com a média simples deles."""
    valid = values.dropna()
    if len(valid) < period:
        return pd.Series(np.nan, index=values.index, dtype=float)
    seeded = valid.copy().astype(float)
    seeded.iloc[: period - 1] = np.nan
    seeded.iloc[period - 1] = valid.iloc[:period].mean()
    smoothed = seeded.ewm(alpha=alpha, adjust=False, ignore_na=True).mean()
    return cast(pd.Series, smoothed.reindex(values.index))
