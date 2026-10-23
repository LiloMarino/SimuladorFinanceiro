"""Rebalanceamento por meta: aporte dentro do limite, venda e resgate fora dele e os pisos."""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from backend.core.dto.strategy import AllocationViewDTO
from backend.core.enum import StrategyAction
from backend.features.strategy.context import FixedHolding, Holding
from backend.features.strategy.rebalance import TargetRebalance
from tests.strategy_helpers import closes, context, offer

PARAMS = {"asset": "AAA", "stock_target": 60, "max_deviation": 5}
LIQUID = offer(daily_liquidity=True, name="CDB Liquidez Diária")


def shares(quantity: int) -> dict[str, Holding]:
    return {"AAA": Holding("AAA", quantity, 0, Decimal(100))}


def fixed(
    value: str, *, daily: bool = True, redeemable: str | None = None
) -> FixedHolding:
    return FixedHolding(
        uuid.uuid4(),
        "CDB Liquidez Diária" if daily else "CDB Longo",
        Decimal(value),
        daily,
        Decimal(redeemable or value) if daily else None,
    )


def run(cash: str = "0", **kwargs):
    ctx = context(
        cash=cash,
        history={"AAA": closes([100.0])},
        offers=kwargs.pop("offers", [LIQUID]),
        **kwargs,
    )
    TargetRebalance().next(ctx, PARAMS)
    return ctx


def test_the_first_cash_is_split_by_the_target():
    ctx = run(cash="10000")

    buy, invest = ctx.intents
    assert (buy.action, buy.ticker, buy.quantity) == (StrategyAction.BUY, "AAA", 60)
    assert invest.action is StrategyAction.INVEST
    assert invest.asset_uuid == LIQUID.asset_uuid
    assert invest.value == Decimal("4000.00")


def test_within_the_limit_the_cash_goes_to_the_side_below_the_target():
    # Ações em 58% (meta 60%, limite 5 p.p.): R$ 1.000 de caixa levam as duas à meta
    ctx = run(
        cash="1000",
        holdings=shares(58),
        fixed_holdings=[fixed("4200")],
    )

    buy, invest = ctx.intents
    assert (buy.action, buy.quantity) == (StrategyAction.BUY, 8)
    assert invest.value == Decimal("200.00")
    assert "caixa parado" in buy.reason


def test_within_the_limit_nothing_is_sold_even_when_a_side_is_above_the_target():
    # Ações em 63%: dentro do limite, o caixa pequeno vai todo para a renda fixa
    ctx = run(
        cash="100",
        holdings=shares(63),
        fixed_holdings=[fixed("3700")],
    )

    [invest] = ctx.intents
    assert invest.action is StrategyAction.INVEST
    assert invest.value == Decimal("100.00")


def test_stocks_above_the_limit_are_sold_and_the_money_goes_to_fixed_income():
    # Ações em 70% da carteira contra a meta de 60%
    ctx = run(holdings=shares(70), fixed_holdings=[fixed("3000")])

    sell, invest = ctx.intents
    assert (sell.action, sell.quantity) == (StrategyAction.SELL, 10)
    assert (invest.action, invest.value) == (StrategyAction.INVEST, Decimal("1000.00"))
    assert "70,0%" in sell.reason
    assert "60,0%" in sell.reason


def test_stocks_below_the_limit_are_bought_with_a_redeem_of_daily_liquidity():
    # Ações em 50% da carteira contra a meta de 60%
    ctx = run(holdings=shares(50), fixed_holdings=[fixed("5000")])

    redeem, buy = ctx.intents
    assert (redeem.action, redeem.value) == (StrategyAction.REDEEM, Decimal("1000.00"))
    assert (buy.action, buy.quantity) == (StrategyAction.BUY, 10)


def test_the_redeem_stops_at_what_daily_liquidity_pays_net():
    # O título resgata só R$ 600 líquidos: a compra segue o que o caixa tem
    ctx = run(
        holdings=shares(50),
        fixed_holdings=[fixed("5000", redeemable="600")],
    )

    redeem, buy = ctx.intents
    assert redeem.value == Decimal("600.00")
    assert buy.quantity == 6


def test_what_the_strategy_does_not_manage_stays_put():
    # 80% da carteira estão em outra ação e 20% num título sem liquidez diária
    ctx = context(
        cash="0",
        history={"AAA": closes([100.0]), "OTHER": closes([100.0])},
        holdings={"OTHER": Holding("OTHER", 80, 0, Decimal(100))},
        fixed_holdings=[fixed("2000", daily=False)],
        offers=[LIQUID],
    )

    TargetRebalance().next(ctx, PARAMS)

    assert ctx.intents == []


def test_the_part_of_the_asset_held_by_open_orders_is_not_sold():
    ctx = run(
        holdings={"AAA": Holding("AAA", 70, 65, Decimal(100))},
        fixed_holdings=[fixed("3000")],
    )

    sell, _ = ctx.intents
    assert sell.quantity == 5


def test_no_orders_when_there_is_no_cash_and_the_split_is_within_the_limit():
    ctx = run(holdings=shares(62), fixed_holdings=[fixed("3800")])
    assert ctx.intents == []


def test_without_a_daily_liquidity_offer_it_only_trades_the_stock_side():
    ctx = run(cash="10000", offers=[])

    [buy] = ctx.intents
    assert buy.action is StrategyAction.BUY


def test_the_offer_with_a_per_player_cap_is_not_used():
    capped = offer(daily_liquidity=True, player_cap="5000")
    ctx = run(cash="10000", offers=[capped])

    assert [i.action for i in ctx.intents] == [StrategyAction.BUY]


def test_the_view_shows_each_side_against_the_target_and_what_it_would_do_today():
    ctx = context(
        cash="0",
        history={"AAA": closes([100.0])},
        holdings=shares(70),
        fixed_holdings=[fixed("3000")],
        offers=[LIQUID],
    )

    view = TargetRebalance().view(ctx, PARAMS)

    assert isinstance(view, AllocationViewDTO)
    stocks, fixed_income = view.items
    assert (stocks.current_pct, stocks.target_pct, stocks.deviation_pp) == (
        Decimal("70.0"),
        Decimal("60.0"),
        Decimal("10.0"),
    )
    assert (fixed_income.current_pct, fixed_income.deviation_pp) == (
        Decimal("30.0"),
        Decimal("-10.0"),
    )
    assert view.limit_pp == 5
    assert view.has_liquid_offer
    assert len(view.today) == 2


@pytest.mark.parametrize(
    ("params", "field"),
    [
        ({**PARAMS, "stock_target": 5}, "stock_target"),
        ({**PARAMS, "stock_target": 95}, "stock_target"),
        ({**PARAMS, "max_deviation": 0}, "max_deviation"),
        ({**PARAMS, "max_deviation": 25}, "max_deviation"),
        ({**PARAMS, "asset": "ZZZ"}, "asset"),
    ],
)
def test_validate_reports_the_field_that_is_out_of_range(params, field):
    assert TargetRebalance.validate(params, {"AAA"})[field]


def test_validate_accepts_the_defaults():
    assert TargetRebalance.validate(PARAMS, {"AAA"}) == {}
