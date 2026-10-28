"""Comprar e segurar: o caixa vira cotas do ativo (inteiras, ou em fração na cripto) e nada é vendido."""

from __future__ import annotations

from decimal import Decimal

from backend.core.dto.strategy import StrategyParamValue
from backend.core.enum import StrategyAction
from backend.features.strategy.buy_and_hold import BuyAndHold
from tests.strategy_helpers import closes, context

PARAMS: dict[str, StrategyParamValue] = {"asset": "AAA"}


def test_puts_the_idle_cash_in_whole_shares_of_the_asset():
    ctx = context(cash="1050", history={"AAA": closes([100.0, 100.0, 30.0])})

    BuyAndHold().next(ctx, PARAMS)

    [intent] = ctx.intents
    assert intent.action is StrategyAction.BUY
    assert intent.ticker == "AAA"
    # R$ 1.050 a R$ 30: 35 cotas, arredondando para baixo
    assert intent.quantity == 35


def test_crypto_takes_the_cash_in_eight_decimal_places():
    ctx = context(
        cash="1050",
        history={"AAA": closes([100.0, 100.0, 30000.0])},
        fractional=frozenset({"AAA"}),
    )

    BuyAndHold().next(ctx, PARAMS)

    [intent] = ctx.intents
    # R$ 1.050 a R$ 30.000: 0,035 unidade, sem exigir uma unidade inteira
    assert intent.quantity == Decimal("0.035")


def test_never_sells_even_when_the_price_falls():
    ctx = context(cash="0", history={"AAA": closes([100.0, 10.0])})
    BuyAndHold().next(ctx, PARAMS)
    assert ctx.intents == []


def test_does_nothing_when_the_cash_does_not_buy_a_share():
    ctx = context(cash="50", history={"AAA": closes([100.0])})
    BuyAndHold().next(ctx, PARAMS)
    assert ctx.intents == []


def test_does_nothing_without_a_quote_for_the_asset():
    ctx = context(history={"BBB": closes([10.0])})
    BuyAndHold().next(ctx, PARAMS)
    assert ctx.intents == []


def test_the_signal_is_the_price_line_of_the_asset():
    signal = BuyAndHold().signal(closes([10.0, 11.0, 12.0]), PARAMS)

    assert signal is not None
    [price] = signal.lines
    assert price.key == "price"
    assert [point.value for point in price.points] == [10.0, 11.0, 12.0]
    assert signal.markers == []


def test_validate_requires_a_known_asset():
    assert BuyAndHold.validate(PARAMS, {"AAA"}) == {}
    assert BuyAndHold.validate({"asset": "ZZZ"}, {"AAA"})["asset"]
    assert BuyAndHold.validate({"asset": ["AAA"]}, {"AAA"})["asset"]
