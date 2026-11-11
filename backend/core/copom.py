"""O calendário das reuniões do Copom e o passo em que a SELIC anda."""

from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from functools import cache

from backend.core.utils import is_business_day, next_business_day

# O Copom se reúne 8 vezes por ano, a cada 45 dias; a reunião cai no dia útil seguinte
MEETINGS_PER_YEAR = 8
MEETING_SPACING_DAYS = 45
# A SELIC anda em passos de 0,25 ponto
SELIC_STEP = Decimal("0.0025")


@cache
def meeting_days(year: int) -> tuple[date, ...]:
    """As reuniões do ano: os dias 45, 90, …, 360, no dia útil seguinte quando caem no fim de semana."""
    first = date(year, 1, 1)
    days = (
        first + timedelta(days=MEETING_SPACING_DAYS * k - 1)
        for k in range(1, MEETINGS_PER_YEAR + 1)
    )
    return tuple(d if is_business_day(d) else next_business_day(d) for d in days)


def next_meeting(day: date) -> date:
    """A primeira reunião em `day` ou depois."""
    for year in (day.year, day.year + 1):
        for meeting in meeting_days(year):
            if meeting >= day:
                return meeting
    raise AssertionError("o ano seguinte sempre tem reunião")


def is_meeting_day(day: date) -> bool:
    return day in meeting_days(day.year)


def to_step(selic: Decimal) -> Decimal:
    """A taxa no passo de 0,25 ponto mais próximo."""
    return (selic / SELIC_STEP).quantize(Decimal(1), ROUND_HALF_UP) * SELIC_STEP
