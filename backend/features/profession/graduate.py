"""
A mecânica do Recém-formado: a matrícula nos degraus da escada acadêmica, a conclusão que
abre um trecho novo na curva de carreira, a saída da casa dos pais e a política dos bots.
Só funções do estado, do dia e dos valores da partida.
"""

from collections.abc import Callable
from datetime import date
from decimal import Decimal
from typing import cast

from backend.core.clt import MONTHS_PER_YEAR
from backend.core.dates import add_months
from backend.core.dto.profession import (
    CompletedStep,
    CurveSegment,
    EnrollStep,
    GraduateState,
    LeaveHome,
    MechanicAction,
    MechanicState,
    StepEnrollment,
)
from backend.core.enum import AcademicStep
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.graduate import (
    STEP_NAMES,
    STEP_RULES,
    line_multiple,
    new_curve_end,
    stipend_of,
    tuition_of,
)
from backend.features.economy.growth import NEUTRAL_UNEMPLOYMENT, MacroMonth


def apply_graduate(
    state: MechanicState, action: MechanicAction, day: date, macro: MacroMonth
) -> GraduateState:
    """
    Matricula no degrau seguinte da escada ou sai da casa dos pais. A matrícula com o
    desemprego acima do neutro fixa o desconto da mensalidade e a bolsa maior até o
    degrau acabar.
    """
    state = cast(GraduateState, state)
    if isinstance(action, LeaveHome):
        if state.left_home_on is not None:
            raise ConflictError("Você já saiu da casa dos pais.")
        return state.model_copy(update={"left_home_on": day})
    if not isinstance(action, EnrollStep):
        raise ConflictError("Esta ação não é do Recém-formado.")
    if state.current is not None:
        raise ConflictError(
            f"Você já está matriculado no degrau de {STEP_NAMES[state.current.step]}: um degrau por vez."
        )
    wanted = action.step
    if state.next_step is None:
        raise ConflictError("Você já concluiu todos os degraus da escada.")
    if wanted is not state.next_step:
        raise ConflictError(
            f"O próximo degrau da escada é o de {STEP_NAMES[state.next_step]}: os degraus se sobem na ordem."
        )
    enrollment = StepEnrollment(
        step=wanted,
        enrolled_on=day,
        discounted=macro.unemployment > NEUTRAL_UNEMPLOYMENT,
    )
    return state.model_copy(update={"current": enrollment})


def conclude_step(
    state: GraduateState, day: date, multiple_today: Decimal, initial_end: date
) -> GraduateState:
    """
    O degrau em curso conclui em `day`: nasce um trecho da curva sem salto, de (hoje, o
    múltiplo de hoje na curva em vigor) até (o fim anterior, ou hoje se ele já passou,
    mais a duração do degrau; o múltiplo final do degrau). A matrícula sai do estado.
    """
    enrollment = state.current
    if enrollment is None:
        return state
    previous_end = state.curve[-1].end if state.curve else initial_end
    segment = CurveSegment(
        start=day,
        start_multiple=multiple_today,
        end=new_curve_end(previous_end, day, enrollment.step),
        end_multiple=STEP_RULES[enrollment.step].final_multiple,
    )
    return state.model_copy(
        update={
            "completed": [
                *state.completed,
                CompletedStep(step=enrollment.step, concluded_on=day),
            ],
            "current": None,
            "curve": [*state.curve, segment],
        }
    )


def policy_step(
    state: GraduateState,
    day: date,
    end: date,
    curve_on: Callable[[date], Decimal],
    base_income: Decimal,
    annual_rate: Decimal,
    discounted: bool,
    initial_end: date,
) -> AcademicStep | None:
    """
    O degrau em que o bot se matricula hoje: o seguinte, só se o que sobra da partida o
    paga. O ganho é a diferença entre a curva com o degrau e sem ele, vezes a renda base,
    mês a mês até o fim da partida; o custo são as mensalidades ou o salário que a bolsa
    deixa de pagar. Os dois a valor presente, à `annual_rate`, com a renda base de hoje.
    """
    step = state.next_step
    if state.current is not None or step is None:
        return None
    rule = STEP_RULES[step]
    concluded_on = add_months(day, rule.months)
    if concluded_on >= end:
        return None
    previous_end = state.curve[-1].end if state.curve else initial_end
    start_multiple = curve_on(concluded_on)
    new_end = new_curve_end(previous_end, concluded_on, step)
    monthly = (1 + annual_rate) ** (Decimal(1) / MONTHS_PER_YEAR)
    gain = cost = Decimal(0)
    discount = Decimal(1)
    month = 0
    while (when := add_months(day, month)) <= end:
        if month < rule.months:
            if rule.stipend_rate is None:
                cost += discount * tuition_of(base_income, discounted)
            else:
                salary = curve_on(when) * base_income
                paid = stipend_of(base_income, step, discounted)
                cost += discount * max(salary - paid, Decimal(0))
        else:
            with_step = line_multiple(
                concluded_on, start_multiple, new_end, rule.final_multiple, when
            )
            gain += discount * (with_step - curve_on(when)) * base_income
        month += 1
        discount /= monthly
    return step if gain > cost else None
