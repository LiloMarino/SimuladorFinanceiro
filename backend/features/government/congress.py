"""O calendário do Congresso: a casa vota a fila e o pedido de impeachment no último dia útil de cada mês."""

import calendar
from datetime import date, timedelta

from backend.core.utils import is_business_day


def last_business_day(year: int, month: int) -> date:
    day = date(year, month, calendar.monthrange(year, month)[1])
    while not is_business_day(day):
        day -= timedelta(days=1)
    return day


def is_vote_day(day: date) -> bool:
    return day == last_business_day(day.year, day.month)


def next_vote_date(day: date) -> date:
    """O dia de votação do mês de `day`, ou o do mês seguinte quando o deste já passou."""
    this_month = last_business_day(day.year, day.month)
    if day <= this_month:
        return this_month
    year, month = (day.year + 1, 1) if day.month == 12 else (day.year, day.month + 1)
    return last_business_day(year, month)
