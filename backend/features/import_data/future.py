"""
Futuro gerado da Central de dados: a prévia, que gera sem gravar, e a gravação,
que troca o futuro comum pelo novo.

O gerador lê o histórico real uma vez por processo e é refeito só quando o real
muda, então cada mudança de controle na prévia custa só a geração.
"""

import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from threading import Event, Lock

import numpy as np
import pandas as pd

from backend.core import repository
from backend.core.dto.generated_future import (
    DrawdownDTO,
    FutureParamsDTO,
    FuturePreviewDTO,
    FuturePreviewRequest,
    GeneratedFutureDTO,
    LevelChangeDTO,
    PeakDTO,
    PreviewPointDTO,
    PreviewSeriesDTO,
    SeriesStartDTO,
)
from backend.core.dto.series_coverage import SeriesKind
from backend.core.enum import IndicatorSeries, MarketRegime
from backend.core.exceptions.http_exceptions import BadRequestError, ConflictError
from backend.core.repository.generated_future import GeneratedRows
from backend.core.utils import (
    business_days_between,
    next_business_day,
    subtract_months,
)
from backend.features.import_data.synthetic import (
    PRICE_COLUMNS,
    TRADING_DAYS_PER_YEAR,
    AssetHistory,
    GeneratedSeries,
    MarketHistory,
    Regime,
    SeriesGenerator,
)
from backend.features.realtime import notify
from backend.features.realtime.schemas import FutureRecordingProgressEventDTO

logger = logging.getLogger(__name__)

# Cauda real mostrada antes do gerado na prévia, em meses: vale para a série
# diária e para a mensal
PREVIEW_REAL_MONTHS = 24
IPCA_WINDOW_MONTHS = 12

_generator_lock = Lock()
_generator: tuple[tuple, SeriesGenerator] | None = None

_recording_lock = Lock()
_cancel_recording = Event()


class RecordingCancelledError(Exception):
    pass


def load_market_history() -> MarketHistory:
    """O real da série comum no formato do gerador, com o setor e o segmento de cada ativo."""
    classification = repository.stock.get_classification()
    bars: dict[str, list[tuple]] = defaultdict(list)
    for ticker, *bar in repository.generated_future.get_real_prices():
        bars[ticker].append(tuple(bar))
    assets = {}
    for ticker, rows in bars.items():
        frame = pd.DataFrame(rows, columns=["date", *PRICE_COLUMNS]).set_index("date")
        segment = classification.get(ticker)
        assets[ticker] = AssetHistory(
            frame,
            segment=segment.segment if segment else None,
            sector=segment.sector if segment else None,
        )

    values: dict[str, list[tuple[date, Decimal]]] = defaultdict(list)
    for series, day, value in repository.generated_future.get_real_indicators():
        values[series].append((day, value))
    indicators = {
        IndicatorSeries(series): pd.Series(
            [float(value) for _, value in rows], index=[day for day, _ in rows]
        )
        for series, rows in values.items()
    }
    return MarketHistory(assets, indicators)


def get_generator() -> SeriesGenerator:
    """O gerador do real de agora; sem Ibovespa na base não há o que gerar."""
    global _generator
    fingerprint = repository.generated_future.get_real_fingerprint()
    with _generator_lock:
        if _generator is None or _generator[0] != fingerprint:
            try:
                built = SeriesGenerator(load_market_history())
            except ValueError as error:
                raise BadRequestError(
                    "Falta o Ibovespa na base: baixe os indicadores antes de gerar."
                ) from error
            _generator = (fingerprint, built)
        return _generator[1]


def _generate(
    generator: SeriesGenerator, params: FutureParamsDTO, tickers: list[str] | None
) -> GeneratedSeries:
    ibov_end = generator.calendar_days[-1]
    if params.until <= ibov_end:
        raise BadRequestError(
            f"Escolha uma data depois de {ibov_end:%d/%m/%Y}, "
            "o último dado real do Ibovespa."
        )
    regime = Regime[params.start_regime.value] if params.start_regime else None
    return generator.generate(
        params.until,
        seed=params.seed,
        temperature=params.temperature,
        start_regime=regime,
        inflation_shock=params.inflation_shock,
        tickers=tickers,
    )


# ----------------------------------------------------------------------
# Prévia


@dataclass(frozen=True)
class _Line:
    """Uma série como dias e valores, sem o índice do pandas."""

    days: list[date]
    values: np.ndarray

    @classmethod
    def of(cls, data: pd.Series | pd.DataFrame | None) -> "_Line":
        if data is None:
            return cls([], np.array([]))
        days = data.index.to_numpy().astype("datetime64[D]").tolist()
        return cls(days, np.asarray(data, dtype=float).ravel())

    def recent(self, months: int) -> "_Line":
        """Os últimos `months` meses da série, contados do último dia dela."""
        if not self.days:
            return self
        since = subtract_months(self.days[-1], months)
        start = next((i for i, day in enumerate(self.days) if day > since), 0)
        return _Line(self.days[start:], self.values[start:])

    def points(self) -> list[PreviewPointDTO]:
        return [
            PreviewPointDTO(date=day, value=float(value))
            for day, value in zip(self.days, self.values, strict=True)
            if not np.isnan(value)
        ]


def _preview_series(key: str, real: _Line, generated: _Line) -> PreviewSeriesDTO:
    return PreviewSeriesDTO(
        key=key,
        real=real.recent(PREVIEW_REAL_MONTHS).points(),
        generated=generated.points(),
    )


def _annual_selic(daily: _Line) -> _Line:
    """SELIC em % ao ano a partir da taxa em % ao dia útil."""
    return _Line(
        daily.days, ((1 + daily.values / 100) ** TRADING_DAYS_PER_YEAR - 1) * 100
    )


def _ipca_12m(real: _Line, generated: _Line) -> tuple[_Line, _Line]:
    """IPCA acumulado em 12 meses, em %, no real e no gerado que o continua."""
    growth = 1 + np.concatenate([real.values, generated.values]) / 100
    accumulated = np.full(len(growth), np.nan)
    for i in range(IPCA_WINDOW_MONTHS - 1, len(growth)):
        accumulated[i] = (np.prod(growth[i - IPCA_WINDOW_MONTHS + 1 : i + 1]) - 1) * 100
    split = len(real.values)
    return (
        _Line(real.days, accumulated[:split]),
        _Line(generated.days, accumulated[split:]),
    )


def _max_drawdown(start: float, generated: _Line) -> DrawdownDTO | None:
    """A maior queda do pico ao fundo no caminho que parte do último real."""
    levels = np.concatenate([[start], generated.values])
    drawdown = levels / np.maximum.accumulate(levels) - 1
    trough = int(np.argmin(drawdown))
    if drawdown[trough] >= 0:
        return None
    peak = int(np.argmax(levels[: trough + 1]))
    # A posição 0 é o último real, que vem antes do primeiro dia gerado
    days = [generated.days[0], *generated.days]
    return DrawdownDTO(
        value=float(drawdown[trough]), peak=days[peak], trough=days[trough]
    )


def _peak(generated: _Line, real: _Line) -> PeakDTO | None:
    """O ponto mais alto do gerado, ao lado do último valor real."""
    known = real.values[~np.isnan(real.values)]
    if not len(generated.values) or np.isnan(generated.values).all() or not len(known):
        return None
    top = int(np.nanargmax(generated.values))
    return PeakDTO(
        value=float(generated.values[top]),
        on=generated.days[top],
        today=float(known[-1]),
    )


def _series_starts(
    generator: SeriesGenerator,
) -> tuple[SeriesStartDTO, SeriesStartDTO | None]:
    """O primeiro dia gerado do Ibovespa e o da série que começa mais cedo, se outra."""
    ibov = SeriesStartDTO(
        key=IndicatorSeries.IBOV.value,
        start=next_business_day(generator.calendar_days[-1]),
    )
    last_days = {
        ticker: _Line.of(asset.bars["close"]).days[-1]
        for ticker, asset in generator.history.assets.items()
    } | {
        series.value: _Line.of(values).days[-1]
        for series, values in generator.indicators.items()
        if series is not IndicatorSeries.IPCA
    }
    key = min(last_days, key=lambda k: last_days[k])
    laggard = SeriesStartDTO(key=key, start=next_business_day(last_days[key]))
    return ibov, laggard if laggard.start < ibov.start else None


def preview(request: FuturePreviewRequest) -> FuturePreviewDTO:
    generator = get_generator()
    if request.ticker and request.ticker not in generator.history.assets:
        raise BadRequestError(f"{request.ticker} não tem pregão real na base.")
    generated = _generate(
        generator, request, [request.ticker] if request.ticker else []
    )

    def real(series: IndicatorSeries) -> _Line:
        return _Line.of(generator.indicators.get(series))

    def new(series: IndicatorSeries) -> _Line:
        return _Line.of(generated.indicators.get(series))

    ibov_real, ibov = real(IndicatorSeries.IBOV), new(IndicatorSeries.IBOV)
    selic_real = _annual_selic(real(IndicatorSeries.SELIC))
    selic = _annual_selic(new(IndicatorSeries.SELIC))
    ipca_real, ipca = _ipca_12m(real(IndicatorSeries.IPCA), new(IndicatorSeries.IPCA))

    asset = None
    if request.ticker and request.ticker in generated.assets:
        asset = _preview_series(
            request.ticker,
            _Line.of(generator.history.assets[request.ticker].bars["close"]),
            _Line.of(generated.assets[request.ticker]["close"]),
        )

    ibov_start, laggard_start = _series_starts(generator)
    start_level, end_level = float(ibov_real.values[-1]), float(ibov.values[-1])
    return FuturePreviewDTO(
        current_regime=MarketRegime[generator.current_regime.name],
        ibov_start=ibov_start,
        laggard_start=laggard_start,
        trading_days=business_days_between(generator.calendar_days[-1], request.until),
        assets=len(generator.history.assets),
        indicators=len(generator.indicators),
        ibov=_preview_series(IndicatorSeries.IBOV.value, ibov_real, ibov),
        asset=asset,
        selic=_preview_series(IndicatorSeries.SELIC.value, selic_real, selic),
        ipca_12m=_preview_series(IndicatorSeries.IPCA.value, ipca_real, ipca),
        ibov_change=LevelChangeDTO(
            change=end_level / start_level - 1,
            start=start_level,
            end=end_level,
            on=ibov.days[-1],
        ),
        max_drawdown=_max_drawdown(start_level, ibov),
        selic_peak=_peak(selic, selic_real),
        ipca_peak=_peak(ipca, ipca_real),
    )


# ----------------------------------------------------------------------
# Gravação


def _rows(generated: GeneratedSeries) -> list[GeneratedRows]:
    """O futuro nas colunas das tabelas; indicador como Decimal do valor já arredondado."""
    series = []
    for indicator, values in generated.indicators.items():
        line = _Line.of(values)
        series.append(
            GeneratedRows(
                SeriesKind.INDICATOR,
                indicator.value,
                [
                    {"ref_date": day, "value": Decimal(str(value))}
                    for day, value in zip(line.days, line.values, strict=True)
                ],
            )
        )
    for ticker, bars in generated.assets.items():
        days = _Line.of(bars["close"]).days
        columns = {c: np.asarray(bars[c], dtype=float) for c in PRICE_COLUMNS}
        series.append(
            GeneratedRows(
                SeriesKind.STOCK,
                ticker,
                [
                    {
                        "price_date": day,
                        **{c: float(columns[c][i]) for c in PRICE_COLUMNS[:4]},
                        "volume": int(columns["volume"][i]),
                    }
                    for i, day in enumerate(days)
                ],
            )
        )
    return series


def _report_progress(series: str, done: int, total: int) -> None:
    if _cancel_recording.is_set():
        raise RecordingCancelledError
    notify(
        "future_recording_progress",
        FutureRecordingProgressEventDTO(
            series=series, done=done, total=total
        ).to_json(),
    )


def record(params: FutureParamsDTO) -> GeneratedFutureDTO:
    """
    Gera todas as séries e troca o futuro comum pelo novo. Cancelar ou falhar no
    meio desfaz a troca inteira: o futuro anterior, se havia, continua.
    """
    if not _recording_lock.acquire(blocking=False):
        raise ConflictError("Já há um futuro sendo gravado.")
    try:
        _cancel_recording.clear()
        generated = _generate(get_generator(), params, None)
        try:
            repository.generated_future.replace(
                params, _rows(generated), datetime.now(UTC), _report_progress
            )
        except RecordingCancelledError as error:
            raise ConflictError("Gravação cancelada: nada mudou na base.") from error
        finally:
            repository.economic.clear_cache()
        logger.info(
            "Futuro gravado até %s (semente %s).",
            f"{params.until:%d/%m/%Y}",
            params.seed,
        )
    finally:
        _recording_lock.release()

    future = repository.generated_future.get()
    if future is None:
        raise RuntimeError("O futuro gravado sumiu logo depois da gravação.")
    return future


def cancel_recording() -> None:
    """Interrompe a gravação em andamento antes da próxima série; sem gravação, nada muda."""
    if _recording_lock.locked():
        _cancel_recording.set()


def get_future() -> GeneratedFutureDTO | None:
    return repository.generated_future.get()
