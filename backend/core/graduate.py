"""
As regras do Recém-formado: a escada acadêmica (especialização, mestrado e doutorado), a
curva de carreira que ela estica e a casa dos pais, em Decimal e sem estado.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from backend.core.clt import MONTHS_PER_YEAR, cents
from backend.core.dates import add_months
from backend.core.enum import AcademicStep


@dataclass(frozen=True)
class StepRule:
    """Um degrau: quanto dura, o múltiplo final da carreira e a bolsa que paga no lugar do salário (nula no degrau em que trabalha junto)."""

    months: int
    final_multiple: Decimal
    stipend_rate: Decimal | None


# Os degraus, na ordem em que se sobe; um por vez, cada um exige o anterior concluído
LADDER: tuple[AcademicStep, ...] = (
    AcademicStep.SPECIALIZATION,
    AcademicStep.MASTERS,
    AcademicStep.DOCTORATE,
)

# A graduação não tem regra: já vem concluída, e o múltiplo final dela é o da curva inicial da profissão
STEP_RULES: dict[AcademicStep, StepRule] = {
    AcademicStep.SPECIALIZATION: StepRule(1 * MONTHS_PER_YEAR, Decimal("1.6"), None),
    AcademicStep.MASTERS: StepRule(
        2 * MONTHS_PER_YEAR, Decimal("2.2"), Decimal("0.35")
    ),
    AcademicStep.DOCTORATE: StepRule(
        4 * MONTHS_PER_YEAR, Decimal("3.0"), Decimal("0.5")
    ),
}

# O nome de cada degrau nas mensagens de recusa
STEP_NAMES: dict[AcademicStep, str] = {
    AcademicStep.GRADUATION: "graduação",
    AcademicStep.SPECIALIZATION: "especialização",
    AcademicStep.MASTERS: "mestrado",
    AcademicStep.DOCTORATE: "doutorado",
}

# A mensalidade da especialização, por mês, em fração da renda base do mês
TUITION_RATE = Decimal("0.1")

# Matrícula com o desemprego acima do neutro: a mensalidade cai e a bolsa sobe por esta fração, até o fim do degrau
UNEMPLOYMENT_TUITION_DISCOUNT = Decimal("0.3")
UNEMPLOYMENT_STIPEND_BONUS = Decimal("0.2")

# A casa dos pais: a despesa paga cai esta fração nos primeiros meses na profissão
HOME_DISCOUNT = Decimal("0.4")
HOME_MONTHS = 3 * MONTHS_PER_YEAR


def next_step(completed: list[AcademicStep]) -> AcademicStep | None:
    """O próximo degrau da escada, depois dos concluídos; nulo no topo."""
    for step in LADDER:
        if step not in completed:
            return step
    return None


def months_between(start: date, day: date) -> int:
    """Os meses que passaram de `start` a `day`, pela virada do calendário."""
    return (day.year - start.year) * MONTHS_PER_YEAR + day.month - start.month


def months_done(enrolled_on: date, step: AcademicStep, day: date) -> int:
    """Os meses do degrau que passaram em `day`, de 0 até a duração dele."""
    return min(max(months_between(enrolled_on, day), 0), STEP_RULES[step].months)


def ends_on(enrolled_on: date, step: AcademicStep) -> date:
    """O dia em que os meses do degrau fecham."""
    return add_months(enrolled_on, STEP_RULES[step].months)


def concluded(enrolled_on: date, step: AcademicStep, day: date) -> bool:
    """O degrau conclui na virada do mês em que os meses fecham."""
    return months_done(enrolled_on, step, day) >= STEP_RULES[step].months


def has_stipend(step: AcademicStep) -> bool:
    """Se o degrau paga bolsa no lugar do salário."""
    return STEP_RULES[step].stipend_rate is not None


def tuition_of(base_income: Decimal, discounted: bool) -> Decimal:
    """A mensalidade do mês: a fração da renda base, com o desconto do desemprego quando a matrícula o teve."""
    rate = TUITION_RATE
    if discounted:
        rate *= 1 - UNEMPLOYMENT_TUITION_DISCOUNT
    return cents(base_income * rate)


def stipend_of(base_income: Decimal, step: AcademicStep, discounted: bool) -> Decimal:
    """A bolsa do mês no lugar do salário: a fração da renda base do degrau, com o acréscimo do desemprego quando a matrícula o teve; zero no degrau sem bolsa."""
    rate = STEP_RULES[step].stipend_rate
    if rate is None:
        return Decimal(0)
    if discounted:
        rate *= 1 + UNEMPLOYMENT_STIPEND_BONUS
    return cents(base_income * rate)


def line_multiple(
    start: date,
    start_multiple: Decimal,
    end: date,
    end_multiple: Decimal,
    day: date,
) -> Decimal:
    """O múltiplo em `day` na reta de (`start`, `start_multiple`) a (`end`, `end_multiple`); antes do início vale o inicial e depois do fim, o final."""
    span = (end - start).days
    if span <= 0:
        return end_multiple
    progress = min(max(Decimal((day - start).days) / span, Decimal(0)), Decimal(1))
    return start_multiple + progress * (end_multiple - start_multiple)


def new_curve_end(previous_end: date, today: date, step: AcademicStep) -> date:
    """O fim do trecho novo: o do trecho anterior, ou hoje se ele já passou, mais a duração do degrau."""
    return add_months(max(previous_end, today), STEP_RULES[step].months)


def home_ends_on(career_start: date) -> date:
    """O dia em que o desconto da casa dos pais acaba sozinho."""
    return add_months(career_start, HOME_MONTHS)


def lives_with_parents(
    career_start: date, left_home_on: date | None, day: date
) -> bool:
    """Se o jogador mora com os pais em `day`: nos primeiros anos da profissão e até o dia em que saiu de casa."""
    if left_home_on is not None and day >= left_home_on:
        return False
    return day < home_ends_on(career_start)
