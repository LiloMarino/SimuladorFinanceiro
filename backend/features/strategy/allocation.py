"""
Divisão de dinheiro entre itens com meta: o rebalanceamento por meta e a divisão de um aporte.

A divisão é uma só conta para os dois modos. Cada item termina em
`max(piso, meta * (P + A) - L)`, onde P é o patrimônio de hoje, A o aporte e L o
nível que faz os itens somarem P + A. Subir L tira dinheiro de todos os itens acima
do piso por igual, em reais: é o "enche primeiro o mais abaixo da meta até empatar
com o segundo". Só com aporte, o piso é o valor de hoje e nada é vendido; com venda,
o piso é a parte que a estratégia não mexe.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

from backend.features.variable_income.quantity import affordable_quantity

ZERO = Decimal(0)


@dataclass(frozen=True, slots=True, kw_only=True)
class Item:
    """`target` é a fração da meta; `floor` é o valor abaixo do qual o item não desce."""

    value: Decimal
    target: Decimal
    floor: Decimal


def distribute(items: Sequence[Item], amount: Decimal) -> list[Decimal]:
    """
    O valor de cada item depois de pôr `amount` na carteira, o mais perto possível
    da meta sem descer de nenhum piso. A soma dos pisos não passa do patrimônio de
    hoje, então sempre existe a divisão.
    """
    total = sum((item.value for item in items), ZERO) + amount
    goals = [item.target * total for item in items]
    # O nível em que cada item encosta no piso, do mais alto para o mais baixo
    order = sorted(
        range(len(items)),
        key=lambda index: goals[index] - items[index].floor,
        reverse=True,
    )
    floors = sum((item.floor for item in items), ZERO)
    active_goals = ZERO
    level = ZERO
    for count, index in enumerate(order, start=1):
        active_goals += goals[index]
        floors -= items[index].floor
        level = (active_goals + floors - total) / count
        following = order[count] if count < len(order) else None
        next_break = (
            goals[following] - items[following].floor if following is not None else None
        )
        if next_break is None or level >= next_break:
            break
    return [
        max(item.floor, goal - level) for item, goal in zip(items, goals, strict=True)
    ]


def whole_shares(move: Decimal, price: Decimal, *, fractional: bool = False) -> Decimal:
    """Cotas de uma movimentação em reais, arredondadas para mexer menos: inteiras, ou até oito casas na cripto."""
    if price <= 0:
        return ZERO
    return affordable_quantity(abs(move), price, fractional=fractional)
