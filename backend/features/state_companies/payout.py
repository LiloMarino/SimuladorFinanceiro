"""Dividendos das estatais: payout da política e o corte de lucro que o controle causa."""

from decimal import Decimal

from backend.core.enum import DividendPolicy, StateControl

# Fração do lucro que cada política paga ao acionista
PAYOUT: dict[DividendPolicy, Decimal] = {
    DividendPolicy.REINVEST: Decimal("0.25"),
    DividendPolicy.NORMAL: Decimal("0.50"),
    DividendPolicy.SQUEEZE: Decimal("0.80"),
}

# Corte de lucro por ponto percentual de preço segurado:
# P20 corta 30% do lucro
PROFIT_CUT_PER_PERCENT = Decimal("0.015")


def payout_ratio(policy: DividendPolicy) -> Decimal:
    return PAYOUT[policy]


def profit_cut(control: StateControl) -> Decimal:
    """Fração do lucro que o controle de preço tira da empresa."""
    return Decimal(control.percent) * PROFIT_CUT_PER_PERCENT


def profit_after_control(profit: Decimal, control: StateControl) -> Decimal:
    return profit * (1 - profit_cut(control))


def dividend(profit: Decimal, policy: DividendPolicy, control: StateControl) -> Decimal:
    """Provento da estatal fundada: payout da política sobre o lucro depois do corte."""
    return profit_after_control(profit, control) * payout_ratio(policy)


def dividend_factor(policy: DividendPolicy, control: StateControl) -> Decimal:
    """Multiplicador do provento histórico da estatal importada: a história já paga o
    payout Normal, então vale (payout da política ÷ payout Normal) vezes o lucro que sobra."""
    return (payout_ratio(policy) / payout_ratio(DividendPolicy.NORMAL)) * (
        1 - profit_cut(control)
    )
