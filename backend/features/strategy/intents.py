from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from backend.core.enum import PrepaymentMode, StrategyAction


@dataclass(frozen=True)
class Intent:
    """O que a estratégia quer fazer; o motor executa e registra o resultado."""

    action: StrategyAction
    # Frase em português para a coluna "Por quê" do registro
    reason: str
    ticker: str | None = None
    quantity: Decimal | None = None
    # Sem limite, a ordem é a mercado
    limit: float | None = None
    order_id: str | None = None
    # Na renda fixa é o título; nas operações de crédito, o empréstimo
    asset_uuid: UUID | None = None
    value: Decimal | None = None
    term_months: int | None = None
    mode: PrepaymentMode | None = None


def buy(
    ticker: str, quantity: Decimal | int, reason: str, limit: float | None = None
) -> Intent:
    return Intent(StrategyAction.BUY, reason, ticker, Decimal(quantity), limit)


def sell(
    ticker: str, quantity: Decimal | int, reason: str, limit: float | None = None
) -> Intent:
    return Intent(StrategyAction.SELL, reason, ticker, Decimal(quantity), limit)


def cancel(order_id: str, reason: str) -> Intent:
    return Intent(StrategyAction.CANCEL, reason, order_id=order_id)


def redeem(asset_uuid: UUID, value: Decimal, reason: str) -> Intent:
    """Resgate de liquidez diária; `value` é o líquido que a estratégia quer no caixa."""
    return Intent(StrategyAction.REDEEM, reason, asset_uuid=asset_uuid, value=value)


def invest(asset_uuid: UUID, value: Decimal, reason: str) -> Intent:
    return Intent(StrategyAction.INVEST, reason, asset_uuid=asset_uuid, value=value)


def take_loan(amount: Decimal, term_months: int, reason: str) -> Intent:
    return Intent(
        StrategyAction.TAKE_LOAN, reason, value=amount, term_months=term_months
    )


def prepay_loan(
    loan_id: UUID, amount: Decimal, mode: PrepaymentMode, reason: str
) -> Intent:
    return Intent(
        StrategyAction.PREPAY_LOAN,
        reason,
        asset_uuid=loan_id,
        value=amount,
        mode=mode,
    )


def payoff_loan(loan_id: UUID, reason: str) -> Intent:
    return Intent(StrategyAction.PAYOFF_LOAN, reason, asset_uuid=loan_id)


def pay_overdue(loan_id: UUID, reason: str) -> Intent:
    return Intent(StrategyAction.PAY_OVERDUE, reason, asset_uuid=loan_id)
