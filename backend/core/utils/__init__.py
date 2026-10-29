import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def required[T](value: T | None) -> T:
    """
    O valor que a regra do domínio garante presente, já sem `None` para o pyright. A
    checagem vale também no executável, que é empacotado com `optimize=2` e perde os
    `assert`.
    """
    if value is None:
        raise ValueError("Valor obrigatório ausente")
    return value


def format_percent(rate: float | Decimal) -> str:
    return f"{rate * 100:.2f}%"


def format_money(value: Decimal) -> str:
    """Real brasileiro com separadores: R$ 1.234,50."""
    return "R$ " + f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_quantity(value: Decimal) -> str:
    """Quantidade sem zeros à direita nem expoente: 35, 0,005."""
    text = format(value.normalize(), "f")
    return text.replace(".", ",")


def resource_path(relative: str) -> Path:
    """
    Resolve caminho de recurso em dev e no executável PyInstaller. Em dev é relativo à
    raiz do repositório, de onde quer que o comando rode: o diretório atual decide só
    config.toml, .env e logs (`app_files_dir`).
    """
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / relative  # pyright: ignore[reportAttributeAccessIssue]
    return PROJECT_ROOT / relative


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


def next_month_turn(d: date) -> date:
    """Primeiro dia útil do mês seguinte ao de `d`: o dia em que a partida vira de mês."""
    last_day_of_month = d.replace(day=1) + timedelta(days=32)
    last_day_of_month = last_day_of_month.replace(day=1) - timedelta(days=1)
    return next_business_day(last_day_of_month)


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


def last_day_of_month(d: date) -> date:
    """O último dia do mês de `d`."""
    return (d.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)


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
