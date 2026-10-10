import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path


def format_percent(rate: float | Decimal) -> str:
    return f"{rate * 100:.2f}%"


def resource_path(relative: str) -> Path:
    """Resolve caminho de recurso em dev e no executável PyInstaller."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / relative  # type: ignore
    return Path(relative).resolve()


def ratio(numerator: Decimal, denominator: Decimal) -> Decimal:
    """Fração numerator/denominator; denominador zero (ou negativo) vale 0."""
    return numerator / denominator if denominator > 0 else Decimal(0)


def is_business_day(d: date) -> bool:
    return d.weekday() < 5


def next_business_day(d: date) -> date:
    """Primeiro dia útil estritamente depois de `d`. Dia útil = segunda a sexta."""
    d += timedelta(days=1)
    while not is_business_day(d):
        d += timedelta(days=1)
    return d


def business_days_between(start: date, end: date) -> int:
    """Quantos dias úteis existem em (start, end]; zero quando end <= start."""
    if end <= start:
        return 0
    # Toda semana cheia tem 5 dias úteis; só o resto precisa ser olhado dia a dia
    weeks, rest = divmod((end - start).days, 7)
    tail_start = start + timedelta(days=weeks * 7)
    tail = sum(
        is_business_day(tail_start + timedelta(days=i)) for i in range(1, rest + 1)
    )
    return weeks * 5 + tail


def subtract_business_days(d: date, n: int) -> date:
    """Dia útil que fica `n` dias úteis antes de `d`."""
    while n > 0:
        d -= timedelta(days=1)
        if is_business_day(d):
            n -= 1
    return d


def business_days_in_month(d: date) -> int:
    """Quantos dias úteis tem o mês de `d`."""
    first = d.replace(day=1)
    next_month = (first + timedelta(days=32)).replace(day=1)
    return business_days_between(
        first - timedelta(days=1), next_month - timedelta(days=1)
    )


def subtract_months(d: date, months: int) -> date:
    """Mesmo dia `months` meses antes; num mês mais curto, o último dia dele."""
    year, month = divmod(d.year * 12 + d.month - 1 - months, 12)
    first = date(year, month + 1, 1)
    last_day = ((first + timedelta(days=32)).replace(day=1) - timedelta(days=1)).day
    return first.replace(day=min(d.day, last_day))
