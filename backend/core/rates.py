"""
Juros compostos, em Decimal.

Uma taxa é a fração que rende no período (0,12 = 12%) e `periods` conta períodos,
inteiros ou fracionários (meio período = Decimal("0.5")). O percentual é o valor
como o Banco Central publica, e `from_percent` o leva para fração.
"""

from decimal import Decimal
from math import prod
from typing import NewType

# Valor como o BCB publica: 0,0551 = 0,0551%, e não a fração 0,0551
Percent = NewType("Percent", Decimal)


def from_percent(value: Percent) -> Decimal:
    """A fração de um percentual: 0,0551 (%) vira 0,000551."""
    return value / 100


def compound(rate: Decimal, periods: Decimal | int) -> Decimal:
    """O que `rate` rende em `periods` períodos: (1 + rate)^periods - 1."""
    return (1 + rate) ** periods - 1


def period_rate(rate: Decimal, periods: Decimal | int) -> Decimal:
    """A taxa de um período que, composta por `periods` períodos, rende `rate`: (1 + rate)^(1/periods) - 1."""
    return compound(rate, Decimal(1) / periods)


def compose(*rates: Decimal) -> Decimal:
    """O que várias taxas rendem uma depois da outra: (1 + r1)(1 + r2)... - 1."""
    return prod((1 + rate for rate in rates), start=Decimal(1)) - 1
