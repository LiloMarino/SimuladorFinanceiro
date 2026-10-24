"""
O Resumo técnico e as séries do gráfico de uma ação, montados das funções de
`indicators` com os parâmetros do jogador.

Cada indicador com lado vota compra, neutro ou venda por uma regra fixa, como no
Investing.com; a nota é (compras - vendas) ÷ indicadores com valor, de -1 a 1.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import cast

import pandas as pd

from backend.core.dto.stock_price_history import StockPriceHistoryDTO
from backend.core.dto.technical_indicators import (
    AverageSeriesDTO,
    BandsSeriesDTO,
    IndicatorParamsDTO,
    IndicatorPointDTO,
    IndicatorSeriesDTO,
    IndicatorsRequestDTO,
    MacdSeriesDTO,
    MovingAverageDTO,
    MovingAverageKind,
    ReadingGroup,
    ReadingKey,
    ReadingSignal,
    StochasticSeriesDTO,
    SummaryVerdict,
    TechnicalIndicatorsDTO,
    TechnicalReadingDTO,
    TechnicalSummaryDTO,
)
from backend.features.technical_analysis import indicators

# O OBV vota pela direção do saldo de volume nesta janela
OBV_LOOKBACK = 5
STOCHASTIC_OVERBOUGHT = 80
STOCHASTIC_OVERSOLD = 20

# Limites inferiores de cada faixa da nota, da mais forte para a mais fraca
VERDICTS: list[tuple[float, SummaryVerdict]] = [
    (0.5, "strong_buy"),
    (0.2, "buy"),
    (-0.2, "neutral"),
    (-0.5, "sell"),
]

AVERAGE_LABELS: dict[MovingAverageKind, str] = {"sma": "MMS", "ema": "MME"}


def price_frame(history: list[StockPriceHistoryDTO]) -> pd.DataFrame:
    """O histórico do gráfico como tabela OHLCV indexada pela data."""
    return pd.DataFrame(
        [[h.open, h.high, h.low, h.close, h.volume] for h in history],
        columns=["open", "high", "low", "close", "volume"],
        index=pd.DatetimeIndex([pd.Timestamp(h.price_date) for h in history]),
        dtype=float,
    )


def build_technical_indicators(
    frame: pd.DataFrame, request: IndicatorsRequestDTO
) -> TechnicalIndicatorsDTO:
    return TechnicalIndicatorsDTO(
        series=_series(frame, request),
        summary=build_summary(frame, request.params),
    )


def build_summary(
    frame: pd.DataFrame, params: IndicatorParamsDTO
) -> TechnicalSummaryDTO:
    readings = [reading(frame, params) for reading in _READINGS]
    sided = [r for r in readings if r.key != "atr"]
    counted = [r for r in sided if r.value is not None]
    buys = sum(r.signal == "buy" for r in counted)
    sells = sum(r.signal == "sell" for r in counted)
    # A nota sai quando a maioria dos indicadores com lado já tem valor
    has_majority = len(counted) * 2 > len(sided)
    score = (buys - sells) / len(counted) if has_majority else None
    return TechnicalSummaryDTO(
        date=frame.index[-1].date() if len(frame) else None,
        readings=readings,
        buys=buys,
        sells=sells,
        counted=len(counted),
        sided=len(sided),
        score=round(score, 4) if score is not None else None,
        verdict=verdict_for(score) if score is not None else None,
    )


def summary_average(
    params: IndicatorParamsDTO, kind: MovingAverageKind
) -> MovingAverageDTO:
    """A média que o resumo lê: a primeira daquele tipo no seletor, ou a padrão."""
    chosen = next((a for a in params.averages if a.kind == kind), None)
    if chosen is not None:
        return chosen
    return next(a for a in IndicatorParamsDTO().averages if a.kind == kind)


def verdict_for(score: float) -> SummaryVerdict:
    for floor, verdict in VERDICTS:
        if score >= floor:
            return verdict
    return "strong_sell"


@dataclass(frozen=True)
class _Vote:
    signal: ReadingSignal
    reason: str


def _close(frame: pd.DataFrame) -> pd.Series:
    return cast(pd.Series, frame["close"])


def _last(series: pd.Series) -> float | None:
    value = series.iloc[-1] if len(series) else math.nan
    return None if pd.isna(value) else float(value)


def _reading(
    key: ReadingKey,
    group: ReadingGroup,
    label: str,
    frame: pd.DataFrame,
    needed: int,
    value: float | None,
    vote: Callable[[float], _Vote],
    *,
    lower: float | None = None,
    upper: float | None = None,
) -> TechnicalReadingDTO:
    missing = max(0, needed - len(frame))
    if value is None:
        return TechnicalReadingDTO(
            key=key,
            group=group,
            label=label,
            value=None,
            signal="none" if key == "atr" else "neutral",
            reason=f"aparece com {needed} pregões",
            needed_sessions=needed,
            missing_sessions=max(missing, 1),
        )
    result = vote(value)
    return TechnicalReadingDTO(
        key=key,
        group=group,
        label=label,
        value=round(value, 4),
        lower=round(lower, 4) if lower is not None else None,
        upper=round(upper, 4) if upper is not None else None,
        signal=result.signal,
        reason=result.reason,
        needed_sessions=needed,
        missing_sessions=0,
    )


def _against_price(frame: pd.DataFrame) -> Callable[[float], _Vote]:
    def vote(average: float) -> _Vote:
        close = float(_close(frame).iloc[-1])
        if close > average:
            return _Vote("buy", "preço acima da média")
        if close < average:
            return _Vote("sell", "preço abaixo da média")
        return _Vote("neutral", "preço na média")

    return vote


def _average_reading(
    frame: pd.DataFrame, params: IndicatorParamsDTO, kind: MovingAverageKind
) -> TechnicalReadingDTO:
    average = summary_average(params, kind)
    close = _close(frame)
    series = (
        indicators.sma(close, average.period)
        if kind == "sma"
        else indicators.ema(close, average.period)
    )
    return _reading(
        kind,
        "price",
        f"{AVERAGE_LABELS[kind]} {average.period}",
        frame,
        average.period,
        _last(series),
        _against_price(frame),
    )


def _sma_reading(
    frame: pd.DataFrame, params: IndicatorParamsDTO
) -> TechnicalReadingDTO:
    return _average_reading(frame, params, "sma")


def _ema_reading(
    frame: pd.DataFrame, params: IndicatorParamsDTO
) -> TechnicalReadingDTO:
    return _average_reading(frame, params, "ema")


def _bollinger_reading(
    frame: pd.DataFrame, params: IndicatorParamsDTO
) -> TechnicalReadingDTO:
    bands = indicators.bollinger(
        _close(frame), params.bollinger_period, params.bollinger_deviations
    )
    lower, middle, upper = _last(bands.lower), _last(bands.middle), _last(bands.upper)

    def vote(_: float) -> _Vote:
        close = float(_close(frame).iloc[-1])
        if upper is not None and close > upper:
            return _Vote("sell", "acima da faixa: esticado para cima")
        if lower is not None and close < lower:
            return _Vote("buy", "abaixo da faixa: esticado para baixo")
        return _Vote("neutral", "dentro da faixa")

    return _reading(
        "bollinger",
        "price",
        f"Bollinger {params.bollinger_period}, {_number(params.bollinger_deviations)}",
        frame,
        params.bollinger_period,
        middle,
        vote,
        lower=lower,
        upper=upper,
    )


def _rsi_reading(
    frame: pd.DataFrame, params: IndicatorParamsDTO
) -> TechnicalReadingDTO:
    high, low = params.rsi_overbought, params.rsi_oversold

    def vote(value: float) -> _Vote:
        if value > high:
            return _Vote("sell", f"acima de {high}: sobrecomprado")
        if value < low:
            return _Vote("buy", f"abaixo de {low}: sobrevendido")
        return _Vote("neutral", f"entre {low} e {high}")

    return _reading(
        "rsi",
        "oscillator",
        f"IFR {params.rsi_period}",
        frame,
        params.rsi_period + 1,
        _last(indicators.rsi(_close(frame), params.rsi_period)),
        vote,
    )


def _macd_reading(
    frame: pd.DataFrame, params: IndicatorParamsDTO
) -> TechnicalReadingDTO:
    result = indicators.macd(
        _close(frame), params.macd_fast, params.macd_slow, params.macd_signal
    )
    line = _last(result.line)
    signal = _last(result.signal)

    def vote(value: float) -> _Vote:
        if signal is None:
            return _Vote("neutral", "sem sinal ainda")
        if value > signal:
            return _Vote("buy", "linha acima do sinal")
        if value < signal:
            return _Vote("sell", "linha abaixo do sinal")
        return _Vote("neutral", "linha no sinal")

    return _reading(
        "macd",
        "oscillator",
        f"MACD {params.macd_fast}, {params.macd_slow}, {params.macd_signal}",
        frame,
        params.macd_slow + params.macd_signal - 1,
        line if signal is not None else None,
        vote,
    )


def _stochastic_reading(
    frame: pd.DataFrame, params: IndicatorParamsDTO
) -> TechnicalReadingDTO:
    result = indicators.stochastic(frame, params.stochastic_k, params.stochastic_d)

    def vote(value: float) -> _Vote:
        if value > STOCHASTIC_OVERBOUGHT:
            return _Vote("sell", f"acima de {STOCHASTIC_OVERBOUGHT}: sobrecomprado")
        if value < STOCHASTIC_OVERSOLD:
            return _Vote("buy", f"abaixo de {STOCHASTIC_OVERSOLD}: sobrevendido")
        return _Vote(
            "neutral", f"entre {STOCHASTIC_OVERSOLD} e {STOCHASTIC_OVERBOUGHT}"
        )

    return _reading(
        "stochastic",
        "oscillator",
        f"Estocástico {params.stochastic_k}, {params.stochastic_d}",
        frame,
        params.stochastic_k,
        _last(result.k),
        vote,
    )


def _atr_reading(
    frame: pd.DataFrame, params: IndicatorParamsDTO
) -> TechnicalReadingDTO:
    return _reading(
        "atr",
        "oscillator",
        f"ATR {params.atr_period}",
        frame,
        params.atr_period,
        _last(indicators.atr(frame, params.atr_period)),
        lambda _: _Vote("none", "quanto o preço anda por dia"),
    )


def _obv_reading(frame: pd.DataFrame, _: IndicatorParamsDTO) -> TechnicalReadingDTO:
    balance = indicators.obv(frame)
    value = _last(balance) if len(balance) > OBV_LOOKBACK else None
    before = float(balance.iloc[-1 - OBV_LOOKBACK]) if value is not None else 0.0

    def vote(today: float) -> _Vote:
        if today > before:
            return _Vote("buy", f"{OBV_LOOKBACK} dias: mais volume nas altas")
        if today < before:
            return _Vote("sell", f"{OBV_LOOKBACK} dias: mais volume nas baixas")
        return _Vote("neutral", f"{OBV_LOOKBACK} dias: volume equilibrado")

    return _reading("obv", "oscillator", "OBV", frame, OBV_LOOKBACK + 1, value, vote)


_READINGS: list[Callable[[pd.DataFrame, IndicatorParamsDTO], TechnicalReadingDTO]] = [
    _sma_reading,
    _ema_reading,
    _bollinger_reading,
    _rsi_reading,
    _macd_reading,
    _stochastic_reading,
    _atr_reading,
    _obv_reading,
]


def _points(series: pd.Series) -> list[IndicatorPointDTO]:
    return [
        IndicatorPointDTO(
            date=cast(pd.Timestamp, day).date(), value=round(float(value), 4)
        )
        for day, value in series.dropna().items()
    ]


def _series(frame: pd.DataFrame, request: IndicatorsRequestDTO) -> IndicatorSeriesDTO:
    params, wanted = request.params, set(request.series)
    close = _close(frame)
    updates: dict[str, object] = {}
    if "averages" in wanted:
        updates["averages"] = [
            AverageSeriesDTO(
                kind=a.kind,
                period=a.period,
                points=_points(
                    indicators.sma(close, a.period)
                    if a.kind == "sma"
                    else indicators.ema(close, a.period)
                ),
            )
            for a in params.averages
        ]
    if "bollinger" in wanted:
        bands = indicators.bollinger(
            close, params.bollinger_period, params.bollinger_deviations
        )
        updates["bollinger"] = BandsSeriesDTO(
            upper=_points(bands.upper),
            middle=_points(bands.middle),
            lower=_points(bands.lower),
        )
    if "rsi" in wanted:
        updates["rsi"] = _points(indicators.rsi(close, params.rsi_period))
    if "macd" in wanted:
        result = indicators.macd(
            close, params.macd_fast, params.macd_slow, params.macd_signal
        )
        updates["macd"] = MacdSeriesDTO(
            line=_points(result.line),
            signal=_points(result.signal),
            histogram=_points(result.histogram),
        )
    if "stochastic" in wanted:
        result = indicators.stochastic(frame, params.stochastic_k, params.stochastic_d)
        updates["stochastic"] = StochasticSeriesDTO(
            k=_points(result.k), d=_points(result.d)
        )
    if "atr" in wanted:
        updates["atr"] = _points(indicators.atr(frame, params.atr_period))
    if "obv" in wanted:
        updates["obv"] = _points(indicators.obv(frame))
    return IndicatorSeriesDTO.model_validate(updates)


def _number(value: float) -> str:
    return f"{value:g}".replace(".", ",")
