"""
A mecânica do Auxílio: o depósito mensal do Pé-de-Meia, a liberação do saldo, a matrícula no
curso técnico e a política dos bots. Só funções do estado, do dia e dos valores da partida.
"""

from datetime import date
from decimal import Decimal
from typing import NamedTuple, cast

from backend.core.clt import MONTHS_PER_YEAR
from backend.core.dates import add_months
from backend.core.dto.profession import (
    MechanicAction,
    MechanicState,
    WelfareState,
)
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.welfare import (
    BOT_COURSE_MIN_YEARS,
    deposit_amount,
    releases_reached,
    spending_factor,
)
from backend.features.economy.growth import MacroMonth


class MonthlyDeposit(NamedTuple):
    """O estado depois da virada do mês e o que o governo depositou no Pé-de-Meia."""

    state: WelfareState
    deposit: Decimal


class SavingsRelease(NamedTuple):
    """O que a data de liberação fez: o estado novo, o que caiu no caixa e se a data foi adiada."""

    state: WelfareState
    released: Decimal
    postponed: bool


def apply_welfare(
    state: MechanicState, action: MechanicAction, day: date, macro: MacroMonth
) -> WelfareState:
    """Matricula no curso técnico, recusando quem já está matriculado."""
    state = cast(WelfareState, state)
    if state.in_course:
        raise ConflictError("Você já está matriculado no curso técnico.")
    return state.model_copy(update={"course_enrolled_on": day})


def month_turn(
    state: WelfareState, wealth: Decimal, net_income: Decimal, welfare_spending: Decimal
) -> MonthlyDeposit:
    """
    A virada do mês antes da renda cair: a sobra do mês que fechou é o `wealth` de hoje
    menos o do início dele, e o governo deposita no Pé-de-Meia a fração dela, até o teto.
    O `wealth` de hoje vira o início do mês que abre; sem início guardado não há sobra
    para medir, e a partida salva só guarda o valor na primeira virada.
    """
    start = state.month_start_wealth
    deposit = Decimal(0)
    if start is not None:
        deposit = deposit_amount(
            wealth - start, net_income, spending_factor(welfare_spending)
        )
    return MonthlyDeposit(
        state.model_copy(
            update={
                "balance": state.balance + deposit,
                "month_start_wealth": wealth,
            }
        ),
        deposit,
    )


def mark_negative_cash(state: WelfareState, cash: Decimal) -> WelfareState:
    """O estado com a marca de caixa negativo, quando o caixa do dia está abaixo de zero; a marca fica até a próxima data de liberação."""
    if cash >= 0 or state.cash_was_negative:
        return state
    return state.model_copy(update={"cash_was_negative": True})


def release_due(state: WelfareState, start: date, day: date) -> bool:
    """Se chegou uma data de liberação que o estado ainda não tratou."""
    return releases_reached(start, day) > state.releases_done


def release(state: WelfareState, start: date, day: date) -> SavingsRelease:
    """
    A data de liberação: o saldo inteiro cai no caixa, ou fica para a data seguinte se o
    caixa ficou negativo em algum dia do período. Os dois casos zeram a marca. As datas
    anteriores à entrada do jogador no Auxílio contam como tratadas, sem pagar nem adiar.
    """
    reached = releases_reached(start, day)
    settled = state.model_copy(
        update={"releases_done": reached, "cash_was_negative": False}
    )
    if state.cash_was_negative:
        return SavingsRelease(settled, Decimal(0), True)
    return SavingsRelease(
        settled.model_copy(update={"balance": Decimal(0)}), state.balance, False
    )


def policy_enroll(state: WelfareState, start: date, end: date) -> bool:
    """O bot se matricula no primeiro mês quando a partida tem 10 anos ou mais; fora disso nunca."""
    if state.in_course:
        return False
    return add_months(start, BOT_COURSE_MIN_YEARS * MONTHS_PER_YEAR) <= end
