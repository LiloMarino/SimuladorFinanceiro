"""
A mecânica do Aposentado: abrir o saldo, converter parte dele em renda vitalícia, resgatar
parte dele, o rendimento do mês e a política dos bots. Só funções do estado, do dia e da economia.
"""

from datetime import date
from decimal import Decimal
from typing import cast

from backend.core.clt import cents
from backend.core.dto.profession import (
    ConvertPension,
    MechanicAction,
    MechanicState,
    PensionConversion,
    RedeemPension,
    RetireeAction,
    RetireeState,
)
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.pension import (
    BOT_CONVERT_MIN_REAL_RATE,
    BOT_CONVERT_SHARE,
    LOWEST_RATE_MONTHS,
    amount_valid,
    balance_after_month,
    converted_income,
    months_in_plan,
    opening_balance,
)
from backend.features.economy.growth import MacroMonth


def open_balance(
    state: RetireeState, monthly_income: Decimal, day: date
) -> RetireeState:
    """O estado com o saldo aberto em `day`: 24 rendas do mês; o saldo que já abriu fica como está."""
    if state.balance is not None:
        return state
    return state.model_copy(
        update={"balance": opening_balance(monthly_income), "since": day}
    )


def apply_retiree(
    state: MechanicState, action: MechanicAction, day: date, macro: MacroMonth
) -> RetireeState:
    """Converte ou resgata parte do saldo, recusando o que o estado ou o valor não permitem."""
    state = cast(RetireeState, state)
    action = cast(RetireeAction, action)
    if isinstance(action, ConvertPension):
        return convert(state, action, day)
    return redeem(state, cast(RedeemPension, action))


def _checked_amount(state: RetireeState, amount: Decimal) -> Decimal:
    """O valor da ação, que vai de R$ 0,01 até o saldo; o erro de quem pede fora disso."""
    if state.balance is None or not amount_valid(amount, state.balance):
        raise ConflictError("O valor vai de R$ 0,01 até o saldo da previdência.")
    return amount


def convert(state: RetireeState, action: ConvertPension, day: date) -> RetireeState:
    """Tira `amount` do saldo e o guarda como uma parcela de renda vitalícia, fixada ao juro real do dia."""
    amount = _checked_amount(state, action.amount)
    if action.real_rate <= 0:
        raise ConflictError(
            "Com o juro real zerado ou negativo a renda vitalícia não paga: espere o juro real subir."
        )
    part = PensionConversion(
        converted_on=day,
        amount=amount,
        real_rate=action.real_rate,
        income=converted_income(amount, action.real_rate),
    )
    return state.model_copy(
        update={
            "balance": cast(Decimal, state.balance) - amount,
            "conversions": [*state.conversions, part],
        }
    )


def redeem(state: RetireeState, action: RedeemPension) -> RetireeState:
    """Tira `amount` do saldo; o que cai no caixa é o valor menos o IR regressivo (`core.pension.redeem_net`)."""
    amount = _checked_amount(state, action.amount)
    return state.model_copy(update={"balance": cast(Decimal, state.balance) - amount})


def pay_month(state: RetireeState, cdi: Decimal) -> RetireeState:
    """O estado depois do pagamento do mês: o saldo rende o CDI menos 1% ao ano, sem IR."""
    if state.balance is None:
        return state
    return state.model_copy(update={"balance": balance_after_month(state.balance, cdi)})


def converted_amount(state: RetireeState) -> Decimal:
    """A soma dos valores já convertidos em renda."""
    return sum((part.amount for part in state.conversions), Decimal(0))


def converted_real_rate(state: RetireeState) -> Decimal | None:
    """O juro real médio das conversões, ponderado pelo valor de cada uma; nulo sem conversão."""
    total = converted_amount(state)
    if total <= 0:
        return None
    return (
        sum((part.amount * part.real_rate for part in state.conversions), Decimal(0))
        / total
    )


def policy_convert_amount(state: RetireeState, real_rate: Decimal) -> Decimal | None:
    """O bot converte metade do saldo uma vez, no primeiro pagamento com o juro real acima de 6% ao ano; nulo fora disso."""
    if (
        state.conversions
        or state.balance is None
        or real_rate <= BOT_CONVERT_MIN_REAL_RATE
    ):
        return None
    amount = cents(state.balance * BOT_CONVERT_SHARE)
    return amount if amount > 0 else None


def policy_redeem_amount(state: RetireeState, day: date) -> Decimal | None:
    """O bot resgata o saldo inteiro quando o plano chega à faixa da menor alíquota; nulo antes disso ou sem saldo."""
    if state.balance is None or state.since is None or state.balance <= 0:
        return None
    if months_in_plan(state.since, day) < LOWEST_RATE_MONTHS:
        return None
    return state.balance
