"""Cotas de gestoras: o valor da cota, a compra até o teto, a venda acima do valor e a oferta do emissor."""

from __future__ import annotations

from decimal import Decimal

import pytest

from backend.core.dto.strategy import StrategyParamValue
from backend.core.enum import OrderAction, StrategyAction
from backend.core.fund_reference import FundReference, price_ceiling
from backend.features.strategy.context import Holding, OpenOrder, Quote
from backend.features.strategy.fund_quotas import FundQuotas, fair_value, opinion
from tests.strategy_helpers import TODAY, context, offer

PARAMS: dict[str, StrategyParamValue] = {"quota_pct": 40, "fund_pct": 15}
LIQUID = offer(daily_liquidity=True, name="CDB Liquidez Diária")


def reference(
    nav: float = 100.0,
    performance: float = 0.0,
    fixed_price: float | None = None,
    last_session: bool = False,
    book_price: float | None = None,
) -> FundReference:
    return FundReference(nav, performance, fixed_price, last_session, book_price)


def with_quote(
    ctx,
    fund: FundReference | None,
    *,
    ticker: str = "AURA11",
    close: float = 100.0,
    bid: float | None = None,
) -> None:
    ctx.quotes[ticker] = Quote(
        ticker, ticker, close, 1000, None, None, False, None, bid, fund
    )


def run(fund: FundReference | None, *, bid: float | None = None, **kwargs):
    ctx = context(cash=kwargs.pop("cash", "10000"), offers=[LIQUID], **kwargs)
    with_quote(ctx, fund, bid=bid)
    FundQuotas().next(ctx, PARAMS)
    return ctx


def zero_opinion(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("backend.features.strategy.fund_quotas.opinion", lambda *_: 0.0)


def test_value_adds_twice_the_performance_to_the_nav():
    # 3 pontos acima do CDI valem 6% de prêmio
    assert fair_value(reference(performance=0.03), 0.0) == pytest.approx(106.0)


def test_value_premium_is_clamped_to_twenty_percent_both_ways():
    assert fair_value(reference(performance=0.50), 0.0) == pytest.approx(120.0)
    assert fair_value(reference(performance=-0.50), 0.0) == pytest.approx(80.0)


def test_opinion_is_the_same_for_the_same_seed_ticker_and_day():
    assert opinion(7, "AURA11", TODAY) == opinion(7, "AURA11", TODAY)
    assert opinion(7, "AURA11", TODAY) != opinion(8, "AURA11", TODAY)
    assert -0.05 <= opinion(7, "AURA11", TODAY) <= 0.05


def test_buys_the_quota_at_the_value_when_it_is_under_the_cap(monkeypatch):
    zero_opinion(monkeypatch)
    ctx = run(reference(performance=0.03))

    [buy, *_] = [i for i in ctx.intents if i.action is StrategyAction.BUY]
    assert buy.ticker == "AURA11"
    assert buy.limit == 106.0
    # Um quarto do teto de 15% de R$ 10.000 (R$ 375) paga 3 cotas a R$ 106
    assert buy.quantity == 3


def test_buy_limit_never_passes_the_cap_over_the_nav(monkeypatch):
    zero_opinion(monkeypatch)
    # Valor de 120 (prêmio no limite) mais opinião de +5% passaria do teto de 120
    monkeypatch.setattr(
        "backend.features.strategy.fund_quotas.opinion", lambda *_: 0.05
    )
    ctx = run(reference(performance=0.50))

    [buy, *_] = [i for i in ctx.intents if i.action is StrategyAction.BUY]
    assert buy.limit == price_ceiling(100.0) == 120.0


def test_sells_when_the_bid_pays_above_the_value(monkeypatch):
    zero_opinion(monkeypatch)
    holdings = {"AURA11": Holding("AURA11", Decimal(50), Decimal(0), Decimal(100))}
    ctx = run(reference(), bid=110.0, holdings=holdings)

    [sell] = [i for i in ctx.intents if i.action is StrategyAction.SELL]
    assert sell.ticker == "AURA11"
    assert sell.limit == 100.0
    assert not [i for i in ctx.intents if i.action is StrategyAction.BUY]


def test_does_not_sell_when_the_bid_is_below_the_value(monkeypatch):
    zero_opinion(monkeypatch)
    holdings = {"AURA11": Holding("AURA11", Decimal(50), Decimal(0), Decimal(100))}
    ctx = run(reference(), bid=95.0, holdings=holdings)

    assert not [i for i in ctx.intents if i.action is StrategyAction.SELL]


def test_cancels_yesterdays_orders_and_buys_again(monkeypatch):
    zero_opinion(monkeypatch)
    old = OpenOrder("o1", "AURA11", OrderAction.BUY, 100.0, Decimal(2))
    ctx = context(cash="10000", offers=[LIQUID])
    ctx.open_orders.append(old)
    with_quote(ctx, reference())

    FundQuotas().next(ctx, PARAMS)

    assert ctx.intents[0].action is StrategyAction.CANCEL
    assert ctx.intents[0].order_id == "o1"
    assert any(i.action is StrategyAction.BUY for i in ctx.intents)


def test_fixed_price_is_bought_only_on_the_last_session(monkeypatch):
    zero_opinion(monkeypatch)
    early = run(reference(fixed_price=90.0, last_session=False))
    assert not [i for i in early.intents if i.action is StrategyAction.BUY]

    last = run(reference(fixed_price=90.0, last_session=True))
    [buy, *_] = [i for i in last.intents if i.action is StrategyAction.BUY]
    assert buy.limit == 90.0


def test_fixed_price_above_the_value_is_not_bought(monkeypatch):
    zero_opinion(monkeypatch)
    ctx = run(reference(fixed_price=101.0, last_session=True))

    assert not [i for i in ctx.intents if i.action is StrategyAction.BUY]


def test_a_quote_without_fund_is_not_traded(monkeypatch):
    zero_opinion(monkeypatch)
    ctx = run(None)

    assert not [
        i for i in ctx.intents if i.action in (StrategyAction.BUY, StrategyAction.SELL)
    ]


def test_the_cash_outside_the_quotas_goes_to_the_liquid_offer(monkeypatch):
    zero_opinion(monkeypatch)
    ctx = run(reference())

    invest = [i for i in ctx.intents if i.action is StrategyAction.INVEST]
    assert [i.asset_uuid for i in invest] == [LIQUID.asset_uuid]


def test_the_photo_makes_the_fixed_price_cheap_for_a_pessimistic_bot():
    """Opinião de -5% dá valor de 95 e o preço fixo de 100 fica caro; com a foto a 110, o valor passa a ser 110."""
    ctx = context(cash="10000", offers=[LIQUID])
    with_quote(ctx, reference(fixed_price=100.0, last_session=True))
    FundQuotas().run(ctx, PARAMS, lambda _: -0.05)
    assert not [i for i in ctx.intents if i.action is StrategyAction.BUY]

    ctx = context(cash="10000", offers=[LIQUID])
    with_quote(ctx, reference(fixed_price=100.0, last_session=True, book_price=110.0))
    FundQuotas().run(ctx, PARAMS, lambda _: -0.05)
    [buy, *_] = [i for i in ctx.intents if i.action is StrategyAction.BUY]
    assert buy.limit == 100.0


def test_the_photo_never_lifts_the_value_over_the_buy_ceiling():
    """Foto a 150 vale no máximo o teto de 120; o preço fixo acima dele segue caro."""
    ctx = context(cash="10000", offers=[LIQUID])
    with_quote(ctx, reference(fixed_price=125.0, last_session=True, book_price=150.0))
    FundQuotas().run(ctx, PARAMS, lambda _: 0.0)

    assert not [i for i in ctx.intents if i.action is StrategyAction.BUY]


def test_the_photo_has_no_weight_before_the_last_session():
    ctx = context(cash="10000", offers=[LIQUID])
    with_quote(ctx, reference(fixed_price=100.0, last_session=False, book_price=110.0))
    FundQuotas().run(ctx, PARAMS, lambda _: 0.0)

    assert not [i for i in ctx.intents if i.action is StrategyAction.BUY]


def test_the_opinion_given_to_run_replaces_the_daily_one():
    ctx = context(cash="10000", offers=[LIQUID])
    with_quote(ctx, reference())
    FundQuotas().run(ctx, PARAMS, lambda _: 0.05)

    [buy, *_] = [i for i in ctx.intents if i.action is StrategyAction.BUY]
    assert buy.limit == 105.0
