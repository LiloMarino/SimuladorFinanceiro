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
    CorrelationAssetDTO,
    CorrelationAssetsDTO,
    CorrelationCellDTO,
    CorrelationHighlightsDTO,
    CorrelationMatrixDTO,
    CorrelationPairDTO,
    CorrelationWindow,
    PortfolioCorrelationDTO,
)
from backend.core.dto.series_coverage import OriginCoverageDTO
from backend.core.enum import IndicatorSeries
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.utils import subtract_months

# Pregões em comum abaixo dos quais a correlação é ruído: ~3 meses
MIN_COMMON_DAYS = 63

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
        return CorrelationCellDTO(
            correlation=None, days=len(common), reason="insufficient_days"
        )
    try:
        value = statistics.correlation([a[d] for d in common], [b[d] for d in common])
    except statistics.StatisticsError:
        # Série parada na janela: não há variação para comparar
        return CorrelationCellDTO(
            correlation=None, days=len(common), reason="constant_series"
        )
    return CorrelationCellDTO(correlation=Decimal(f"{value:.4f}"), days=len(common))


def correlation_matrix(
    series: dict[str, DailyReturns],
) -> list[list[CorrelationCellDTO]]:
    labels = list(series)
    return [[pair(series[row], series[column]) for column in labels] for row in labels]


def highlights(
    labels: list[str], rows: list[list[CorrelationCellDTO]], held: set[str]
) -> CorrelationHighlightsDTO:
    """Os pares que se destacam entre os ativos escolhidos, e a média entre os da carteira."""
    pairs = [
        CorrelationPairDTO(first=first, second=second, correlation=correlation)
        for i, first in enumerate(labels)
        for j, second in enumerate(labels)
        if i < j
        and REFERENCE not in (first, second)
        and (correlation := rows[i][j].correlation) is not None
    ]
    owned = [p for p in pairs if p.first in held and p.second in held]
    portfolio = None
    if owned:
        average = statistics.fmean(float(p.correlation) for p in owned)
        portfolio = PortfolioCorrelationDTO(
            tickers=[t for t in labels if t in held],
            average=Decimal(f"{average:.4f}"),
        )
    return CorrelationHighlightsDTO(
        most_similar=max(pairs, key=lambda p: p.correlation, default=None),
        best_diversifier=min(pairs, key=lambda p: p.correlation, default=None),
        portfolio=portfolio,
    )


def resolve_end(end: date | None) -> date:
    """Na partida, a janela termina na data da simulação, para não revelar o futuro."""
    if SimulationManager.has_active_simulation():
        return SimulationManager.get_active_simulation().get_current_date()
    if end is not None:
        return end
    return _last_price_date(repository.stock.get_coverage()) or date.today()  # noqa: DTZ011


def _last_price_date(coverage: list[OriginCoverageDTO]) -> date | None:
    return max((c.end for c in coverage), default=None)


def _reference_levels(start: date, end: date) -> dict[date, float]:
    history = repository.economic.get_history(IndicatorSeries.IBOV)
    return {
        day: float(history.values[day]) for day in history.dates if start <= day <= end
    }


def build_correlation_matrix(
    tickers: list[str],
    window: CorrelationWindow,
    end: date | None,
    held: set[str] | None = None,
) -> CorrelationMatrixDTO:
    end = resolve_end(end)
    start = subtract_months(end, WINDOW_MONTHS[window])
    closes = repository.stock.get_closes_between(tickers, start, end)
    series = {ticker: daily_returns(closes[ticker]) for ticker in tickers}
    series[REFERENCE] = daily_returns(_reference_levels(start, end))
    labels = list(series)
    rows = correlation_matrix(series)
    return CorrelationMatrixDTO(
        labels=labels,
        rows=rows,
        start=start,
        end=end,
        min_days=MIN_COMMON_DAYS,
        highlights=highlights(labels, rows, held or set()),
    )


def build_correlation_assets() -> CorrelationAssetsDTO:
    coverage = repository.stock.get_coverage()
    classification = repository.stock.get_classification()

    def assets(tickers: set[str]) -> list[CorrelationAssetDTO]:
        return [
            CorrelationAssetDTO(
                ticker=t,
                sector=c.sector if (c := classification.get(t)) else None,
            )
            for t in sorted(tickers)
        ]

    if SimulationManager.has_active_simulation():
        today = SimulationManager.get_active_simulation().get_current_date()
        tickers = {c.key for c in coverage if c.start <= today}
        return CorrelationAssetsDTO(
            assets=assets(tickers), last_date=today, end_fixed=True
        )
    return CorrelationAssetsDTO(
        assets=assets({c.key for c in coverage}),
        last_date=_last_price_date(coverage),
        end_fixed=False,
    )
