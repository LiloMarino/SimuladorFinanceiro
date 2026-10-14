"""Quanto cada jogador negociou e quanto isso custou."""

import statistics
from collections import defaultdict
from datetime import date
from decimal import Decimal
from itertools import groupby

from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.statistics_report import MonthlyVolumeDTO, TurnoverStyle
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


# Giro a partir do qual cada estilo vale: abaixo de 0,5 a carteira quase não mexe
TURNOVER_STYLES: list[tuple[Decimal, TurnoverStyle]] = [
    (Decimal(4), "Muito ativo"),
    (Decimal(2), "Ativo"),
    (Decimal("0.5"), "Moderado"),
    (Decimal(0), "Segura"),
]


def turnover_style(value: Decimal | None) -> TurnoverStyle | None:
    """O giro em palavras: não é bom nem ruim, mostra o estilo."""
    if value is None:
        return None
    return next(style for floor, style in TURNOVER_STYLES if value >= floor)


def monthly_volume(
    trades: list[EquityEventDTO], history: list[PatrimonialHistoryDTO]
) -> list[MonthlyVolumeDTO]:
    """Um item por mês da partida, com zero nos meses em que o jogador só segurou."""
    totals: dict[date, dict[EquityEventType, Decimal]] = defaultdict(
        lambda: defaultdict(Decimal)
    )
    counts: dict[date, dict[EquityEventType, int]] = defaultdict(
        lambda: defaultdict(int)
    )
    for trade in trades:
        month = trade.event_date.replace(day=1)
        totals[month][trade.event_type] += trade.quantity * trade.price
        counts[month][trade.event_type] += 1

    months = {h.snapshot_date.replace(day=1) for h in history} | totals.keys()
    return [
        MonthlyVolumeDTO(
            month=month,
            bought=totals[month][EquityEventType.BUY],
            sold=totals[month][EquityEventType.SELL],
            buy_count=counts[month][EquityEventType.BUY],
            sell_count=counts[month][EquityEventType.SELL],
        )
        for month in sorted(months)
    ]


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
