from __future__ import annotations

from decimal import Decimal

from backend.core.dto.strategy import StrategyParamValue
from backend.core.enum import StrategyGroup, StrategyParamKind
from backend.core.fund_reference import FundReference, price_ceiling
from backend.core.professions import Expansion
from backend.core.utils import format_quantity
from backend.features.strategy.base_strategy import (
    BaseStrategy,
    ParamSpec,
    param_int,
)
from backend.features.strategy.context import StrategyContext
from backend.features.strategy.fair_value_trading import (
    DAILY_SLICE,
    Candidate,
    cancel_open_orders,
    equity,
    money,
    opinion,
    place_purchases,
    plan_purchases,
    price_text,
    quantity,
)
from backend.features.strategy.liquidity import ZERO

# O prêmio da cota é duas vezes o desempenho sobre o CDI, limitado a esta fração do PL por cota
PREMIUM_LEVERAGE = 2
PREMIUM_LIMIT = 0.20


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
        available = cancel_open_orders(ctx, {quote.ticker for quote, _ in funds})

        total = equity(ctx, available)
        cap = fund_pct * total
        slice_value = cap * DAILY_SLICE
        quota_room = quota_pct * total - _quota_value(ctx)

        # Cada cota: vende a que o livro paga acima do valor e candidata a compra as demais
        candidates: list[Candidate] = []
        for quote, fund in funds:
            value = fair_value(fund, opinion(ctx.seed, quote.ticker, ctx.date))
            held = ctx.holdings.get(quote.ticker)
            held_value = money(quote.close) * held.size if held is not None else ZERO
            worth = round(value, 2)

            # A venda do emissor: compra só no último pregão, e só se o preço fixo cabe no valor
            if fund.fixed_price is not None:
                if fund.fixed_price_last_session and fund.fixed_price <= value:
                    candidates.append(
                        Candidate(
                            quote,
                            fund.fixed_price,
                            held_value,
                            f"Comprou {quote.ticker} da oferta a {price_text(fund.fixed_price)}, "
                            f"abaixo do valor de {price_text(worth)}",
                        )
                    )
                continue

            if held is not None and quote.bid is not None and quote.bid > value:
                shares = min(
                    held.size,
                    max(quantity(slice_value, worth, quote), Decimal(1)),
                )
                ctx.sell(
                    quote.ticker,
                    shares,
                    f"Vendeu {format_quantity(shares)} {quote.ticker}: pagam "
                    f"{price_text(quote.bid)}, acima do valor de {price_text(worth)}",
                    worth,
                )
                continue

            limit = min(worth, price_ceiling(fund.nav))
            candidates.append(
                Candidate(
                    quote,
                    limit,
                    held_value,
                    f"Deixou compra de {quote.ticker} a {price_text(limit)}, "
                    f"dentro do valor de {price_text(worth)}",
                )
            )

        # As compras e o caixa fora das cotas, que rende na renda fixa de liquidez diária
        place_purchases(
            ctx,
            plan_purchases(candidates, slice_value, cap, quota_room),
            available,
            cash_reason="Caixa para as cotas",
            idle_reason="o caixa fora das cotas",
        )


def _quota_value(ctx: StrategyContext) -> Decimal:
    """O valor das cotas de gestora que o bot tem, ao fechamento."""
    total = ZERO
    for ticker, holding in ctx.holdings.items():
        quote = ctx.quotes.get(ticker)
        if quote is not None and quote.fund is not None:
            total += money(quote.close) * holding.size
    return total
