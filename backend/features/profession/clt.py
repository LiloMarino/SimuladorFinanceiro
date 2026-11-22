"""
A mecânica do CLT: a hora extra que o jogador liga e desliga, e o que o mês, a recessão
e a demissão fazem com o FGTS e com ela. Só funções do estado, do dia e da economia.
"""

from datetime import date
from decimal import Decimal
from typing import cast

from backend.core.clt import (
    OVERTIME_HEALTH_MULTIPLE,
    OVERTIME_MIN_GROWTH,
    fgts_deposit,
    fgts_payout,
    fgts_yield,
)
from backend.core.dto.profession import (
    OVERTIME_OFF,
    OVERTIME_ON,
    CltState,
    MechanicAction,
    MechanicState,
    SetOvertime,
)
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.professions import DRIVER_CURVES, IncomeDriver
from backend.features.economy.growth import MacroMonth
from backend.features.profession.reserve import Reserve


def overtime_offered(macro: MacroMonth) -> bool:
    """A hora extra só existe com o PIB de 12 meses a partir de zero."""
    return macro.growth >= OVERTIME_MIN_GROWTH


def set_overtime(
    state: MechanicState, action: MechanicAction, day: date, macro: MacroMonth
) -> CltState:
    """Liga ou desliga a hora extra; ligar pede o PIB de 12 meses a partir de zero."""
    state, action = cast(CltState, state), cast(SetOvertime, action)
    if action.enabled == state.overtime:
        raise ConflictError(
            "A hora extra já está ligada."
            if state.overtime
            else "A hora extra já está desligada."
        )
    if action.enabled and not overtime_offered(macro):
        raise ConflictError(
            "A hora extra só existe com o PIB de 12 meses a partir de zero."
        )
    return state.model_copy(update={"overtime": action.enabled})


def overtime_ends_with_recession(state: CltState, macro: MacroMonth) -> bool:
    """A hora extra ligada acaba sozinha quando o PIB de 12 meses fica negativo."""
    return state.overtime and not overtime_offered(macro)


def end_overtime(state: CltState) -> CltState:
    """O estado com a hora extra desligada."""
    return state.model_copy(update={"overtime": False})


def overtime_policy(
    state: MechanicState, day: date, macro: MacroMonth, reserve: Reserve
) -> MechanicAction | None:
    """
    Liga a hora extra com o PIB de 12 meses acima do neutro e o caixa cobrindo um
    imprevisto de saúde em dobro; desliga quando uma das duas condições falha.
    """
    state = cast(CltState, state)
    growing = macro.growth > DRIVER_CURVES[IncomeDriver.GDP].neutral
    covered = reserve.cash >= reserve.health_cost * OVERTIME_HEALTH_MULTIPLE
    wanted = growing and covered
    if wanted == state.overtime:
        return None
    return SetOvertime(kind=OVERTIME_ON if wanted else OVERTIME_OFF)


def after_month(
    state: CltState, gross: Decimal, tr: Decimal, salary_paid: bool
) -> CltState:
    """
    O FGTS na virada do mês: o saldo rende com a TR do mês e, com o salário pago, recebe
    o depósito de 8% do bruto; sem salário a conta só rende.
    """
    balance = state.fgts_balance + fgts_yield(state.fgts_balance, tr)
    if salary_paid:
        balance += fgts_deposit(gross)
    return state.model_copy(update={"fgts_balance": balance})


def after_layoff(state: CltState) -> tuple[CltState, Decimal]:
    """O estado depois da demissão sorteada (conta zerada, hora extra desligada) e o que cai no caixa: o saldo e a multa."""
    return (
        state.model_copy(update={"fgts_balance": Decimal(0), "overtime": False}),
        fgts_payout(state.fgts_balance),
    )
