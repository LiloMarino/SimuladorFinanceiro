from __future__ import annotations

from decimal import Decimal

import pytest

from backend.core.exceptions import InsufficentPositionError
from backend.features.variable_income.entities.position import Position


def _position(*buys: tuple[str, int]) -> Position:
    position = Position("ABCD")
    for price, size in buys:
        position.update_buy(Decimal(price), size)
    return position


def test_successive_buys_average_the_price():
    """Compras sucessivas recalculam o preço médio pelo custo total."""
    position = _position(("10", 10), ("13", 5))

    # (100 + 65) / 15 = 11
    assert position.size == 15
    assert position.total_cost == Decimal("165")
    assert position.avg_price == Decimal("11")


def test_partial_sell_keeps_average_price():
    """Venda parcial reduz o custo pelo preço médio e mantém o médio."""
    position = _position(("10", 10), ("13", 5))

    position.update_sell(6)

    assert position.size == 9
    assert position.avg_price == Decimal("11")
    assert position.total_cost == Decimal("99")


def test_full_sell_zeroes_position():
    """Vender tudo zera quantidade, custo e preço médio."""
    position = _position(("10", 10))

    position.update_sell(10)

    assert position.size == 0
    assert position.total_cost == 0
    assert position.avg_price == 0


def test_sell_more_than_held_is_rejected():
    """Vender acima da quantidade em carteira falha sem alterar a posição."""
    position = _position(("10", 10))

    with pytest.raises(InsufficentPositionError):
        position.update_sell(11)

    assert position.size == 10


def test_reserve_limited_to_free_quantity():
    """Reserva só usa a quantidade livre: o que já está reservado não conta."""
    position = _position(("10", 10))
    position.reserve(7)

    with pytest.raises(InsufficentPositionError):
        position.reserve(4)

    position.reserve(3)
    assert position.reserved == 10


def test_release_never_goes_negative():
    """Liberar mais do que o reservado zera a reserva."""
    position = _position(("10", 10))
    position.reserve(2)

    position.release(5)

    assert position.reserved == 0
