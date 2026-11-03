"""
A retrospectiva do ano de um jogador, montada a partir dos snapshots que o banco já
guarda.
"""

from collections import OrderedDict
from collections.abc import Sequence
from decimal import Decimal
from math import prod

from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.summaries import YearMonthDTO, YearReviewDTO
from backend.features.statistics import risk


def year_review(
    year: int,
    history: Sequence[PatrimonialHistoryDTO],
    starting_cash: Decimal,
    ibov_pct: Decimal | None,
) -> YearReviewDTO | None:
    """
    `history` traz os snapshots do ano e, quando existe, o último de antes dele, que é
    o patrimônio de partida; sem ele (o primeiro ano) a partida é o saldo inicial.
    Nula quando o ano não tem snapshot.
    """
    before = [h for h in history if h.snapshot_date.year < year]
    during = [h for h in history if h.snapshot_date.year == year]
    if not during:
        return None
    start = before[-1] if before else None
    end = during[-1]

    days = [d for d in risk.daily_returns(list(history)) if d[0].year == year]
    monthly = risk.monthly_returns(days)
    # O último snapshot de cada mês é o patrimônio com que ele fechou
    month_ends = OrderedDict((h.snapshot_date.replace(day=1), h) for h in during)
    measured = [
        YearMonthDTO(
            month=m.month,
            return_pct=m.value,
            networth_end=month_ends[m.month].total_networth,
        )
        for m in monthly
    ]
    return YearReviewDTO(
        year=year,
        networth_start=start.total_networth if start else starting_cash,
        networth_end=end.total_networth,
        return_pct=_compound([m.return_pct for m in measured]) if measured else None,
        cdi_pct=_compound([m.cdi for m in monthly]),
        ibov_pct=ibov_pct,
        contributions=end.total_contribution
        - (start.total_contribution if start else Decimal(0)),
        months=measured,
        best_month=max(measured, key=lambda m: m.return_pct, default=None),
        worst_month=min(measured, key=lambda m: m.return_pct, default=None)
        if len(measured) > 1
        else None,
    )


def _compound(rates: Sequence[Decimal]) -> Decimal:
    return prod((1 + r for r in rates), start=Decimal(1)) - 1
