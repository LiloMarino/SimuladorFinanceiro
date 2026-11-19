"""Estatais: compra abaixo do valor justo, vende acima, só negocia o que tem valor de estatal e exige a expansão Governo."""

from __future__ import annotations

from decimal import Decimal

import pytest

from backend.core.dto.strategy import StrategyParamValue
from backend.core.enum import OrderAction, StrategyAction
from backend.features.strategy import registry
from backend.features.strategy.context import Holding, OpenOrder, Quote
from backend.features.strategy.state_companies import StateCompanies
from tests.strategy_helpers import context, offer

PARAMS: dict[str, StrategyParamValue] = {"state_pct": 30, "company_pct": 10}
LIQUID = offer(daily_liquidity=True, name="CDB Liquidez Diária")


def with_quote(
    ctx,
    fair: float | None,
    *,
    ticker: str = "ESTA3",
    close: float = 20.0,
    bid: float | None = None,
) -> None:
    ctx.quotes[ticker] = Quote(
        ticker, ticker, close, 1000, None, None, False, None, bid, None, fair
    )


def run(fair: float | None, *, bid: float | None = None, **kwargs):
    ctx = context(cash=kwargs.pop("cash", "10000"), offers=[LIQUID], **kwargs)
    with_quote(ctx, fair, bid=bid)
    StateCompanies().next(ctx, PARAMS)
    return ctx


def zero_opinion(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "backend.features.strategy.state_companies.opinion", lambda *_: 0.0
    )


def test_buys_at_the_fair_value(monkeypatch):
    zero_opinion(monkeypatch)
    ctx = run(25.10)

    [buy, *_] = [i for i in ctx.intents if i.action is StrategyAction.BUY]
    assert buy.ticker == "ESTA3"
    assert buy.limit == 25.10
    # Um quarto do teto de 10% de R$ 10.000 (R$ 250) paga 9 ações a R$ 25,10
    assert buy.quantity == 9


def test_sells_when_the_bid_pays_above_the_fair_value(monkeypatch):
    zero_opinion(monkeypatch)
    holdings = {"ESTA3": Holding("ESTA3", Decimal(50), Decimal(0), Decimal(20))}
    ctx = run(25.0, bid=28.0, holdings=holdings)

    [sell] = [i for i in ctx.intents if i.action is StrategyAction.SELL]
    assert sell.ticker == "ESTA3"
    assert sell.limit == 25.0
    assert not [i for i in ctx.intents if i.action is StrategyAction.BUY]


def test_does_not_sell_when_the_bid_is_below_the_fair_value(monkeypatch):
    zero_opinion(monkeypatch)
    holdings = {"ESTA3": Holding("ESTA3", Decimal(50), Decimal(0), Decimal(20))}
    ctx = run(25.0, bid=22.0, holdings=holdings)

    assert not [i for i in ctx.intents if i.action is StrategyAction.SELL]


def test_a_quote_without_state_value_is_not_traded(monkeypatch):
    zero_opinion(monkeypatch)
    ctx = run(None)

    assert not [
        i for i in ctx.intents if i.action in (StrategyAction.BUY, StrategyAction.SELL)
    ]


def test_cancels_yesterdays_orders_and_buys_again(monkeypatch):
    zero_opinion(monkeypatch)
    old = OpenOrder("o1", "ESTA3", OrderAction.BUY, 25.0, Decimal(2))
    ctx = context(cash="10000", offers=[LIQUID])
    ctx.open_orders.append(old)
    with_quote(ctx, 25.0)

    StateCompanies().next(ctx, PARAMS)

    assert ctx.intents[0].action is StrategyAction.CANCEL
    assert any(i.action is StrategyAction.BUY for i in ctx.intents)


def test_the_cash_outside_the_state_companies_goes_to_the_liquid_offer(monkeypatch):
    zero_opinion(monkeypatch)
    ctx = run(25.0)

    invest = [i for i in ctx.intents if i.action is StrategyAction.INVEST]
    assert [i.asset_uuid for i in invest] == [LIQUID.asset_uuid]


def test_stops_buying_when_the_state_share_of_the_equity_is_full(monkeypatch):
    zero_opinion(monkeypatch)
    # R$ 3.000 de estatal em R$ 10.000 de patrimônio já enche os 30% do parâmetro
    holdings = {"ESTA3": Holding("ESTA3", Decimal(150), Decimal(0), Decimal(20))}
    ctx = run(25.0, cash="7000", holdings=holdings)

    assert not [i for i in ctx.intents if i.action is StrategyAction.BUY]


def test_opinion_changes_the_value_within_five_percent():
    ctx = context(cash="10000", offers=[LIQUID])
    with_quote(ctx, 100.0)
    StateCompanies().next(ctx, PARAMS)

    [buy, *_] = [i for i in ctx.intents if i.action is StrategyAction.BUY]
    assert buy.limit is not None
    assert 95.0 <= buy.limit <= 105.0


def test_available_only_with_the_government_expansion():
    assert StateCompanies.available(funds_enabled=False, government_enabled=True)
    assert not StateCompanies.available(funds_enabled=True, government_enabled=False)


def test_registry_refuses_it_without_the_government_expansion():
    with pytest.raises(Exception, match="Governo"):
        registry.ensure_available(
            StateCompanies, funds_enabled=True, government_enabled=False
        )
    registry.ensure_available(
        StateCompanies, funds_enabled=False, government_enabled=True
    )
