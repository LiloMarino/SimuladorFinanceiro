import statistics
from datetime import date
from decimal import Decimal
from itertools import pairwise

from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.player_history import RiskMetricsDTO
from backend.core.enum import IndicatorSeries
from backend.core.indicators import BUSINESS_DAYS_PER_YEAR, index_daily_rate
from backend.core.utils import subtract_business_days

DAYS_PER_YEAR = Decimal(BUSINESS_DAYS_PER_YEAR)


def build_risk_metrics(history: list[PatrimonialHistoryDTO]) -> RiskMetricsDTO:
    """
    Métricas de risco sobre os snapshots diários. Cada snapshot é um dia útil, então
    anualizar é multiplicar por 252 (retorno) ou por √252 (volatilidade).
    """
    days = daily_returns(history)
    returns = [r for _, r in days]
    volatility = annual_volatility(returns)
    return RiskMetricsDTO(
        max_drawdown=max_drawdown(returns),
        annual_volatility=volatility,
        sharpe_ratio=sharpe_ratio(days, volatility),
    )


def daily_returns(history: list[PatrimonialHistoryDTO]) -> list[tuple[date, Decimal]]:
    """
    Rendimento de cada dia sobre o patrimônio da véspera, com o aporte do dia
    descontado: o salário que entrou é capital, não rendimento.
    """
    days = []
    for prev, curr in pairwise(history):
        if prev.total_networth <= 0:
            continue
        contribution = curr.total_contribution - prev.total_contribution
        gain = curr.total_networth - contribution - prev.total_networth
        days.append((curr.snapshot_date, gain / prev.total_networth))
    return days


def max_drawdown(returns: list[Decimal]) -> Decimal | None:
    """
    Maior queda a partir de um pico, medida numa cota que só os rendimentos movem
    (como a cota de um fundo): o aporte não disfarça a queda.
    """
    if not returns:
        return None

    quota = peak = Decimal(1)
    worst = Decimal(0)
    for daily in returns:
        quota *= 1 + daily
        peak = max(peak, quota)
        worst = max(worst, (peak - quota) / peak)
    return worst


def annual_volatility(returns: list[Decimal]) -> Decimal | None:
    """Desvio-padrão amostral dos retornos diários x √252."""
    if len(returns) < 2:
        return None
    return statistics.stdev(returns) * DAYS_PER_YEAR.sqrt()


def sharpe_ratio(
    days: list[tuple[date, Decimal]], volatility: Decimal | None
) -> Decimal | None:
    """
    (retorno anual - CDI anual) ÷ volatilidade anual, com os anuais como a média
    diária x 252. O CDI de cada dia é o que um título de 100% do CDI rendeu
    entre o snapshot anterior e ele: a taxa do dia útil anterior.
    """
    if not volatility:
        return None

    excess = statistics.mean(r - _cdi_return(day) for day, r in days)
    return excess * DAYS_PER_YEAR / volatility


def _cdi_return(day: date) -> Decimal:
    rate = index_daily_rate(IndicatorSeries.CDI, subtract_business_days(day, 1))
    return rate if rate is not None else Decimal(0)
