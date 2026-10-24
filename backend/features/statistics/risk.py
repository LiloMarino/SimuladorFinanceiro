"""
Retornos e risco sobre os snapshots diários. Cada snapshot é um dia útil, então
anualizar é multiplicar por 252 (retorno) ou por √252 (volatilidade).
"""

import statistics
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from itertools import groupby, pairwise

from backend.core import repository
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.enum import IndicatorSeries
from backend.core.indicators import BUSINESS_DAYS_PER_YEAR, index_daily_rate
from backend.core.repository.economic import IndicatorHistory
from backend.core.utils import subtract_business_days

DAYS_PER_YEAR = Decimal(BUSINESS_DAYS_PER_YEAR)

# Pregões da volatilidade em janela móvel: ~3 meses
ROLLING_WINDOW = 63

type DailyReturns = list[tuple[date, Decimal]]


@dataclass(frozen=True)
class MonthlyReturn:
    month: date
    value: Decimal
    cdi: Decimal


def daily_returns(history: list[PatrimonialHistoryDTO]) -> DailyReturns:
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


def quota_series(returns: list[Decimal]) -> list[Decimal]:
    """
    Cota que só os rendimentos movem (como a cota de um fundo), partindo de 1:
    o aporte não disfarça queda nem conta como ganho.
    """
    quotas = []
    quota = Decimal(1)
    for daily in returns:
        quota *= 1 + daily
        quotas.append(quota)
    return quotas


def drawdown_series(days: DailyReturns) -> DailyReturns:
    """Quanto a cota está abaixo do maior valor já alcançado, dia a dia."""
    peak = Decimal(1)
    series = []
    for (day, _), quota in zip(days, quota_series([r for _, r in days]), strict=True):
        peak = max(peak, quota)
        series.append((day, (peak - quota) / peak))
    return series


def max_drawdown(days: DailyReturns) -> Decimal | None:
    """Maior queda a partir de um pico, medida na cota."""
    drawdowns = [d for _, d in drawdown_series(days)]
    return max(drawdowns, default=None)


def time_underwater(days: DailyReturns) -> int | None:
    """Maior sequência de pregões com a cota abaixo do pico anterior."""
    if not days:
        return None
    longest = current = 0
    for _, drawdown in drawdown_series(days):
        current = current + 1 if drawdown > 0 else 0
        longest = max(longest, current)
    return longest


def annual_volatility(returns: list[Decimal]) -> Decimal | None:
    """Desvio-padrão amostral dos retornos diários x √252."""
    if len(returns) < 2:
        return None
    return statistics.stdev(returns) * DAYS_PER_YEAR.sqrt()


def rolling_volatility(
    days: DailyReturns, window: int = ROLLING_WINDOW
) -> DailyReturns:
    """Volatilidade anual dos últimos `window` pregões, a partir do pregão `window`."""
    returns = [r for _, r in days]
    if len(returns) < window:
        return []

    # Janela deslizante: a soma e a soma dos quadrados andam um pregão por vez,
    # então cada ponto custa O(1) e o desvio sai de (Σx² - (Σx)²/n) / (n - 1).
    total = sum(returns[:window], Decimal(0))
    squares = sum((r * r for r in returns[:window]), Decimal(0))
    annualizer = DAYS_PER_YEAR.sqrt()
    series = []
    for end in range(window, len(returns) + 1):
        if end > window:
            entering, leaving = returns[end - 1], returns[end - 1 - window]
            total += entering - leaving
            squares += entering * entering - leaving * leaving
        variance = max((squares - total * total / window) / (window - 1), Decimal(0))
        series.append((days[end - 1][0], variance.sqrt() * annualizer))
    return series


def annual_return(days: DailyReturns) -> Decimal | None:
    """Retorno da cota composto para um ano: cota_final^(252/n) - 1."""
    if not days:
        return None
    quota = quota_series([r for _, r in days])[-1]
    if quota <= 0:
        return Decimal(-1)
    return quota ** (DAYS_PER_YEAR / len(days)) - 1


# As taxas já calculadas valem para a série em memória a que pertencem: quando o
# repositório recarrega o CDI, a série é outra e a tabela recomeça vazia.
_cdi_memo: tuple[IndicatorHistory | None, dict[date, Decimal]] = (None, {})


def cdi_return(day: date) -> Decimal:
    """
    O que um título de 100% do CDI rendeu entre o snapshot anterior e `day`: a
    taxa do dia útil anterior.
    """
    global _cdi_memo
    history = repository.economic.get_history(IndicatorSeries.CDI)
    if _cdi_memo[0] is not history:
        _cdi_memo = (history, {})
    rates = _cdi_memo[1]
    rate = rates.get(day)
    if rate is None:
        daily = index_daily_rate(IndicatorSeries.CDI, subtract_business_days(day, 1))
        rate = rates[day] = daily if daily is not None else Decimal(0)
    return rate


def sharpe_ratio(days: DailyReturns, volatility: Decimal | None) -> Decimal | None:
    """
    (retorno anual - CDI anual) ÷ volatilidade anual, com os anuais como a média
    diária x 252.
    """
    if not volatility:
        return None

    excess = statistics.mean(r - cdi_return(day) for day, r in days)
    return excess * DAYS_PER_YEAR / volatility


def sortino_ratio(days: DailyReturns) -> Decimal | None:
    """
    Como o Sharpe, mas o risco é só a oscilação para baixo do CDI: o desvio
    calculado apenas com os dias que renderam menos que o CDI (os outros contam zero).
    """
    if len(days) < 2:
        return None

    excess = [r - cdi_return(day) for day, r in days]
    downside = (
        sum((min(e, Decimal(0)) ** 2 for e in excess), Decimal(0)) / len(excess)
    ).sqrt() * DAYS_PER_YEAR.sqrt()
    if not downside:
        return None
    return statistics.mean(excess) * DAYS_PER_YEAR / downside


def monthly_returns(days: DailyReturns) -> list[MonthlyReturn]:
    """Retornos diários e CDI compostos por mês civil, um item por mês da amostra."""
    months = []
    for month, group in groupby(days, key=lambda d: d[0].replace(day=1)):
        value = cdi = Decimal(1)
        for day, daily in group:
            value *= 1 + daily
            cdi *= 1 + cdi_return(day)
        months.append(MonthlyReturn(month=month, value=value - 1, cdi=cdi - 1))
    return months
