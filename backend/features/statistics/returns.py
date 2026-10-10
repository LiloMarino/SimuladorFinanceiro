"""Retorno acumulado da cota e as referências do mesmo período (CDI e IBOV)."""

from datetime import date
from decimal import Decimal

from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.enum import IndicatorSeries
from backend.core.indicators import last_known_value
from backend.features.statistics.risk import (
    DAYS_PER_YEAR,
    DailyReturns,
    cdi_return,
    quota_series,
)


def cumulative_returns(
    history: list[PatrimonialHistoryDTO], days: DailyReturns
) -> DailyReturns:
    """Cota - 1 em cada dia, partindo de 0 no primeiro snapshot."""
    if not history:
        return []
    quotas = quota_series([r for _, r in days])
    return [(history[0].snapshot_date, Decimal(0))] + [
        (day, quota - 1) for (day, _), quota in zip(days, quotas, strict=True)
    ]


def cdi_cumulative(dates: list[date]) -> DailyReturns:
    """Quanto um título de 100% do CDI acumulou desde a primeira data, em cada data."""
    if not dates:
        return []
    growth = Decimal(1)
    series = [(dates[0], Decimal(0))]
    for day in dates[1:]:
        growth *= 1 + cdi_return(day)
        series.append((day, growth - 1))
    return series


def ibov_cumulative(dates: list[date]) -> DailyReturns:
    """Variação do Ibovespa desde a primeira data; vazia sem dado do índice."""
    base = last_known_value(IndicatorSeries.IBOV, dates[0]) if dates else None
    if not base:
        return []
    series = []
    for day in dates:
        level = last_known_value(IndicatorSeries.IBOV, day)
        series.append((day, level / base - 1 if level else Decimal(0)))
    return series


def annualize(cumulative: DailyReturns) -> Decimal | None:
    """Acumulado de uma série de referência composto para um ano."""
    if len(cumulative) < 2:
        return None
    growth = 1 + cumulative[-1][1]
    if growth <= 0:
        return Decimal(-1)
    return growth ** (DAYS_PER_YEAR / (len(cumulative) - 1)) - 1
