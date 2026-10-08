from __future__ import annotations

from datetime import date
from decimal import Decimal

from backend.core.utils import format_percent, is_business_day, next_business_day, ratio
from backend.core.utils.lazy_dict import LazyDict

FRIDAY = date(2020, 1, 10)
SATURDAY = date(2020, 1, 11)
SUNDAY = date(2020, 1, 12)
MONDAY = date(2020, 1, 13)


def test_business_day_is_monday_to_friday():
    """Dia útil é de segunda a sexta."""
    assert is_business_day(FRIDAY)
    assert is_business_day(MONDAY)
    assert not is_business_day(SATURDAY)
    assert not is_business_day(SUNDAY)


def test_next_business_day_skips_weekend():
    """Próximo dia útil de sexta, sábado e domingo é a segunda seguinte."""
    assert next_business_day(FRIDAY) == MONDAY
    assert next_business_day(SATURDAY) == MONDAY
    assert next_business_day(SUNDAY) == MONDAY
    assert next_business_day(MONDAY) == date(2020, 1, 14)


def test_ratio_with_zero_denominator_is_zero():
    """Fração com denominador zero ou negativo vale zero."""
    assert ratio(Decimal(1), Decimal(4)) == Decimal("0.25")
    assert ratio(Decimal(1), Decimal(0)) == 0
    assert ratio(Decimal(1), Decimal(-2)) == 0


def test_format_percent_uses_two_decimals():
    """Taxa vira percentual com duas casas."""
    assert format_percent(Decimal("0.1234")) == "12.34%"


def test_lazy_dict_loads_each_key_once():
    """Cada chave chama o loader uma única vez e depois vem do cache."""
    calls: list[str] = []

    def _loader(key: str) -> int:
        calls.append(key)
        return len(key)

    lazy = LazyDict(_loader)

    assert lazy["abc"] == 3
    assert lazy["abc"] == 3
    assert calls == ["abc"]
