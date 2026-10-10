"""Quanto cada jogador negociou e quanto isso custou."""

import statistics
from collections import defaultdict
from decimal import Decimal
from itertools import groupby

from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.statistics_report import MonthlyVolumeDTO
from backend.core.enum import EquityEventType
from backend.features.variable_income.price_impact import PriceImpact


def traded_volume(trades: list[EquityEventDTO]) -> Decimal:
    return sum((t.quantity * t.price for t in trades), Decimal(0))


def turnover(
    trades: list[EquityEventDTO], history: list[PatrimonialHistoryDTO]
) -> Decimal | None:
    """
    Giro: volume negociado ÷ patrimônio médio. Com patrimônio médio de R$ 100 mil
    e R$ 300 mil negociados, a carteira girou 3 vezes.
    """
    if not history:
        return None
    average = statistics.mean(h.total_networth for h in history)
    return traded_volume(trades) / average if average > 0 else None


def monthly_volume(trades: list[EquityEventDTO]) -> list[MonthlyVolumeDTO]:
    months = []
    for month, group in groupby(trades, key=lambda t: t.event_date.replace(day=1)):
        totals: dict[EquityEventType, Decimal] = defaultdict(Decimal)
        for trade in group:
            totals[trade.event_type] += trade.quantity * trade.price
        months.append(
            MonthlyVolumeDTO(
                month=month,
                bought=totals[EquityEventType.BUY],
                sold=totals[EquityEventType.SELL],
            )
        )
    return months


def impact_cost(trades: list[EquityEventDTO], impact: PriceImpact) -> Decimal | None:
    """
    Executado - histórico de cada execução, com o sinal de quem paga: comprar
    acima do histórico e vender abaixo dele é custo; o contrário é ganho. O preço
    histórico é o executado ÷ o fator de impacto do dia.
    """
    if not impact.enabled:
        return None

    total = Decimal(0)
    for ticker, group in groupby(
        sorted(trades, key=lambda t: t.ticker), key=lambda t: t.ticker
    ):
        ticker_trades = list(group)
        factors = impact.factors_on(ticker, [t.event_date for t in ticker_trades])
        for trade in ticker_trades:
            historical = trade.price / Decimal(str(factors[trade.event_date]))
            sign = 1 if trade.event_type is EquityEventType.BUY else -1
            total += sign * trade.quantity * (trade.price - historical)
    return total
