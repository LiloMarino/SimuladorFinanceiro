"""Cruzamento de médias: quando compra, quando vende e o que o gráfico mostra."""

from __future__ import annotations

from decimal import Decimal

import pytest

from backend.core.enum import StrategyAction
from backend.features.strategy.context import Holding
from backend.features.strategy.moving_average import MovingAverageCross
from tests.strategy_helpers import closes, context

PARAMS = {
    "short_window": 5,
    "long_window": 50,
    "cash_pct": 20,
    "tickers": ["AAA"],
}


def falling_then_rising() -> list[float]:
    """Cai por 60 pregões e sobe nos últimos: a média curta cruza a longa para cima."""
    return [100.0 - i for i in range(60)] + [40.0 + 6 * i for i in range(1, 9)]


def rising_then_falling() -> list[float]:
    return [50.0 + i for i in range(60)] + [110.0 - 6 * i for i in range(1, 9)]


def markers(prices: list[float], side: str) -> int:
    signal = MovingAverageCross().signal(closes(prices), PARAMS)
    assert signal is not None
    return [m.side for m in signal.markers].count(side)


def test_buys_with_the_configured_share_of_cash_when_the_short_average_crosses_up():
    prices = falling_then_rising()
    # O primeiro dia da série em que o cruzamento para cima acontece
    for end in range(55, len(prices) + 1):
        ctx = context(cash="10000", history={"AAA": closes(prices[:end])})
        MovingAverageCross().next(ctx, PARAMS)
        if ctx.intents:
            break
    [intent] = ctx.intents
    price = Decimal(str(prices[end - 1]))
    assert intent.action is StrategyAction.BUY
    assert intent.ticker == "AAA"
    # 20% de R$ 10.000 dividido pelo preço, arredondado para baixo
    assert intent.quantity == int(Decimal(2000) // price)
    assert "cruzou" in intent.reason


def test_sells_the_free_part_of_the_position_when_it_crosses_down():
    prices = rising_then_falling()
    sold = None
    for end in range(55, len(prices) + 1):
        ctx = context(
            history={"AAA": closes(prices[:end])},
            holdings={"AAA": Holding("AAA", Decimal(100), Decimal(30), Decimal(50))},
        )
        MovingAverageCross().next(ctx, PARAMS)
        if ctx.intents:
            sold = ctx.intents[0]
            break
    assert sold is not None
    assert sold.action is StrategyAction.SELL
    # A parte presa em ordens abertas não é vendida
    assert sold.quantity == 70


def test_no_signal_without_enough_history():
    ctx = context(history={"AAA": closes([10.0] * 20)})
    MovingAverageCross().next(ctx, PARAMS)
    assert ctx.intents == []
    assert MovingAverageCross().signal(closes([10.0] * 20), PARAMS) is None


def test_signal_marks_the_crossings_on_the_chart():
    assert markers(falling_then_rising(), "buy") >= 1
    assert markers(rising_then_falling(), "sell") >= 1


def test_each_purchase_uses_the_cash_left_by_the_previous_ones():
    prices = falling_then_rising()
    for end in range(55, len(prices) + 1):
        history = {"AAA": closes(prices[:end]), "BBB": closes(prices[:end])}
        ctx = context(cash="10000", history=history)
        MovingAverageCross().next(ctx, {**PARAMS, "tickers": ["AAA", "BBB"]})
        if ctx.intents:
            break
    first, second = ctx.intents
    price = Decimal(str(prices[end - 1]))
    assert first.quantity == int(Decimal(2000) // price)
    assert first.quantity is not None
    remaining = Decimal(10000) - price * first.quantity
    assert second.quantity == int(remaining * 20 / 100 // price)


@pytest.mark.parametrize(
    ("params", "field"),
    [
        ({**PARAMS, "short_window": 2}, "short_window"),
        ({**PARAMS, "long_window": 500}, "long_window"),
        ({**PARAMS, "short_window": 60, "long_window": 60}, "long_window"),
        ({**PARAMS, "cash_pct": 0}, "cash_pct"),
        ({**PARAMS, "tickers": []}, "tickers"),
        ({**PARAMS, "tickers": ["ZZZ"]}, "tickers"),
    ],
)
def test_validate_reports_the_field_that_is_out_of_range(params, field):
    errors = MovingAverageCross.validate(params, {"AAA"})
    assert errors[field]


def test_validate_accepts_the_defaults():
    assert MovingAverageCross.validate(PARAMS, {"AAA"}) == {}
