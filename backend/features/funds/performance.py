from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from backend.core.dto.fund import FundDistributionDTO

# Pregões da janela de desempenho da cota, contados antes de hoje
PERFORMANCE_WINDOW = 126


@dataclass(frozen=True)
class NavPoint:
    """O patrimônio por cota de um pregão fechado."""

    day: date
    nav: Decimal


def excess_return(
    points: Sequence[NavPoint],
    nav: Decimal,
    today: date,
    distributions: Sequence[FundDistributionDTO],
    cdi_factor: Callable[[date, date], Decimal],
) -> Decimal:
    """O retorno da cota na janela menos o do CDI, em fração (0,02 é 2 pontos acima do CDI).

    O retorno é o total: o patrimônio por cota de hoje mais o que a gestora pagou por cota
    de rendimento depois do primeiro ponto, sobre o patrimônio por cota desse ponto. `points`
    vem em ordem cronológica e termina no pregão anterior a `today`; o primeiro é o início da
    janela. Com menos de um pregão de histórico a diferença é zero.
    """
    if not points or points[0].nav <= 0:
        return Decimal(0)
    start = points[0]
    paid = sum(
        (
            d.paid_per_quota
            for d in distributions
            if d.paid_per_quota is not None
            and d.paid_on is not None
            and start.day < d.paid_on <= today
        ),
        Decimal(0),
    )
    fund_return = (nav + paid) / start.nav - 1
    return fund_return - (cdi_factor(start.day, today) - 1)


def cut_window(points: Sequence[NavPoint]) -> list[NavPoint]:
    """Os últimos `PERFORMANCE_WINDOW` pontos."""
    return list(points[-PERFORMANCE_WINDOW:])
