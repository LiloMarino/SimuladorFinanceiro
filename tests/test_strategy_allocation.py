"""A divisão do dinheiro entre itens com meta e piso."""

from __future__ import annotations

from decimal import Decimal

from backend.features.strategy.allocation import Item, distribute, whole_shares


def item(value: str, target: str, floor: str | None = None) -> Item:
    return Item(
        value=Decimal(value),
        target=Decimal(target),
        floor=Decimal(value if floor is None else floor),
    )


def test_the_contribution_fills_first_the_items_furthest_below_the_target():
    # Meta 40/30/30, hoje 600/200/200 e aporte de R$ 300: o primeiro já passou da meta
    items = [item("600", "0.4"), item("200", "0.3"), item("200", "0.3")]

    assert distribute(items, Decimal(300)) == [600, 350, 350]


def test_with_enough_money_every_item_reaches_its_target():
    items = [item("600", "0.4"), item("200", "0.3"), item("200", "0.3")]

    # Patrimônio de 1.000 + 500 de aporte: metas de 600, 450 e 450
    assert distribute(items, Decimal(500)) == [600, 450, 450]
    assert distribute(items, Decimal(1000)) == [800, 600, 600]


def test_selling_brings_the_items_back_to_the_target():
    items = [
        item("700", "0.6", floor="0"),
        item("300", "0.4", floor="0"),
    ]

    assert distribute(items, Decimal(0)) == [600, 400]


def test_an_item_never_goes_below_its_floor():
    # O primeiro tem 800 e meta de 600, mas 700 estão presos
    items = [
        item("800", "0.6", floor="700"),
        item("200", "0.4", floor="0"),
    ]

    assert distribute(items, Decimal(0)) == [700, 300]


def test_whole_shares_round_toward_moving_less():
    assert whole_shares(Decimal("1050"), Decimal(30)) == 35
    assert whole_shares(Decimal("-1050"), Decimal(30)) == 35
    assert whole_shares(Decimal("29.99"), Decimal(30)) == 0
    assert whole_shares(Decimal(100), Decimal(0)) == 0
