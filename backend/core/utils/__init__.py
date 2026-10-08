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
