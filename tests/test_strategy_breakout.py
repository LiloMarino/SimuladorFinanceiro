"""Rompimento com volume: compra ao passar a máxima com volume, vende ao cair abaixo da mínima."""

from __future__ import annotations

from decimal import Decimal

import pytest

from backend.core.enum import SignalLineStyle, SignalPane, StrategyAction
from backend.features.strategy.breakout import VolumeBreakout
from backend.features.strategy.context import Holding
from tests.strategy_helpers import closes, context

PARAMS = {
    "high_window": 20,
    "volume_pct": 150,
    "exit_window": 10,
    "cash_pct": 20,
    "tickers": ["AAA"],
}


def history(last_close: float, last_volume: int, days: int = 30):
    """Dias parados em R$ 100 com volume 1000 e um último pregão à escolha."""
    prices = [100.0] * (days - 1) + [last_close]
    volumes = [1000] * (days - 1) + [last_volume]
    return closes(prices, volumes=volumes)


def run(last_close: float, last_volume: int, **kwargs):
    ctx = context(history={"AAA": history(last_close, last_volume)}, **kwargs)
    VolumeBreakout().next(ctx, PARAMS)
    return ctx


def test_buys_when_the_close_passes_the_high_with_enough_volume():
    ctx = run(105.0, 2000)

    [intent] = ctx.intents
    assert intent.action is StrategyAction.BUY
    assert intent.ticker == "AAA"
    # 20% de R$ 10.000 a R$ 105
    assert intent.quantity == int(Decimal(2000) // Decimal(105))
    assert "20 dias" in intent.reason


def test_does_not_buy_without_the_volume():
    assert run(105.0, 1400).intents == []


def test_does_not_buy_when_the_close_stays_below_the_high():
    assert run(100.0, 5000).intents == []


def test_does_not_buy_again_an_asset_it_already_holds():
    ctx = run(
        105.0,
        2000,
        holdings={"AAA": Holding("AAA", Decimal(10), Decimal(0), Decimal(90))},
    )
    assert ctx.intents == []


def test_sells_the_free_part_when_the_close_falls_below_the_low():
    ctx = run(
        95.0,
        1000,
        holdings={"AAA": Holding("AAA", Decimal(100), Decimal(40), Decimal(90))},
    )

    [intent] = ctx.intents
    assert intent.action is StrategyAction.SELL
    assert intent.quantity == 60
    assert "10 dias" in intent.reason


def test_does_not_sell_what_it_does_not_hold():
    assert run(95.0, 1000).intents == []


def test_no_signal_without_enough_history():
    short = closes([100.0] * 10)
    ctx = context(history={"AAA": short})
    VolumeBreakout().next(ctx, PARAMS)
    assert ctx.intents == []
    assert VolumeBreakout().signal(short, PARAMS) is None


def test_needs_one_more_day_than_the_longest_window():
    assert VolumeBreakout.needed_days(PARAMS) == 21
    assert VolumeBreakout.needed_days({**PARAMS, "exit_window": 50}) == 51


def test_the_signal_draws_the_price_and_the_channel_with_one_marker_per_breakout():
    prices = [100.0] * 29 + [105.0, 106.0, 107.0]
    volumes = [1000] * 29 + [2000, 2000, 2000]
    signal = VolumeBreakout().signal(closes(prices, volumes=volumes), PARAMS)

    assert signal is not None
    price, upper, lower = signal.lines
    assert price.style is SignalLineStyle.PRICE
    assert {upper.style, lower.style} == {SignalLineStyle.CHANNEL}
    assert {line.pane for line in signal.lines} == {SignalPane.PRICE}
    assert "20 dias" in upper.label
    assert "10 dias" in lower.label
    # A máxima de hoje não conta o próprio dia: é a de ontem
    assert upper.points[-1].value == 106.0
    # Três dias seguidos acima do canal: o marcador é só o primeiro
    assert [m.side for m in signal.markers] == ["buy"]


@pytest.mark.parametrize(
    ("params", "field"),
    [
        ({**PARAMS, "high_window": 2}, "high_window"),
        ({**PARAMS, "volume_pct": 50}, "volume_pct"),
        ({**PARAMS, "exit_window": 80}, "exit_window"),
        ({**PARAMS, "cash_pct": 0}, "cash_pct"),
        ({**PARAMS, "tickers": []}, "tickers"),
    ],
)
def test_validate_reports_the_field_that_is_out_of_range(params, field):
    assert VolumeBreakout.validate(params, {"AAA"})[field]


def test_validate_accepts_the_defaults():
    assert VolumeBreakout.validate(PARAMS, {"AAA"}) == {}
