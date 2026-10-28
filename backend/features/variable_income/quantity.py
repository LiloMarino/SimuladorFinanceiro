"""Quantidade negociável de um ativo: inteira, ou fracionária na cripto."""

from decimal import ROUND_DOWN, Decimal

QUANTITY_STEP = Decimal("1E-8")


def affordable_quantity(
    money: Decimal, price: Decimal | None, *, fractional: bool
) -> Decimal:
    """O que o dinheiro paga ao preço: inteiro, ou até oito casas na cripto."""
    if not price:
        return Decimal(0)
    if fractional:
        return (money / price).quantize(QUANTITY_STEP, rounding=ROUND_DOWN)
    return money // price
