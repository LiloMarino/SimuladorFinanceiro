from __future__ import annotations

from decimal import Decimal

from backend.core.dto.strategy import StrategyParamValue
from backend.core.enum import StrategyGroup, StrategyParamKind
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


class StateCompanies(BaseStrategy):
    """
    Dá a cada estatal fundada na partida um valor, o valor justo por ação com a opinião
    do dia, e negocia por ele: compra quando o livro vende abaixo do valor e vende quando
    alguém paga acima. As estatais fundadas nascem durante a partida, então o bot as
    descobre pela cotação de cada dia.
    """

    key = "state_companies"
    name = "Estatais"
    bot_names = ("Concursado", "Sócio do Governo", "Caçador de Estatais")
    summary = "Compra estatal fundada abaixo do valor justo e vende acima."
    description = (
        "Dá a cada estatal fundada na partida um valor: o valor justo por ação, "
        "que é o que a empresa vale (o capital posto mais o lucro que ela gerou) "
        "dividido pelo número de ações, mais ou menos uma opinião do dia de até 5%. "
        "Compra ação que o livro vende abaixo desse valor e vende a que alguém paga "
        "acima dele. Com valor justo de R$ 25,10 e preço de R$ 23,00, compra: o preço "
        "está 8% abaixo. O caixa que não está reservado para estatais rende na renda "
        "fixa de liquidez diária."
    )
    group = StrategyGroup.TACTIC
    requires_expansion = Expansion.GOVERNMENT
    term_hint = (
        "O valor justo por ação é quanto a empresa vale dividido pelo número de ações. "
        "O preço anda em volta dele: a bolsa o puxa para cima ou para baixo e, com o "
        "tempo, ele volta para perto do valor justo. Preço 8% abaixo do valor justo "
        "é chance de compra; 8% acima, de venda."
    )
    params = (
        ParamSpec(
            key="state_pct",
            label="Parte do patrimônio em estatais",
            kind=StrategyParamKind.PERCENT,
            default=30,
            min=5,
            max=100,
            unit="%",
            hint=(
                "O máximo do patrimônio que fica em ações de estatais fundadas. Com "
                "R$ 10.000 e 30%, as ações somam até R$ 3.000; o resto fica na renda fixa."
            ),
        ),
        ParamSpec(
            key="company_pct",
            label="Teto por estatal",
            kind=StrategyParamKind.PERCENT,
            default=10,
            min=1,
            max=100,
            unit="%",
            hint=(
                "O máximo do patrimônio em uma só estatal. Com R$ 10.000 e 10%, "
                "uma estatal recebe até R$ 1.000. Por dia, a estratégia negocia "
                "até um quarto desse teto."
            ),
        ),
    )

    def next(self, ctx: StrategyContext, params: dict[str, StrategyParamValue]) -> None:
        state_pct = Decimal(param_int(params, "state_pct")) / 100
        company_pct = Decimal(param_int(params, "company_pct")) / 100
        companies = sorted(
            (
                (quote, quote.state_fair_value)
                for quote in ctx.quotes.values()
                if quote.state_fair_value is not None
            ),
            key=lambda pair: pair[0].ticker,
        )

        # As ordens abertas de ontem saem; o caixa que as de compra prendiam volta ao bot
        available = cancel_open_orders(ctx, {quote.ticker for quote, _ in companies})

        total = equity(ctx, available)
        cap = company_pct * total
        slice_value = cap * DAILY_SLICE
        state_room = state_pct * total - _state_value(ctx)

        # Cada estatal: vende a que o livro paga acima do valor e candidata a compra as demais
        candidates: list[Candidate] = []
        for quote, fair in companies:
            value = fair * (1 + opinion(ctx.seed, quote.ticker, ctx.date))
            worth = round(value, 2)
            held = ctx.holdings.get(quote.ticker)

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

            held_value = money(quote.close) * held.size if held is not None else ZERO
            candidates.append(
                Candidate(
                    quote,
                    worth,
                    held_value,
                    f"Deixou compra de {quote.ticker} a {price_text(worth)}, "
                    f"dentro do valor justo",
                )
            )

        # As compras e o caixa fora das estatais, que rende na renda fixa de liquidez diária
        place_purchases(
            ctx,
            plan_purchases(candidates, slice_value, cap, state_room),
            available,
            cash_reason="Caixa para as estatais",
            idle_reason="o caixa fora das estatais",
        )


def _state_value(ctx: StrategyContext) -> Decimal:
    """O valor das ações de estatal fundada que o bot tem, ao fechamento."""
    total = ZERO
    for ticker, holding in ctx.holdings.items():
        quote = ctx.quotes.get(ticker)
        if quote is not None and quote.state_fair_value is not None:
            total += money(quote.close) * holding.size
    return total
