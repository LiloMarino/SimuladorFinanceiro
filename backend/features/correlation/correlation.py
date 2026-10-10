"""
Correlação de Pearson entre os retornos diários de ativos, par a par. Cada par
usa só os pregões em que os dois lados têm retorno, então a amostra muda de
célula para célula.
"""

import math
import statistics
from datetime import date
from decimal import Decimal
from itertools import pairwise

from backend.core import repository
from backend.core.dto.correlation import (
    CorrelationAssetsDTO,
    CorrelationCellDTO,
    CorrelationMatrixDTO,
    CorrelationWindow,
)
from backend.core.dto.series_coverage import OriginCoverageDTO
from backend.core.enum import IndicatorSeries
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.utils import subtract_months

# Pregões em comum abaixo dos quais a correlação é ruído: ~1 mês
MIN_COMMON_DAYS = 20

WINDOW_MONTHS: dict[CorrelationWindow, int] = {"6m": 6, "1y": 12, "3y": 36, "5y": 60}

REFERENCE = IndicatorSeries.IBOV.value

type DailyReturns = dict[date, float]


def daily_returns(levels: dict[date, float]) -> DailyReturns:
    """
    Variação de cada pregão sobre o pregão anterior da própria série. Um preço
    inválido (NaN, zero) conta como dia sem pregão.
    """
    days = sorted(d for d, v in levels.items() if math.isfinite(v) and v > 0)
    return {day: levels[day] / levels[previous] - 1 for previous, day in pairwise(days)}


def pair(a: DailyReturns, b: DailyReturns) -> CorrelationCellDTO:
    common = sorted(a.keys() & b.keys())
    if len(common) < MIN_COMMON_DAYS:
        return CorrelationCellDTO(correlation=None, days=len(common))
    try:
        value = statistics.correlation([a[d] for d in common], [b[d] for d in common])
    except statistics.StatisticsError:
        # Série parada na janela: não há variação para comparar
        return CorrelationCellDTO(correlation=None, days=len(common))
    return CorrelationCellDTO(correlation=Decimal(f"{value:.4f}"), days=len(common))


def correlation_matrix(
    series: dict[str, DailyReturns],
) -> list[list[CorrelationCellDTO]]:
    labels = list(series)
    return [[pair(series[row], series[column]) for column in labels] for row in labels]


def resolve_end(end: date | None) -> date:
    """Na partida, a janela termina na data da simulação, para não revelar o futuro."""
    if SimulationManager.has_active_simulation():
        return SimulationManager.get_active_simulation().get_current_date()
    if end is not None:
        return end
    return _last_price_date(repository.stock.get_coverage()) or date.today()


def _last_price_date(coverage: list[OriginCoverageDTO]) -> date | None:
    return max((c.end for c in coverage), default=None)


def _reference_levels(start: date, end: date) -> dict[date, float]:
    history = repository.economic.get_history(IndicatorSeries.IBOV)
    return {
        day: float(history.values[day]) for day in history.dates if start <= day <= end
    }


def build_correlation_matrix(
    tickers: list[str], window: CorrelationWindow, end: date | None
) -> CorrelationMatrixDTO:
    end = resolve_end(end)
    start = subtract_months(end, WINDOW_MONTHS[window])
    closes = repository.stock.get_closes_between(tickers, start, end)
    series = {ticker: daily_returns(closes[ticker]) for ticker in tickers}
    series[REFERENCE] = daily_returns(_reference_levels(start, end))
    return CorrelationMatrixDTO(
        labels=list(series),
        rows=correlation_matrix(series),
        start=start,
        end=end,
        min_days=MIN_COMMON_DAYS,
    )


def build_correlation_assets() -> CorrelationAssetsDTO:
    coverage = repository.stock.get_coverage()
    if SimulationManager.has_active_simulation():
        today = SimulationManager.get_active_simulation().get_current_date()
        tickers = {c.key for c in coverage if c.start <= today}
        return CorrelationAssetsDTO(
            tickers=sorted(tickers), last_date=today, end_fixed=True
        )
    return CorrelationAssetsDTO(
        tickers=sorted({c.key for c in coverage}),
        last_date=_last_price_date(coverage),
        end_fixed=False,
    )
