"""Aritmética de calendário em meses e trimestres, sobre `date`."""

import calendar
from datetime import date

MONTHS_PER_QUARTER = 3


def add_months(day: date, months: int) -> date:
    """Mesmo dia `months` meses depois; mês mais curto cai no último dia dele."""
    index = day.month - 1 + months
    year, month = day.year + index // 12, index % 12 + 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def quarter_start(day: date) -> date:
    """O 1º dia do trimestre do calendário de `day`."""
    return date(
        day.year, MONTHS_PER_QUARTER * ((day.month - 1) // MONTHS_PER_QUARTER) + 1, 1
    )
