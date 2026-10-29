"""
O resumo do mês e a retrospectiva do ano de um jogador, montados a partir do que o
banco já guarda: snapshots, eventos de caixa e de renda variável e fechamentos.
"""

from collections import defaultdict
from collections.abc import Mapping, Sequence
from datetime import date
from decimal import Decimal
from math import prod

from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.summaries import (
    MonthSummaryDTO,
    PositionResultDTO,
    RankingMoveDTO,
    YearMonthDTO,
    YearReviewDTO,
)
from backend.core.enum import CashflowEventType, EquityEventType
from backend.features.statistics import risk


def month_summary(
    month: date,
    history: Sequence[PatrimonialHistoryDTO],
    starting_cash: Decimal,
    flows: Mapping[CashflowEventType, Decimal],
    positions: Sequence[PositionResultDTO],
    ibov_pct: Decimal | None,
    ranking: RankingMoveDTO | None,
) -> MonthSummaryDTO | None:
    """
    `history` traz os snapshots do mês e, quando existe, o último de antes dele, que
    é o patrimônio de partida; sem ele (o primeiro mês) a partida é o saldo inicial.
    Nulo quando o mês não tem snapshot.
    """
    before = [h for h in history if h.snapshot_date < month]
    during = [h for h in history if h.snapshot_date >= month]
    if not during:
        return None
    start = before[-1] if before else None
    end = during[-1]

    days = [d for d in risk.daily_returns(list(history)) if d[0] >= month]
    monthly = risk.monthly_returns(days)
    ranked = sorted(positions, key=lambda p: p.result, reverse=True)
    return MonthSummaryDTO(
        month=month,
        networth_start=start.total_networth if start else starting_cash,
        networth_end=end.total_networth,
        return_pct=monthly[0].value if monthly else None,
        cdi_pct=monthly[0].cdi if monthly else Decimal(0),
        ibov_pct=ibov_pct,
        best_position=ranked[0] if ranked else None,
        # Com uma posição só, ela é a melhor e não há pior
        worst_position=ranked[-1] if len(ranked) > 1 else None,
        dividends=flows.get(CashflowEventType.DIVIDEND, Decimal(0)),
        income_tax=flows.get(CashflowEventType.TAX, Decimal(0)),
        contributions=end.total_contribution
        - (start.total_contribution if start else Decimal(0)),
        ranking=ranking,
    )


def position_results(
    events: Sequence[EquityEventDTO],
    month: date,
    month_end: date,
    closes_before: Mapping[str, Decimal],
    closes_end: Mapping[str, Decimal],
    names: Mapping[str, str],
) -> list[PositionResultDTO]:
    """
    O resultado de cada ativo que o jogador teve ou negociou no mês: o valor no fim,
    menos o valor no início, menos o que comprou, mais o que vendeu. `closes_before`
    é o fechamento do último pregão antes do mês; `closes_end`, o do fim do mês.
    """
    held_before: defaultdict[str, Decimal] = defaultdict(Decimal)
    held_end: defaultdict[str, Decimal] = defaultdict(Decimal)
    bought: defaultdict[str, Decimal] = defaultdict(Decimal)
    sold: defaultdict[str, Decimal] = defaultdict(Decimal)
    for event in events:
        if event.event_date > month_end or event.event_type not in (
            EquityEventType.BUY,
            EquityEventType.SELL,
        ):
            continue
        buying = event.event_type is EquityEventType.BUY
        signed = event.quantity if buying else -event.quantity
        held_end[event.ticker] += signed
        if event.event_date < month:
            held_before[event.ticker] += signed
        else:
            (bought if buying else sold)[event.ticker] += event.quantity * event.price

    results = []
    for ticker in held_end:
        if not (held_before[ticker] > 0 or held_end[ticker] > 0 or ticker in bought):
            continue
        value_before = held_before[ticker] * closes_before.get(ticker, Decimal(0))
        value_end = held_end[ticker] * closes_end.get(ticker, Decimal(0))
        result = value_end - value_before - bought[ticker] + sold[ticker]
        capital = value_before + bought[ticker]
        results.append(
            PositionResultDTO(
                ticker=ticker,
                name=names.get(ticker, ticker),
                result=result,
                result_pct=result / capital if capital > 0 else None,
            )
        )
    return results


def ranking_move(
    position: int, players: int, previous: MonthSummaryDTO | None
) -> RankingMoveDTO:
    """Quantas posições o jogador andou desde o resumo anterior: positivo é subir."""
    before = previous.ranking if previous else None
    return RankingMoveDTO(
        position=position,
        players=players,
        change=before.position - position if before else None,
    )


def year_review(year: int, months: Sequence[MonthSummaryDTO]) -> YearReviewDTO | None:
    """A retrospectiva sai dos resumos dos meses do ano; nula sem nenhum."""
    played = [m for m in months if m.month.year == year]
    if not played:
        return None
    measured = [
        YearMonthDTO(
            month=m.month, return_pct=m.return_pct, networth_end=m.networth_end
        )
        for m in played
        if m.return_pct is not None
    ]
    ibov = [m.ibov_pct for m in played]
    return YearReviewDTO(
        year=year,
        networth_start=played[0].networth_start,
        networth_end=played[-1].networth_end,
        return_pct=_compound([m.return_pct for m in measured]) if measured else None,
        cdi_pct=_compound([m.cdi_pct for m in played]),
        ibov_pct=None
        if None in ibov
        else _compound([i for i in ibov if i is not None]),
        contributions=sum((m.contributions for m in played), Decimal(0)),
        months=measured,
        best_month=max(measured, key=lambda m: m.return_pct, default=None),
        worst_month=min(measured, key=lambda m: m.return_pct, default=None)
        if len(measured) > 1
        else None,
    )


def _compound(rates: Sequence[Decimal]) -> Decimal:
    return prod((1 + r for r in rates), start=Decimal(1)) - 1
