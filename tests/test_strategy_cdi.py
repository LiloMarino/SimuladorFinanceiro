"""Referência de renda fixa: todo o caixa parado na melhor oferta do CDI."""

from __future__ import annotations

from decimal import Decimal

from backend.core.enum import RateIndexType, StrategyAction
from backend.features.strategy.cdi import CdiReference
from tests.strategy_helpers import context, offer


def test_invests_all_the_idle_cash_in_the_cdi_offer_that_pays_most_after_tax():
    # 110% do CDI com IR de 15% rende 93,5%; 100% isento rende 100%
    taxed = offer(interest_rate="1.10", tax="0.15", name="CDB 110%")
    exempt = offer(interest_rate="1.00", tax="0", name="LCI 100%")
    ctx = context(cash="5000.789", offers=[taxed, exempt])

    CdiReference().next(ctx, {})

    [intent] = ctx.intents
    assert intent.action is StrategyAction.INVEST
    assert intent.asset_uuid == exempt.asset_uuid
    # Centavos truncados: o caixa nunca é excedido
    assert intent.value == Decimal("5000.78")


def test_ignores_offers_that_are_not_indexed_to_the_cdi():
    ctx = context(offers=[offer(rate_index=RateIndexType.IPCA)])
    CdiReference().next(ctx, {})
    assert ctx.intents == []


def test_does_nothing_below_the_minimum_investment():
    ctx = context(cash="0.50", offers=[offer()])
    CdiReference().next(ctx, {})
    assert ctx.intents == []


def test_a_zero_balance_buys_nothing():
    ctx = context(cash="0", offers=[offer()])
    CdiReference().next(ctx, {})
    assert ctx.intents == []


def test_has_no_parameters():
    assert CdiReference.validate({}, set()) == {}
