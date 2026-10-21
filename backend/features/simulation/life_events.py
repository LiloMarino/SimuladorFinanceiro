"""
Regras do viver de renda, puras: os imprevistos sorteados e o juro do cheque
especial. Salário, despesa e meta ficam no `LifeBudget`.

Os imprevistos vêm de um registro de tipos: o motor, o histórico e as telas leem
`LIFE_EVENTS`, então um tipo novo é uma entrada nova na tupla.
"""

import random
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from backend.core.enum import LifeEventEffect
from backend.core.indicators import BUSINESS_DAYS_PER_YEAR
from backend.core.life_budget import MONTHS_PER_YEAR, cents
from backend.core.utils import is_business_day, next_business_day


@dataclass(frozen=True)
class LifeEventType:
    key: str
    label: str
    effect: LifeEventEffect
    # Chance relativa entre os tipos quando sai um imprevisto
    weight: int
    expense_multiple: Decimal = Decimal(0)


LIFE_EVENTS: tuple[LifeEventType, ...] = (
    LifeEventType(
        key="REPAIR",
        label="Conserto do carro",
        effect=LifeEventEffect.CASH_OUT,
        weight=3,
        expense_multiple=Decimal(1),
    ),
    LifeEventType(
        key="HEALTH",
        label="Despesa de saúde",
        effect=LifeEventEffect.CASH_OUT,
        weight=2,
        expense_multiple=Decimal(2),
    ),
    LifeEventType(
        key="LAYOFF",
        label="Demissão",
        effect=LifeEventEffect.SKIP_NEXT_SALARY,
        weight=1,
    ),
)

LIFE_EVENTS_BY_KEY = {event.key: event for event in LIFE_EVENTS}


def unexpected_on(
    seed: int,
    day: date,
    per_year: int,
    events: tuple[LifeEventType, ...] = LIFE_EVENTS,
) -> LifeEventType | None:
    """
    O imprevisto do pregão `day`, ou None. O gerador nasce da semente da partida e
    do dia: todos os jogadores recebem o mesmo, e a retomada sorteia igual.
    A chance por pregão é `per_year / 252`.
    """
    if per_year <= 0 or not events:
        return None
    rng = random.Random(f"{seed}:{day.isoformat()}")
    if rng.random() >= per_year / BUSINESS_DAYS_PER_YEAR:
        return None
    return rng.choices(events, weights=[e.weight for e in events])[0]


def layoff_in(
    seed: int,
    month: date,
    per_year: int,
    start_date: date,
    until: date | None = None,
    events: tuple[LifeEventType, ...] = LIFE_EVENTS,
) -> date | None:
    """O pregão do mês de `month` (a partir do início da partida e até `until`) em que saiu uma demissão."""
    first = month.replace(day=1)
    day = max(first, start_date)
    day = day if is_business_day(day) else next_business_day(day)
    while (day.year, day.month) == (first.year, first.month) and (
        until is None or day <= until
    ):
        event = unexpected_on(seed, day, per_year, events)
        if event is not None and event.effect is LifeEventEffect.SKIP_NEXT_SALARY:
            return day
        day = next_business_day(day)
    return None


def salary_skipped(
    seed: int,
    month: date,
    per_year: int,
    start_date: date,
    events: tuple[LifeEventType, ...] = LIFE_EVENTS,
) -> bool:
    """O salário de `month` não entra quando saiu uma demissão em algum pregão do mês anterior."""
    previous = month.replace(day=1) - timedelta(days=1)
    return layoff_in(seed, previous, per_year, start_date, events=events) is not None


def overdraft_interest(cash: Decimal, monthly_rate: Decimal) -> Decimal:
    """Juro de um pregão sobre o caixa negativo; a taxa mensal vira diária na base de 252 pregões."""
    if cash >= 0:
        return Decimal(0)
    daily = (1 + monthly_rate) ** (
        Decimal(MONTHS_PER_YEAR) / BUSINESS_DAYS_PER_YEAR
    ) - 1
    return cents(-cash * daily)
