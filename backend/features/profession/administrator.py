"""
A mecânica do Administrador: a troca de setor, o concurso para Servidor, a experiência
por setor e a política dos bots. Só funções do estado, do dia e dos valores da partida.
"""

from collections.abc import Callable
from datetime import date
from decimal import Decimal
from typing import cast

from backend.core.administrator import (
    BOT_SWITCH_GAIN,
    SECTORS,
    exam_result_due,
    is_senior,
    switch_concluded,
)
from backend.core.dto.profession import (
    AdministratorState,
    EnrollExam,
    MechanicAction,
    MechanicState,
    SwitchSector,
)
from backend.core.enum import Profession
from backend.core.exceptions.http_exceptions import ConflictError
from backend.features.economy.growth import MacroMonth


def apply_administrator(
    state: MechanicState, action: MechanicAction, day: date, macro: MacroMonth
) -> AdministratorState:
    """Começa a troca de setor ou a inscrição no concurso, recusando o que a troca e o estudo em andamento não permitem."""
    state = cast(AdministratorState, state)
    if state.switching:
        raise ConflictError("A troca de setor já está em andamento.")
    if isinstance(action, SwitchSector):
        if state.studying:
            raise ConflictError(
                "Você está estudando para o concurso: a troca de setor espera o resultado."
            )
        if action.sector is state.sector:
            raise ConflictError("Você já trabalha neste setor.")
        return state.model_copy(
            update={"switching_to": action.sector, "switch_started_on": day}
        )
    if isinstance(action, EnrollExam):
        if state.studying:
            raise ConflictError("Você já está inscrito no concurso.")
        return state.model_copy(update={"exam_enrolled_on": day})
    raise ConflictError("Esta ação não é do Administrador.")


def switch_due(state: AdministratorState, day: date) -> bool:
    """Se a troca de setor em andamento conclui na virada de `day`."""
    return (
        state.switching_to is not None
        and state.switch_started_on is not None
        and switch_concluded(state.switch_started_on, day)
    )


def conclude_switch(state: AdministratorState) -> AdministratorState:
    """O setor novo passa a ser o atual; a experiência dos dois setores fica guardada."""
    return state.model_copy(
        update={
            "sector": state.switching_to or state.sector,
            "switching_to": None,
            "switch_started_on": None,
        }
    )


def exam_due(state: AdministratorState, day: date) -> bool:
    """Se o resultado do concurso sai na virada de `day`."""
    return state.exam_enrolled_on is not None and exam_result_due(
        state.exam_enrolled_on, day
    )


def clear_exam(state: AdministratorState) -> AdministratorState:
    """O estado depois do resultado reprovado: a renda volta ao normal e uma nova inscrição fica livre."""
    return state.model_copy(update={"exam_enrolled_on": None, "exam_approved": False})


def grow_experience(state: AdministratorState) -> AdministratorState:
    """Soma o mês trabalhado ao setor atual; o mês da troca em andamento não soma em setor nenhum."""
    if state.switching:
        return state
    months = {**state.experience, state.sector: state.months_in(state.sector) + 1}
    return state.model_copy(update={"experience": months})


def with_broker_volume(
    state: AdministratorState, volume: Decimal, brokers: int
) -> AdministratorState:
    """O volume do mês que fechou e quantos dividem a comissão, para o setor Corretor."""
    return state.model_copy(update={"volume": volume, "brokers": brokers})


def policy_sector(
    state: AdministratorState, income_of: Callable[[Profession], Decimal]
) -> Profession | None:
    """
    O bot troca para o setor de maior renda hoje quando ela passa a do atual em mais de
    20% e o atual já está sênior; fora disso fica onde está.
    """
    if (
        state.switching
        or state.studying
        or not is_senior(state.months_in(state.sector))
    ):
        return None
    current = income_of(state.sector)
    best = max(
        (sector for sector in SECTORS if sector is not state.sector),
        key=income_of,
    )
    if income_of(best) > current * (1 + BOT_SWITCH_GAIN):
        return best
    return None


def policy_exam(
    state: AdministratorState, exam_open: bool, servant_income: Decimal, income: Decimal
) -> bool:
    """O bot se inscreve no edital aberto quando a renda do Servidor supera a do setor atual hoje."""
    if state.switching or state.studying or not exam_open:
        return False
    return servant_income > income
