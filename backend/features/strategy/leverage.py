"""
A política de alavancagem que toda estratégia com o parâmetro "Alavancar" ligado recebe.

Ela roda antes da estratégia, sobre o contexto da conta, e enfileira as operações de
crédito: toma empréstimo com o Ibovespa acima da média de 200 pregões, até a dívida-alvo,
e sai da dívida quando ele cai abaixo da média. A estratégia roda depois, vendo o caixa e a
dívida já atualizados.
"""

from __future__ import annotations

from decimal import Decimal

from backend.core.dto.credit import LoanDTO
from backend.core.dto.strategy import StrategyParamValue
from backend.core.utils import format_money, format_quantity
from backend.features.strategy.allocation import whole_shares
from backend.features.strategy.base_strategy import (
    LEVERAGE_KEY,
    TARGET_DEBT_KEY,
    param_bool,
    param_int,
)
from backend.features.strategy.context import INSTALLMENT_RESERVE_DAYS, StrategyContext
from backend.features.strategy.liquidity import ZERO

# O Ibovespa acima da média deste número de pregões é a alta que sustenta a dívida
MA_DAYS = 200
# Prazo fixo de todo empréstimo da política: o maior, para a parcela pesar pouco no caixa
TERM_MONTHS = 60
# A dívida só sobe quando falta mais que esta fração da dívida-alvo
BAND = Decimal("0.2")
# Abaixo disto uma operação de crédito não vale a ordem
MIN_MOVE = Decimal(500)
# Um empréstimo só é amortizado com caixa parado depois de tantos dias de vida
HOLD_DAYS = 30
# A venda para quitar sobra esta margem sobre a dívida: o preço de execução pode ficar abaixo do fechamento
SALE_MARGIN = Decimal("1.01")
CENT = Decimal("0.01")


def is_uptrend(levels: list[Decimal]) -> bool:
    """O último nível do Ibovespa acima da média dos últimos `MA_DAYS`; sem histórico suficiente não há alta."""
    if len(levels) < MA_DAYS:
        return False
    return levels[-1] > sum(levels[-MA_DAYS:], ZERO) / MA_DAYS


def financed_debt(
    ctx: StrategyContext, params: dict[str, StrategyParamValue]
) -> Decimal:
    """A dívida que financia a parte de risco da estratégia: a da conta com "Alavancar" ligado, zero nas demais."""
    return ctx.debt if param_bool(params, LEVERAGE_KEY) else ZERO


def risk_budget(share: Decimal, total: Decimal, debt: Decimal) -> Decimal:
    """
    O valor da parte de risco de uma carteira de `total` reais com `debt` de dívida: a
    meta `share` do patrimônio próprio (o total menos a dívida) mais toda a dívida.
    Com patrimônio de 100, dívida de 20 e meta de 60%, são 60 + 20 = 80 em risco e 40 em renda fixa.
    """
    own = max(total - debt, ZERO)
    return min(share * own + debt, total)


def plan(
    ctx: StrategyContext, params: dict[str, StrategyParamValue], uptrend: bool
) -> None:
    """Enfileira as operações de crédito do dia; as parcelas dos próximos 30 dias já estão fora de `ctx.cash`."""
    # A quitação já inclui o atraso, multa e mora
    if not uptrend:
        _exit(ctx, ctx.cash)
        return
    cash = _pay_overdue(ctx, _cover_installments(ctx))
    target = Decimal(param_int(params, TARGET_DEBT_KEY)) / 100
    if not _take(ctx, cash, target):
        _amortize(ctx, cash)


def _payoff_of(loan: LoanDTO) -> Decimal:
    """O que quita o empréstimo hoje: o saldo mais a multa e a mora do atraso."""
    return loan.balance + loan.overdue_charges


def _by_rate(loans: list[LoanDTO]) -> list[LoanDTO]:
    """Os empréstimos do mais caro ao mais barato; o número desempata."""
    return sorted(loans, key=lambda loan: (-loan.annual_rate, loan.number))


def _pay_overdue(ctx: StrategyContext, cash: Decimal) -> Decimal:
    """Paga o atraso de cada empréstimo que `cash` cobre; devolve o caixa que sobra."""
    for loan in _by_rate([loan for loan in ctx.loans if loan.overdue]):
        owed = sum((o.total for o in loan.overdue), ZERO)
        if owed <= cash:
            ctx.pay_overdue(
                loan.id,
                f"Havia caixa: pagou o atraso de {format_money(owed)} do empréstimo nº {loan.number}",
            )
            cash -= owed
    return max(cash, ZERO)


def _cover_installments(ctx: StrategyContext) -> Decimal:
    """
    Vende ações na proporção da carteira só pelo que falta ao saldo da conta para as
    parcelas dos próximos 30 dias e o atraso em aberto: com 3.000 de parcelas, 500 de atraso
    e 2.000 em conta, vende 1.500 (mais a margem da venda). Devolve o que sobra do saldo
    depois das parcelas, já com a venda: é com ele que o atraso se paga, no mesmo dia, porque
    a venda cai na conta antes das operações seguintes da fila.
    """
    overdue = sum(
        (o.total for loan in ctx.loans for o in loan.overdue),
        ZERO,
    )
    spare = ctx.gross_cash - ctx.installments_due
    short = (overdue - spare) * SALE_MARGIN
    if short > 0:
        proceeds = _sell_for(
            ctx,
            short,
            f"Caixa abaixo das parcelas dos próximos {INSTALLMENT_RESERVE_DAYS} dias",
            "para pagá-las",
        )
        # O piso do que a venda rende: o preço de execução pode ficar abaixo do fechamento
        spare += proceeds / SALE_MARGIN
    return spare


def _take(ctx: StrategyContext, cash: Decimal, target: Decimal) -> bool:
    """Toma o que falta para a dívida-alvo, descontado o caixa parado; devolve se tomou."""
    wanted = target * ctx.networth
    gap = wanted - ctx.debt
    # A dívida só sobe quando a falta passa da banda e o caixa parado não cobre o que falta
    if gap <= BAND * wanted or gap - cash < MIN_MOVE:
        return False
    offer = ctx.offer
    if offer is None or not offer.available or offer.annual_rate is None:
        return False
    amount = min(gap - cash, offer.max_amount).quantize(CENT)
    if amount < MIN_MOVE:
        return False
    ctx.take_loan(
        amount,
        TERM_MONTHS,
        f"Ibovespa acima da média de {MA_DAYS} pregões: tomou {format_money(amount)} "
        f"em {TERM_MONTHS}x a {_percent(offer.annual_rate)} a.a. para chegar à dívida-alvo "
        f"de {_percent(target)} do patrimônio",
    )
    return True


def _amortize(ctx: StrategyContext, cash: Decimal) -> None:
    """O caixa parado paga os empréstimos em dia com mais de `HOLD_DAYS` dias, do mais caro ao mais barato."""
    idle = cash
    for loan in _by_rate(ctx.loans):
        if idle < MIN_MOVE:
            return
        if loan.overdue or (ctx.date - loan.contract_date).days <= HOLD_DAYS:
            continue
        payoff = _payoff_of(loan)
        # O valor que quita vai pela quitação: a amortização o recusa
        if idle >= payoff:
            ctx.payoff_loan(
                loan.id,
                f"Caixa parado de {format_money(idle)}: quitou o empréstimo nº {loan.number}",
            )
            idle -= payoff
            continue
        amount = min(idle, loan.balance - CENT).quantize(CENT)
        if amount >= MIN_MOVE:
            ctx.prepay_loan(
                loan.id,
                amount,
                f"Caixa parado de {format_money(idle)}: amortizou {format_money(amount)} "
                f"do empréstimo nº {loan.number}",
            )
            idle -= amount


def _exit(ctx: StrategyContext, cash: Decimal) -> None:
    """Com o Ibovespa abaixo da média, vende ações na proporção até cobrir a dívida e quita os empréstimos."""
    loans = _by_rate(ctx.loans)
    owed = sum((_payoff_of(loan) for loan in loans), ZERO)
    if owed <= 0:
        return

    # `budget` conta a venda ao fechamento; `safe` desconta a margem, o piso do que a venda rende
    budget = cash
    safe = cash
    short = (owed - cash) * SALE_MARGIN
    if short > 0:
        proceeds = _sell_for(
            ctx,
            short,
            f"Ibovespa abaixo da média de {MA_DAYS} pregões",
            "para quitar a dívida",
        )
        budget += proceeds
        safe += proceeds / SALE_MARGIN

    for loan in loans:
        payoff = _payoff_of(loan)
        if budget >= payoff:
            ctx.payoff_loan(
                loan.id,
                f"Ibovespa abaixo da média de {MA_DAYS} pregões: quitou o empréstimo nº {loan.number}",
            )
            budget -= payoff
            safe -= payoff
            continue
        if loan.overdue:
            # A amortização só vale para o saldo em dia: o atraso se paga pela própria operação
            late = sum((o.total for o in loan.overdue), ZERO)
            if safe >= late:
                ctx.pay_overdue(
                    loan.id,
                    f"Ibovespa abaixo da média de {MA_DAYS} pregões: pagou o atraso de "
                    f"{format_money(late)} do empréstimo nº {loan.number}",
                )
            return
        amount = min(safe, loan.balance - CENT).quantize(CENT)
        if amount >= MIN_MOVE:
            ctx.prepay_loan(
                loan.id,
                amount,
                f"Ibovespa abaixo da média de {MA_DAYS} pregões: amortizou "
                f"{format_money(amount)} do empréstimo nº {loan.number}",
            )
        return


def _sell_for(
    ctx: StrategyContext, value: Decimal, cause: str, purpose: str
) -> Decimal:
    """Vende cada ação na mesma fração até somar `value` (ou tudo que há para vender); devolve o valor estimado da venda."""
    free = {
        ticker: holding.size - holding.reserved
        for ticker, holding in ctx.holdings.items()
        if ticker in ctx.quotes and holding.size > holding.reserved
    }
    sellable = sum(
        (Decimal(str(ctx.quotes[t].close)) * size for t, size in free.items()), ZERO
    )
    if sellable <= 0:
        return ZERO
    fraction = min(value / sellable, Decimal(1))

    proceeds = ZERO
    for ticker, size in free.items():
        quote = ctx.quotes[ticker]
        price = Decimal(str(quote.close))
        wanted = price * size * fraction
        shares = (
            size
            if fraction >= 1
            else min(
                size,
                whole_shares(wanted, price, fractional=quote.fractional),
            )
        )
        # A venda cobre `value`: a ação inteira que falta para o valor entra, até o que há
        if shares * price < wanted and not quote.fractional:
            shares = min(size, shares + 1)
        if shares <= 0:
            continue
        ctx.sell(
            ticker,
            shares,
            f"{cause}: vendeu {format_quantity(shares)} {ticker} {purpose}",
        )
        proceeds += price * shares
    return proceeds


def _percent(fraction: Decimal) -> str:
    return f"{fraction * 100:.1f}%".replace(".", ",")
