"""
O que as estratégias que negociam um valor justo repartem: a opinião do dia, o patrimônio,
a fatia diária, o tamanho de cada compra e o caixa parado na renda fixa de liquidez diária.
"""

from __future__ import annotations

import random
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_DOWN, Decimal

from backend.core.enum import OrderAction
from backend.core.utils import format_money
from backend.features.strategy.context import Quote, StrategyContext
from backend.features.strategy.liquidity import (
    CENT,
    MIN_MOVE,
    ZERO,
    liquid_offer,
    redeem_liquid,
)
from backend.features.variable_income.quantity import affordable_quantity

# A opinião do dia de cada bot sobre cada ativo: sorteada entre -5% e +5% do valor de referência
OPINION_RANGE = 0.05
# A fatia que o bot negocia por dia, como fração do teto de um emissor
DAILY_SLICE = Decimal("0.25")


def opinion(seed: int, ticker: str, day: date) -> float:
    """A opinião do bot sobre o ativo no dia, em fração do valor de referência; a mesma para a mesma semente."""
    return random.Random(f"{seed}:{ticker}:{day.isoformat()}").uniform(
        -OPINION_RANGE, OPINION_RANGE
    )


@dataclass(frozen=True)
class Candidate:
    """Um ativo que o bot quer comprar ao preço limite, com o que já tem dele e o motivo."""

    quote: Quote
    limit: float
    held_value: Decimal
    why: str


@dataclass(frozen=True)
class Purchase:
    candidate: Candidate
    shares: Decimal

    @property
    def cost(self) -> Decimal:
        return money(self.candidate.limit) * self.shares


def money(value: float) -> Decimal:
    return Decimal(str(value))


def price_text(value: float) -> str:
    return format_money(money(value))


def equity(ctx: StrategyContext, cash: Decimal) -> Decimal:
    """O patrimônio: o caixa, as ações ao fechamento e a renda fixa."""
    stocks = ZERO
    for ticker, holding in ctx.holdings.items():
        quote = ctx.quotes.get(ticker)
        price = money(quote.close) if quote else holding.avg_price
        stocks += price * holding.size
    fixed = sum((h.current_value for h in ctx.fixed_holdings), ZERO)
    return cash + stocks + fixed


def quantity(cash: Decimal, price: float, quote: Quote) -> Decimal:
    """Quantas unidades `cash` paga ao preço; zero sem dinheiro."""
    if cash <= 0 or price <= 0:
        return ZERO
    return affordable_quantity(cash, money(price), fractional=quote.fractional)


def cancel_open_orders(ctx: StrategyContext, tickers: set[str]) -> Decimal:
    """Cancela as ordens abertas de ontem nos `tickers`; devolve o caixa total do bot, com o que as de compra prendiam."""
    available = ctx.cash
    for order in ctx.open_orders:
        if order.ticker in tickers:
            ctx.cancel(order.id, f"Refez a ordem de {order.ticker} do dia")
            if order.action == OrderAction.BUY and order.price is not None:
                available += money(order.price) * order.remaining
    return available


def plan_purchases(
    candidates: Iterable[Candidate], slice_value: Decimal, cap: Decimal, room: Decimal
) -> list[Purchase]:
    """Cada compra pede só o que cabe na fatia do dia, no teto do emissor e na parte do patrimônio reservada à classe (`room`)."""
    purchases: list[Purchase] = []
    for candidate in candidates:
        limit_room = min(slice_value, cap - candidate.held_value, room)
        shares = quantity(limit_room, candidate.limit, candidate.quote)
        if shares > 0:
            room -= shares * money(candidate.limit)
            purchases.append(Purchase(candidate, shares))
    return purchases


def place_purchases(
    ctx: StrategyContext,
    purchases: list[Purchase],
    available: Decimal,
    *,
    cash_reason: str,
    idle_reason: str,
) -> None:
    """
    Faz as compras: o caixa que falta vem do resgate da renda fixa de liquidez diária e o
    que sobra rende nela. `cash_reason` e `idle_reason` nomeiam a classe nas mensagens.
    """
    need = sum((p.cost for p in purchases), ZERO)
    if need > available:
        available += redeem_liquid(ctx, need - available, cash_reason)
    for purchase in purchases:
        candidate = purchase.candidate
        shares = min(
            purchase.shares,
            quantity(available, candidate.limit, candidate.quote),
        )
        if shares <= 0:
            continue
        ctx.buy(candidate.quote.ticker, shares, candidate.why, candidate.limit)
        available -= shares * money(candidate.limit)

    offer = liquid_offer(ctx)
    idle = available.quantize(CENT, rounding=ROUND_DOWN)
    if offer is not None and idle >= MIN_MOVE:
        ctx.invest(
            offer.asset_uuid,
            idle,
            f"Aplicou {format_money(idle)} em {offer.name}, {idle_reason}",
        )
