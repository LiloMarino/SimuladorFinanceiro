"""IFR: compra ao cruzar para baixo do nível de compra, vende ao cruzar para cima do de venda."""

from __future__ import annotations

from decimal import Decimal

import pytest

from backend.core.enum import SignalLineStyle, SignalPane, StrategyAction
from backend.features.strategy.context import Holding
from backend.features.strategy.rsi import RelativeStrength
from tests.strategy_helpers import closes, first_day_with_intents

PARAMS = {
    "period": 5,
    "buy_below": 30,
    "sell_above": 70,
    "cash_pct": 20,
    "tickers": ["AAA"],
}


def rising_then_falling() -> list[float]:
    """Sobe por 40 pregões (IFR perto de 100) e despenca nos últimos: o IFR cai abaixo de 30."""
    return [100.0 + i for i in range(40)] + [140.0 - 5 * i for i in range(1, 12)]


def falling_then_rising() -> list[float]:
    """Cai por 40 pregões (IFR perto de 0) e dispara nos últimos: o IFR passa de 70."""
    return [100.0 - i for i in range(40)] + [60.0 + 5 * i for i in range(1, 12)]


def test_buys_with_the_configured_share_of_cash_when_the_rsi_falls_below_the_buy_level():
    prices = rising_then_falling()

    ctx = first_day_with_intents(RelativeStrength(), prices, PARAMS, start=10)

    [intent] = ctx.intents
    price = Decimal(str(ctx.quotes["AAA"].close))
    assert intent.action is StrategyAction.BUY
    assert intent.ticker == "AAA"
    assert intent.quantity == int(Decimal(2000) // price)
    assert "IFR" in intent.reason
    assert "30" in intent.reason


def test_buys_only_on_the_day_of_the_cross_and_not_on_the_days_after():
    prices = rising_then_falling()
    first = first_day_with_intents(RelativeStrength(), prices, PARAMS, start=10)
    cross_end = len(first.history("AAA", 1000))

    # Um dia depois o IFR segue abaixo de 30, mas já cruzou
    after = first_day_with_intents(
        RelativeStrength(), prices[: cross_end + 1], PARAMS, start=cross_end + 1
    )

    assert after.intents == []


def test_sells_the_free_part_when_the_rsi_rises_above_the_sell_level():
    prices = falling_then_rising()

    ctx = first_day_with_intents(
        RelativeStrength(),
        prices,
        PARAMS,
        start=10,
        holdings={"AAA": Holding("AAA", Decimal(100), Decimal(30), Decimal(50))},
    )

    [intent] = ctx.intents
    assert intent.action is StrategyAction.SELL
    # A parte presa em ordens abertas não é vendida
    assert intent.quantity == 70
    assert "70" in intent.reason


def test_no_signal_without_enough_history():
    ctx = first_day_with_intents(RelativeStrength(), [10.0] * 4, PARAMS, start=1)
    assert ctx.intents == []
    assert RelativeStrength().signal(closes([10.0] * 4), PARAMS) is None


def test_the_signal_has_the_price_and_the_rsi_on_their_own_panes_with_the_two_levels():
    signal = RelativeStrength().signal(closes(rising_then_falling()), PARAMS)

    assert signal is not None
    price, rsi = signal.lines
    assert (price.style, price.pane) == (SignalLineStyle.PRICE, SignalPane.PRICE)
    assert (rsi.style, rsi.pane) == (SignalLineStyle.OSCILLATOR, SignalPane.OSCILLATOR)
    assert "5 dias" in rsi.label
    assert all(0 <= point.value <= 100 for point in rsi.points)
    assert [(level.value, level.label) for level in signal.levels] == [
        (30, "Compra 30"),
        (70, "Venda 70"),
    ]


def test_the_signal_marks_the_crossings_on_the_price():
    down = RelativeStrength().signal(closes(rising_then_falling()), PARAMS)
    up = RelativeStrength().signal(closes(falling_then_rising()), PARAMS)

    assert down is not None
    assert up is not None
    assert [m.side for m in down.markers].count("buy") == 1
    assert [m.side for m in up.markers].count("sell") == 1


def test_the_rsi_is_100_when_the_price_only_rises_and_50_when_it_never_moves():
    rising = RelativeStrength().signal(closes([float(i) for i in range(1, 30)]), PARAMS)
    flat = RelativeStrength().signal(closes([10.0] * 30), PARAMS)

    assert rising is not None
    assert flat is not None
    assert rising.lines[1].points[-1].value == 100
    assert flat.lines[1].points[-1].value == 50


@pytest.mark.parametrize(
    ("params", "field"),
    [
        ({**PARAMS, "period": 1}, "period"),
        ({**PARAMS, "buy_below": 60}, "buy_below"),
        ({**PARAMS, "sell_above": 40}, "sell_above"),
        ({**PARAMS, "buy_below": 50, "sell_above": 50}, "sell_above"),
        ({**PARAMS, "cash_pct": 0}, "cash_pct"),
        ({**PARAMS, "tickers": ["ZZZ"]}, "tickers"),
    ],
)
def test_validate_reports_the_field_that_is_out_of_range(params, field):
    assert RelativeStrength.validate(params, {"AAA"})[field]


def test_validate_accepts_the_defaults():
    assert RelativeStrength.validate(PARAMS, {"AAA"}) == {}
