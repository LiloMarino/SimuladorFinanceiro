from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_DOWN, Decimal

from backend.core.dto.strategy import StrategyParamValue
from backend.core.enum import OrderAction, StrategyGroup, StrategyParamKind
from backend.core.fund_reference import FundReference, price_ceiling
from backend.core.professions import Expansion
from backend.core.utils import format_money, format_quantity
from backend.features.strategy.base_strategy import (
    BaseStrategy,
    ParamSpec,
    param_int,
)
from backend.features.strategy.context import Quote, StrategyContext
from backend.features.strategy.liquidity import (
    CENT,
    MIN_MOVE,
    ZERO,
    liquid_offer,
    redeem_liquid,
)
from backend.features.variable_income.quantity import affordable_quantity

# O prêmio da cota é duas vezes o desempenho sobre o CDI, limitado a esta fração do PL por cota
PREMIUM_LEVERAGE = 2
PREMIUM_LIMIT = 0.20
# A opinião do dia de cada bot sobre cada cota: sorteada entre -5% e +5% do PL por cota
OPINION_RANGE = 0.05
# A fatia que o bot negocia por dia, como fração do teto de uma gestora
DAILY_SLICE = Decimal("0.25")


def opinion(seed: int, ticker: str, day: date) -> float:
    """A opinião do bot sobre a cota no dia, em fração do PL por cota; a mesma para a mesma semente."""
    return random.Random(f"{seed}:{ticker}:{day.isoformat()}").uniform(
        -OPINION_RANGE, OPINION_RANGE
    )


def fair_value(fund: FundReference, bias: float) -> float:
    """O valor que o bot dá à cota: o PL por cota mais o prêmio do desempenho e a opinião do dia."""
    premium = max(
        -PREMIUM_LIMIT, min(PREMIUM_LIMIT, PREMIUM_LEVERAGE * fund.performance)
    )
    return fund.nav * (1 + premium + bias)


class FundQuotas(BaseStrategy):
    """
    Dá a cada cota de gestora um valor, o patrimônio por cota com um prêmio pelo
    desempenho contra o CDI, e negocia por ele: compra quando o livro vende abaixo do
    valor e vende quando alguém paga acima.
    """

    key = "fund_quotas"
    name = "Cotas de gestoras"
    bot_names = ("Cotista", "Caçador de Ágio", "Dona Cota")
    summary = "Compra cota abaixo do valor que dá a ela e vende acima."
    description = (
        "Dá a cada cota de gestora um valor: o patrimônio por cota (o que a gestora "
        "tem dividido pelo número de cotas) mais ou menos um prêmio. O prêmio é "
        "o dobro de quanto a cota rendeu acima do CDI nos últimos 126 pregões, "
        "limitado a 20% para cima ou para baixo, e cada dia traz uma opinião própria "
        "de até 5%. Compra cota que o livro vende abaixo desse valor, vende a que "
        "alguém paga acima dele e nunca paga mais que 1,2 vez o patrimônio por cota. "
        "O caixa que não está reservado para cotas rende na renda fixa de liquidez diária."
    )
    group = StrategyGroup.TACTIC
    requires_expansion = Expansion.FUNDS
    term_hint = (
        "P/VP é o preço da cota dividido pelo patrimônio por cota: 1,10 é 10% de ágio "
        "(paga-se 10% a mais que o patrimônio) e 0,90 é 10% de deságio. O desempenho "
        "sobre o CDI é quanto a cota rendeu a mais ou a menos que a renda fixa: "
        "cota que rendeu 6% quando o CDI rendeu 4% está 2 pontos acima e ganha "
        "prêmio de 4%; é um bom valor ela custar um pouco mais que o patrimônio."
    )
    params = (
        ParamSpec(
            key="quota_pct",
            label="Parte do patrimônio em cotas",
            kind=StrategyParamKind.PERCENT,
            default=40,
            min=5,
            max=100,
            unit="%",
            hint=(
                "O máximo do patrimônio que fica em cotas de gestoras. Com "
                "R$ 10.000 e 40%, as cotas somam até R$ 4.000; o resto fica na renda fixa."
            ),
        ),
        ParamSpec(
            key="fund_pct",
            label="Teto por gestora",
            kind=StrategyParamKind.PERCENT,
            default=15,
            min=1,
            max=100,
            unit="%",
            hint=(
                "O máximo do patrimônio em uma só gestora. Com R$ 10.000 e 15%, "
                "uma gestora recebe até R$ 1.500. Por dia, a estratégia negocia "
                "até um quarto desse teto."
            ),
        ),
    )

    def next(self, ctx: StrategyContext, params: dict[str, StrategyParamValue]) -> None:
        quota_pct = Decimal(param_int(params, "quota_pct")) / 100
        fund_pct = Decimal(param_int(params, "fund_pct")) / 100
        funds = sorted(
            (
                (quote, quote.fund)
                for quote in ctx.quotes.values()
                if quote.fund is not None
            ),
            key=lambda pair: pair[0].ticker,
        )

        # As ordens abertas de ontem saem; o caixa que as de compra prendiam volta ao bot
        available = ctx.cash
        tickers = {quote.ticker for quote, _ in funds}
        for order in ctx.open_orders:
            if order.ticker in tickers:
                ctx.cancel(order.id, f"Refez a ordem de {order.ticker} do dia")
                if order.action == OrderAction.BUY and order.price is not None:
                    available += _money(order.price) * order.remaining

        equity = _equity(ctx, available)
        cap = fund_pct * equity
        slice_value = cap * DAILY_SLICE
        quota_room = quota_pct * equity - _quota_value(ctx)

        # Cada cota: vende a que o livro paga acima do valor e candidata a compra as demais
        candidates: list[_Candidate] = []
        for quote, fund in funds:
            value = fair_value(fund, opinion(ctx.seed, quote.ticker, ctx.date))
            held = ctx.holdings.get(quote.ticker)
            held_value = _money(quote.close) * held.size if held is not None else ZERO
            worth = round(value, 2)

            # A venda do emissor: compra só no último pregão, e só se o preço fixo cabe no valor
            if fund.fixed_price is not None:
                if fund.fixed_price_last_session and fund.fixed_price <= value:
                    candidates.append(
                        _Candidate(
                            quote,
                            fund.fixed_price,
                            held_value,
                            f"Comprou {quote.ticker} da oferta a {_price(fund.fixed_price)}, "
                            f"abaixo do valor de {_price(worth)}",
                        )
                    )
                continue

            if held is not None and quote.bid is not None and quote.bid > value:
                shares = min(
                    held.size,
                    max(_quantity(slice_value, worth, quote), Decimal(1)),
                )
                ctx.sell(
                    quote.ticker,
                    shares,
                    f"Vendeu {format_quantity(shares)} {quote.ticker}: pagam "
                    f"{_price(quote.bid)}, acima do valor de {_price(worth)}",
                    worth,
                )
                continue

            limit = min(worth, price_ceiling(fund.nav))
            candidates.append(
                _Candidate(
                    quote,
                    limit,
                    held_value,
                    f"Deixou compra de {quote.ticker} a {_price(limit)}, "
                    f"dentro do valor de {_price(worth)}",
                )
            )

        # Cada compra pede só o que cabe no teto da gestora e na parte do patrimônio em cotas
        purchases: list[_Purchase] = []
        for candidate in candidates:
            room = min(slice_value, cap - candidate.held_value, quota_room)
            shares = _quantity(room, candidate.limit, candidate.quote)
            if shares > 0:
                quota_room -= shares * _money(candidate.limit)
                purchases.append(_Purchase(candidate, shares))

        # O caixa que falta para as compras vem do resgate da renda fixa de liquidez diária
        need = sum((p.cost for p in purchases), ZERO)
        if need > available:
            available += redeem_liquid(ctx, need - available, "Caixa para as cotas")
        for purchase in purchases:
            shares = min(
                purchase.shares,
                _quantity(
                    available, purchase.candidate.limit, purchase.candidate.quote
                ),
            )
            if shares <= 0:
                continue
            candidate = purchase.candidate
            ctx.buy(candidate.quote.ticker, shares, candidate.why, candidate.limit)
            available -= shares * _money(candidate.limit)

        # O que não foi para cotas rende na renda fixa de liquidez diária
        offer = liquid_offer(ctx)
        idle = available.quantize(CENT, rounding=ROUND_DOWN)
        if offer is not None and idle >= MIN_MOVE:
            ctx.invest(
                offer.asset_uuid,
                idle,
                f"Aplicou {format_money(idle)} em {offer.name}, o caixa fora das cotas",
            )


@dataclass(frozen=True)
class _Candidate:
    """Uma cota que o bot quer comprar ao preço limite, com o que já tem dela e o motivo."""

    quote: Quote
    limit: float
    held_value: Decimal
    why: str


@dataclass(frozen=True)
class _Purchase:
    candidate: _Candidate
    shares: Decimal

    @property
    def cost(self) -> Decimal:
        return _money(self.candidate.limit) * self.shares


def _money(value: float) -> Decimal:
    return Decimal(str(value))


def _price(value: float) -> str:
    return format_money(_money(value))


def _equity(ctx: StrategyContext, cash: Decimal) -> Decimal:
    """O patrimônio: o caixa, as ações ao fechamento e a renda fixa."""
    stocks = ZERO
    for ticker, holding in ctx.holdings.items():
        quote = ctx.quotes.get(ticker)
        price = _money(quote.close) if quote else holding.avg_price
        stocks += price * holding.size
    fixed = sum((h.current_value for h in ctx.fixed_holdings), ZERO)
    return cash + stocks + fixed


def _quota_value(ctx: StrategyContext) -> Decimal:
    """O valor das cotas de gestora que o bot tem, ao fechamento."""
    total = ZERO
    for ticker, holding in ctx.holdings.items():
        quote = ctx.quotes.get(ticker)
        if quote is not None and quote.fund is not None:
            total += _money(quote.close) * holding.size
    return total


def _quantity(money: Decimal, price: float, quote: Quote) -> Decimal:
    """Quantas cotas `money` paga ao preço; zero sem dinheiro."""
    if money <= 0 or price <= 0:
        return ZERO
    return affordable_quantity(money, _money(price), fractional=quote.fractional)
