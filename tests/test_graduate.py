"""O Recém-formado: a escada acadêmica e a curva de carreira que ela estica, a mensalidade e a bolsa, o desconto do desemprego, a casa dos pais, a política dos bots e a leitura da página."""

from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core.dates import add_months
from backend.core.dto.profession import (
    CONCLUDE_PREFIX,
    ENROLL_PREFIX,
    LEAVE_HOME,
    STATE_TYPES,
    CltState,
    CompletedStep,
    CurveSegment,
    EnrollStep,
    GraduateState,
    LeaveHome,
    StepEnrollment,
    initial_state,
)
from backend.core.dto.profession_page import GraduateMechanicDTO
from backend.core.enum import AcademicStep, IncomeLoss, MechanicStatus, Profession
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.graduate import (
    HOME_DISCOUNT,
    STEP_RULES,
    concluded,
    lives_with_parents,
    months_done,
    new_curve_end,
    next_step,
    stipend_of,
    tuition_of,
)
from backend.core.life_budget import LifeBudget
from backend.core.professions import (
    REFERENCE_PERSONAL_RATE,
    LifeLevers,
)
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.economy.growth import NEUTRAL_UNEMPLOYMENT
from backend.features.profession.graduate import (
    apply_graduate,
    conclude_step,
    policy_step,
)
from backend.features.profession.mechanics import apply_action
from backend.features.simulation.simulation_loader import SimulationLoader
from backend.features.strategy.bots import resolve_bot
from backend.routes.dependencies import get_client_id
from backend.routes.simulation import simulation_router
from tests.fakes import macro_month
from tests.test_bots import (  # noqa: F401
    person,
    professions_rules,
    refusal,
    room,
    started,
)
from tests.test_clt import turn_of_month
from tests.test_profession_mechanics import life_history, match
from tests.test_professions import SALARY, START
from tests.test_professions import budget as profession_budget

pytestmark = pytest.mark.usefixtures("room")

SPECIALIZATION = AcademicStep.SPECIALIZATION
MASTERS = AcademicStep.MASTERS
DOCTORATE = AcademicStep.DOCTORATE

# O desemprego acima e abaixo do neutro, que decide o desconto da matrícula
HIGH = replace(macro_month(), unemployment=NEUTRAL_UNEMPLOYMENT + Decimal("0.02"))
LOW = replace(macro_month(), unemployment=NEUTRAL_UNEMPLOYMENT - Decimal("0.02"))


def graduate(state: GraduateState | None = None, **levers: Decimal) -> LifeBudget:
    """O orçamento do Recém-formado do teste (salário 5000, despesa 3000) com o estado dado."""
    life = profession_budget(
        Profession.NEW_GRADUATE,
        levers=LifeLevers(**levers) if levers else None,
    )
    return life.with_mechanic_state(lambda: state or GraduateState())


def enrolled(step: AcademicStep, on: date = START, discounted: bool = False):
    return GraduateState(
        current=StepEnrollment(step=step, enrolled_on=on, discounted=discounted)
    )


def after_year(years: int) -> date:
    return add_months(START, 12 * years)


# --- A curva de carreira


def test_without_steps_the_curve_is_the_initial_one():
    life = graduate()
    plain = profession_budget(Profession.NEW_GRADUATE)

    for day in (START, after_year(3), after_year(10), after_year(15)):
        assert life.multiple_on(day) == plain.multiple_on(day)
    assert life.multiple_on(START) == Decimal("0.85")
    assert life.multiple_on(after_year(10) + timedelta(days=5)) == Decimal("1.3")


def test_the_career_counts_from_the_start_in_the_profession():
    entered = after_year(4)
    late = graduate().with_profession_start(entered)

    assert late.multiple_on(entered) == Decimal("0.85")
    assert late.layoff_weight_on(entered) == 2
    assert late.layoff_weight_on(add_months(entered, 120) + timedelta(days=5)) == 1


def test_the_conclusion_opens_a_segment_without_a_jump():
    today = after_year(3)
    before = graduate().multiple_on(today)

    state = conclude_step(
        enrolled(SPECIALIZATION, on=add_months(today, -12)),
        today,
        before,
        graduate().career_end,
    )
    life = graduate(state)

    assert life.multiple_on(today) == before
    assert life.multiple_on(today - timedelta(days=1)) < before
    assert life.multiple_on(add_months(today, 6)) > before
    end = state.curve[-1].end
    assert life.multiple_on(end) == Decimal("1.6")
    assert life.multiple_on(end + timedelta(days=400)) == Decimal("1.6")
    assert [done.step for done in state.completed] == [SPECIALIZATION]
    assert state.current is None


def test_the_new_end_runs_from_the_previous_one_while_it_has_not_passed():
    today = after_year(3)
    life = graduate()

    state = conclude_step(
        enrolled(SPECIALIZATION), today, life.multiple_on(today), life.career_end
    )

    # Ano 10 da curva inicial mais 1 ano da especialização
    assert state.curve[-1].end == add_months(life.career_end, 12)
    assert life.career_end == add_months(START, 120)


def test_the_new_end_runs_from_today_when_the_previous_one_has_passed():
    today = after_year(12)
    life = graduate()

    state = conclude_step(
        enrolled(SPECIALIZATION), today, life.multiple_on(today), life.career_end
    )

    assert state.curve[-1].end == add_months(today, 12)
    assert new_curve_end(life.career_end, today, SPECIALIZATION) == add_months(
        today, 12
    )


def test_the_second_conclusion_stretches_the_end_of_the_first_segment():
    first_day = after_year(2)
    life = graduate()
    state = conclude_step(
        enrolled(SPECIALIZATION),
        first_day,
        life.multiple_on(first_day),
        life.career_end,
    )
    first_end = state.curve[-1].end
    second_day = after_year(3)
    running = graduate(state)
    state = state.model_copy(
        update={
            "current": StepEnrollment(
                step=MASTERS, enrolled_on=first_day, discounted=False
            )
        }
    )

    state = conclude_step(
        state, second_day, running.multiple_on(second_day), life.career_end
    )

    assert state.curve[-1].end == add_months(first_end, 24)
    assert state.curve[-1].end_multiple == Decimal("2.2")
    assert graduate(state).multiple_on(second_day) == running.multiple_on(second_day)
    # O trecho velho segue valendo nos dias antes da conclusão
    assert graduate(state).multiple_on(first_day) == running.multiple_on(first_day)


def test_the_curve_keeps_running_during_a_step():
    life = graduate(enrolled(SPECIALIZATION, on=after_year(1)))
    plain = profession_budget(Profession.NEW_GRADUATE)

    assert life.multiple_on(after_year(1)) == plain.multiple_on(after_year(1))
    assert life.multiple_on(after_year(2)) == plain.multiple_on(after_year(2))


# --- A mensalidade e a bolsa


def test_the_specialization_tuition_is_ten_percent_of_the_base_income():
    life = graduate(enrolled(SPECIALIZATION))
    plain = graduate()

    assert life.tuition_on(START) == Decimal(500)
    assert plain.tuition_on(START) == 0
    assert life.paid_expense_on(START) == plain.paid_expense_on(START) + 500


def test_the_tuition_stays_off_the_goal_and_the_full_expense():
    life = graduate(enrolled(SPECIALIZATION))
    plain = graduate()

    assert life.expense_on(START) == plain.expense_on(START) == Decimal(3000)
    assert life.goal_on(START) == plain.goal_on(START)


def test_the_masters_and_the_doctorate_do_not_charge_tuition():
    assert graduate(enrolled(MASTERS)).tuition_on(START) == 0
    assert graduate(enrolled(DOCTORATE)).tuition_on(START) == 0


def test_the_masters_stipend_replaces_the_whole_salary():
    life = graduate(enrolled(MASTERS))

    exposed, protected = life.income_parts(START)

    assert (exposed, protected) == (Decimal(1750), 0)
    assert life.salary_on(START) == SALARY * Decimal("0.35")
    assert graduate(enrolled(DOCTORATE)).salary_on(START) == SALARY * Decimal("0.5")
    # A especialização trabalha junto: o salário da curva segue inteiro
    assert (
        graduate(enrolled(SPECIALIZATION)).salary_on(START)
        == graduate().salary_on(START)
        == SALARY * Decimal("0.85")
    )


def test_the_stipend_skips_the_income_tax_deviation():
    levers = {"personal_rate": REFERENCE_PERSONAL_RATE + Decimal("0.1")}
    stipend = graduate(enrolled(MASTERS), **levers)
    salary = graduate(enrolled(SPECIALIZATION), **levers)

    assert stipend.net_salary_on(START) == Decimal(1750)
    assert salary.net_salary_on(START) == Decimal("4250") * Decimal("0.9")


def test_the_stipend_has_no_layoff_and_the_risk_comes_back_on_conclusion():
    in_masters = graduate(enrolled(MASTERS))
    assert in_masters.income_loss() is None
    assert graduate(enrolled(DOCTORATE)).income_loss() is None
    assert graduate(enrolled(SPECIALIZATION)).income_loss() is IncomeLoss.LAYOFF

    concluded_state = conclude_step(
        enrolled(MASTERS), after_year(2), Decimal("1.0"), in_masters.career_end
    )
    back = graduate(concluded_state)

    assert back.income_loss() is IncomeLoss.LAYOFF
    # A demissão sorteada tira a renda de quem tem o risco, e a bolsa a poupa
    assert in_masters.net_salary_on(START, income_lost=True) == Decimal(1750)
    assert back.net_salary_on(START, income_lost=True) == 0


def test_the_unemployment_discount_is_fixed_in_the_enrollment():
    cheap = graduate(enrolled(SPECIALIZATION, discounted=True))
    full = graduate(enrolled(SPECIALIZATION, discounted=False))

    assert cheap.tuition_on(START) == Decimal(350)
    assert full.tuition_on(START) == Decimal(500)
    assert graduate(enrolled(MASTERS, discounted=True)).salary_on(START) == Decimal(
        2100
    )
    assert graduate(enrolled(DOCTORATE, discounted=True)).salary_on(START) == Decimal(
        3000
    )
    assert tuition_of(SALARY, True) == Decimal(350)
    assert stipend_of(SALARY, MASTERS, True) == Decimal(2100)
    assert stipend_of(SALARY, SPECIALIZATION, True) == 0


def test_the_enrollment_takes_the_discount_only_above_the_neutral_unemployment():
    state = GraduateState()

    with_discount = apply_graduate(
        state, EnrollStep(kind="enroll_specialization"), START, HIGH
    )
    without = apply_graduate(
        state, EnrollStep(kind="enroll_specialization"), START, LOW
    )

    assert with_discount.current is not None and with_discount.current.discounted
    assert without.current is not None and not without.current.discounted
    assert with_discount.current.enrolled_on == START


# --- As recusas


def test_the_steps_are_climbed_in_order_one_at_a_time():
    state = GraduateState()

    with pytest.raises(ConflictError, match="especialização"):
        apply_graduate(state, EnrollStep(kind="enroll_masters"), START, LOW)
    with pytest.raises(ConflictError, match="especialização"):
        apply_graduate(state, EnrollStep(kind="enroll_doctorate"), START, LOW)

    in_progress = enrolled(SPECIALIZATION)
    with pytest.raises(ConflictError, match="um degrau por vez"):
        apply_graduate(in_progress, EnrollStep(kind="enroll_masters"), START, LOW)
    with pytest.raises(ConflictError, match="um degrau por vez"):
        apply_graduate(
            in_progress, EnrollStep(kind="enroll_specialization"), START, LOW
        )


def test_the_top_of_the_ladder_takes_no_more_enrollments():
    top = GraduateState(
        completed=[
            CompletedStep(step=step, concluded_on=START)
            for step in (SPECIALIZATION, MASTERS, DOCTORATE)
        ]
    )

    assert next_step(top.completed_steps) is None
    with pytest.raises(ConflictError, match="todos os degraus"):
        apply_graduate(top, EnrollStep(kind="enroll_doctorate"), START, LOW)


def test_the_next_step_opens_after_the_previous_one_concludes():
    done = GraduateState(
        completed=[CompletedStep(step=SPECIALIZATION, concluded_on=START)]
    )

    state = apply_graduate(done, EnrollStep(kind="enroll_masters"), START, LOW)

    assert state.current is not None and state.current.step is MASTERS


def test_the_ladder_actions_belong_to_the_new_graduate_only():
    with pytest.raises(ConflictError, match="não é da mecânica"):
        apply_action(
            Profession.CLT, CltState(), EnrollStep(kind="enroll_masters"), START, LOW
        )
    with pytest.raises(ConflictError, match="não é da mecânica"):
        apply_action(Profession.CLT, CltState(), LeaveHome(), START, LOW)


def test_the_enrollment_in_the_simulation_goes_to_the_history(monkeypatch):
    sim, ana = new_graduate(monkeypatch)

    sim.enroll_step(ana, SPECIALIZATION)

    state = state_of(sim, ana)
    assert state.current is not None and state.current.step is SPECIALIZATION
    assert state.current.enrolled_on == sim.get_current_date()
    assert actions_of(sim, ana, f"{ENROLL_PREFIX}specialization")


def test_the_simulation_refuses_the_graduation_the_wrong_order_and_other_professions(
    monkeypatch,
):
    ana, bia = person("Ana"), person("Bia")
    sim = match(monkeypatch)
    sim.switch_profession(ana, Profession.NEW_GRADUATE)

    assert "já vem concluída" in refusal(
        lambda: sim.enroll_step(ana, AcademicStep.GRADUATION)
    )
    assert "próximo degrau" in refusal(lambda: sim.enroll_step(ana, MASTERS))
    sim.enroll_step(ana, SPECIALIZATION)
    assert "um degrau por vez" in refusal(lambda: sim.enroll_step(ana, SPECIALIZATION))
    assert "Só o Recém-formado" in refusal(lambda: sim.enroll_step(bia, SPECIALIZATION))
    assert "Só o Recém-formado" in refusal(lambda: sim.leave_home(bia))


def test_the_months_of_a_step_are_counted_by_the_calendar():
    enrolled_on = date(2004, 3, 15)

    assert months_done(enrolled_on, SPECIALIZATION, date(2004, 3, 31)) == 0
    assert months_done(enrolled_on, SPECIALIZATION, date(2005, 2, 28)) == 11
    assert not concluded(enrolled_on, SPECIALIZATION, date(2005, 2, 28))
    assert concluded(enrolled_on, SPECIALIZATION, date(2005, 3, 1))
    assert months_done(enrolled_on, MASTERS, date(2010, 1, 1)) == 24
    assert concluded(enrolled_on, DOCTORATE, date(2008, 3, 1))
    assert not concluded(enrolled_on, DOCTORATE, date(2008, 2, 28))


# --- A casa dos pais


def test_living_with_the_parents_cuts_the_paid_expense_in_the_first_three_years():
    life = graduate()
    clt = profession_budget(Profession.CLT)

    assert life.expense_discount_on(START) == HOME_DISCOUNT
    assert life.paid_expense_on(START) == Decimal(1800)
    assert clt.paid_expense_on(START) == Decimal(3000)
    # A meta e os imprevistos seguem a despesa cheia
    assert life.expense_on(START) == Decimal(3000)
    assert life.goal_on(START) == clt.goal_on(START)


def test_the_discount_ends_by_itself_after_the_third_year():
    life = graduate()
    deadline = add_months(START, 36)

    assert life.paid_expense_on(deadline - timedelta(days=1)) == Decimal(1800)
    assert life.paid_expense_on(deadline) == Decimal(3000)
    assert lives_with_parents(START, None, deadline - timedelta(days=1))
    assert not lives_with_parents(START, None, deadline)


def test_leaving_home_ends_the_discount_from_that_day():
    left = after_year(1)
    life = graduate(GraduateState(left_home_on=left))

    assert life.paid_expense_on(left - timedelta(days=1)) == Decimal(1800)
    assert life.paid_expense_on(left) == Decimal(3000)
    assert life.paid_expense_on(after_year(2)) == Decimal(3000)


def test_the_discount_counts_from_the_start_in_the_profession():
    entered = after_year(5)
    life = graduate().with_profession_start(entered)

    assert life.paid_expense_on(entered) == Decimal(1800)
    assert life.paid_expense_on(add_months(entered, 36)) == Decimal(3000)


def test_the_discount_stacks_with_the_tuition():
    life = graduate(enrolled(SPECIALIZATION))

    assert life.paid_expense_on(START) == Decimal(1800) + Decimal(500)


def test_leaving_home_has_no_way_back(monkeypatch):
    sim, ana = new_graduate(monkeypatch)

    sim.leave_home(ana)

    assert state_of(sim, ana).left_home_on == sim.get_current_date()
    assert actions_of(sim, ana, LEAVE_HOME)
    assert "já saiu" in refusal(lambda: sim.leave_home(ana))


def test_leaving_home_after_the_deadline_is_refused(monkeypatch):
    sim, ana = new_graduate(monkeypatch)
    sim._current_date = add_months(sim._current_date, 36)

    assert "já acabou" in refusal(lambda: sim.leave_home(ana))


def test_the_state_without_data_is_born_with_the_initial_curve_and_the_home():
    state = initial_state(Profession.NEW_GRADUATE)

    assert STATE_TYPES[Profession.NEW_GRADUATE] is GraduateState
    assert isinstance(state, GraduateState)
    assert state.curve == [] and state.completed == [] and state.current is None
    assert state.left_home_on is None
    # O orçamento sem estado nenhum lido vale o inicial
    bare = profession_budget(Profession.NEW_GRADUATE)
    assert bare.multiple_on(START) == Decimal("0.85")
    assert bare.paid_expense_on(START) == Decimal(1800)


# --- A virada do mês


def test_the_conclusion_at_the_month_turn_opens_the_segment_and_goes_to_the_history(
    monkeypatch,
):
    sim, ana = new_graduate(monkeypatch)
    today = sim.get_current_date()
    save(sim, ana, enrolled(SPECIALIZATION, on=add_months(today, -12)))

    day = turn_of_month(sim)

    state = state_of(sim, ana)
    assert state.current is None
    assert [done.step for done in state.completed] == [SPECIALIZATION]
    assert state.completed[0].concluded_on == day
    [segment] = state.curve
    assert segment.start == day and segment.end_multiple == Decimal("1.6")
    budget = budget_of(sim, ana)
    assert budget.multiple_on(day) == segment.start_multiple
    assert actions_of(sim, ana, f"{CONCLUDE_PREFIX}specialization")


def test_the_step_in_progress_does_not_conclude_before_its_months(monkeypatch):
    sim, ana = new_graduate(monkeypatch)
    today = sim.get_current_date()
    save(sim, ana, enrolled(MASTERS, on=add_months(today, -20)))

    turn_of_month(sim)

    assert state_of(sim, ana).current is not None
    assert state_of(sim, ana).curve == []


def test_the_month_pays_the_stipend_and_charges_the_tuition(monkeypatch):
    sim, ana = new_graduate(monkeypatch)
    save(sim, ana, enrolled(MASTERS, on=sim.get_current_date()))
    cash = sim.get_cash(ana.client_id)

    day = turn_of_month(sim)

    budget = budget_of(sim, ana)
    assert budget.salary_on(day) == (
        budget.base_income_on(day) * Decimal("0.35")
    ).quantize(Decimal("0.01"))
    assert sim.get_cash(ana.client_id) == (
        cash + budget.net_salary_on(day) - budget.paid_expense_on(day)
    )


# --- A política dos bots


def curve_of(life: LifeBudget):
    return life.multiple_on


def test_the_policy_enrolls_when_the_remaining_years_pay_for_the_step():
    life = graduate()

    step = policy_step(
        GraduateState(),
        START,
        add_months(START, 120),
        life.multiple_on,
        life.base_income_on(START),
        Decimal("0.05"),
        False,
        life.career_end,
    )

    assert step is SPECIALIZATION


def test_the_policy_does_not_enroll_near_the_end_of_the_match():
    life = graduate()

    for months in (6, 12, 13, 18):
        assert (
            policy_step(
                GraduateState(),
                START,
                add_months(START, months),
                life.multiple_on,
                life.base_income_on(START),
                Decimal("0.05"),
                False,
                life.career_end,
            )
            is None
        )


def test_the_policy_waits_when_a_step_is_in_progress_or_the_ladder_is_over():
    life = graduate()
    top = GraduateState(
        completed=[
            CompletedStep(step=step, concluded_on=START)
            for step in (SPECIALIZATION, MASTERS, DOCTORATE)
        ]
    )

    for state in (enrolled(SPECIALIZATION), top):
        assert (
            policy_step(
                state,
                START,
                add_months(START, 240),
                life.multiple_on,
                life.base_income_on(START),
                Decimal("0.05"),
                False,
                life.career_end,
            )
            is None
        )


def test_the_policy_weighs_the_salary_that_the_stipend_does_not_pay():
    day = after_year(2)
    life = graduate()
    state = conclude_step(
        enrolled(SPECIALIZATION), day, life.multiple_on(day), life.career_end
    )
    running = graduate(state)

    def pick(years: int):
        return policy_step(
            state,
            day,
            add_months(day, 12 * years),
            running.multiple_on,
            running.base_income_on(day),
            Decimal("0.05"),
            False,
            running.career_end,
        )

    # Com 3 anos de partida o mestrado (2 anos sem salário) não se paga; com muitos, sim
    assert pick(3) is None
    assert pick(30) is MASTERS


def graduate_bot_after_a_month(monkeypatch, years: int) -> GraduateState:
    """A partida de `years` anos com um bot Recém-formado; devolve o estado dele depois da primeira virada de mês."""
    settings = professions_rules(
        unexpected_per_year=0,
        end_date=add_months(professions_rules().start_date, 12 * years),
    )
    monkeypatch.setattr(SettingsManager, "_settings", settings)
    person("Ana")
    bot = UserManager.add_bot(
        "Rentista", resolve_bot("cdi_100", {}, profession=Profession.NEW_GRADUATE)
    )
    SimulationLoader.create(settings)
    sim = SimulationManager.get_active_simulation()
    turn_of_month(sim)
    return state_of(sim, bot)


def test_the_bot_climbs_in_a_long_match(monkeypatch):
    state = graduate_bot_after_a_month(monkeypatch, 20)

    assert state.current is not None and state.current.step is SPECIALIZATION
    # O bot não sai de casa: o desconto acaba sozinho
    assert state.left_home_on is None


def test_the_bot_stays_put_in_a_short_match(monkeypatch):
    state = graduate_bot_after_a_month(monkeypatch, 1)

    assert state.current is None and state.completed == []


# --- A página


def test_the_page_reads_the_default_block(monkeypatch):
    sim, ana = new_graduate(monkeypatch)
    start = sim.get_current_date()
    budget = budget_of(sim, ana)

    block = page_of(sim, ana)

    assert block.status is MechanicStatus.AVAILABLE
    assert block.salary == budget.net_salary_on(start)
    assert block.stipend_income is None
    assert block.career_year == 1
    assert (block.final_multiple, block.next_final_multiple) == (
        Decimal("1.3"),
        Decimal("1.6"),
    )
    assert block.next_step is SPECIALIZATION
    assert block.next_opens_on is None and block.months_left is None
    statuses = [(row.step, row.status) for row in block.steps]
    assert statuses == [
        (AcademicStep.GRADUATION, "done"),
        (SPECIALIZATION, "next"),
        (MASTERS, "later"),
        (DOCTORATE, "later"),
    ]
    graduation = block.steps[0]
    assert graduation.concluded_on == add_months(start, -1)
    assert block.steps[1].tuition == tuition_of(
        budget.base_income_on(start), block.unemployment_discount
    )
    assert block.steps[2].stipend == stipend_of(
        budget.base_income_on(start), MASTERS, block.unemployment_discount
    )
    assert block.home == "with_parents"
    assert block.home_discount == budget.expense_on(start) * HOME_DISCOUNT
    assert block.home_until == add_months(start, 36)
    assert block.full_expense == budget.expense_on(start)
    assert block.neutral_unemployment == NEUTRAL_UNEMPLOYMENT
    assert block.unemployment == sim._macro.latest(start).unemployment


def test_the_page_reads_the_step_in_progress(monkeypatch):
    sim, ana = new_graduate(monkeypatch)
    today = sim.get_current_date()
    enrolled_on = add_months(today, -5)
    save(sim, ana, enrolled(MASTERS, on=enrolled_on, discounted=True))
    budget = budget_of(sim, ana)

    block = page_of(sim, ana)

    assert block.status is MechanicStatus.ACTIVE
    row = next(row for row in block.steps if row.step is MASTERS)
    assert row.status == "current"
    assert (row.months, row.months_done) == (24, 5)
    assert row.ends_on == add_months(enrolled_on, 24)
    assert row.stipend == stipend_of(budget.base_income_on(today), MASTERS, True)
    assert row.unemployment_discount
    assert block.stipend_income == row.stipend
    assert block.next_opens_on == add_months(enrolled_on, 24)
    assert block.months_left == 19
    # O salário da curva segue lido, e a bolsa é a renda do mês
    assert block.stipend_income is not None
    assert block.salary > block.stipend_income
    page = sim.get_profession_page(ana.client_id)
    assert page.header.income == block.stipend_income
    assert page.header.income_loss is None
    assert page.header.layoff_factor is None


def test_the_page_reads_the_home_after_leaving_and_after_the_deadline(monkeypatch):
    sim, ana = new_graduate(monkeypatch)
    sim.leave_home(ana)

    left = page_of(sim, ana)

    assert left.home == "left" and left.home_discount == 0

    sim2_day = add_months(sim.settings.start_date, 40)
    save(sim, ana, GraduateState())
    sim._current_date = sim2_day

    expired = page_of(sim, ana)

    assert expired.home == "expired" and expired.home_discount == 0
    assert expired.career_year == 4


def test_the_page_reads_the_curve_after_a_conclusion(monkeypatch):
    sim, ana = new_graduate(monkeypatch)
    today = sim.get_current_date()
    life = budget_of(sim, ana)
    state = conclude_step(
        enrolled(SPECIALIZATION),
        today,
        life.multiple_on(today),
        life.career_end,
    )
    save(sim, ana, state)

    block = page_of(sim, ana)

    assert block.final_multiple == Decimal("1.6")
    assert block.next_final_multiple == Decimal("2.2")
    assert block.next_step is MASTERS
    done = next(row for row in block.steps if row.step is SPECIALIZATION)
    assert done.status == "done" and done.concluded_on == today
    assert done.tuition is None


def test_the_step_rules_hold_the_ladder_of_the_card():
    assert [
        (s.value, STEP_RULES[s].months, STEP_RULES[s].final_multiple)
        for s in (SPECIALIZATION, MASTERS, DOCTORATE)
    ] == [
        ("SPECIALIZATION", 12, Decimal("1.6")),
        ("MASTERS", 24, Decimal("2.2")),
        ("DOCTORATE", 48, Decimal("3.0")),
    ]
    assert STEP_RULES[SPECIALIZATION].stipend_rate is None
    assert STEP_RULES[MASTERS].stipend_rate == Decimal("0.35")
    assert STEP_RULES[DOCTORATE].stipend_rate == Decimal("0.5")


# --- Apoio


def new_graduate(monkeypatch, **changes):
    """A partida com a Ana de Recém-formada; devolve a partida e a jogadora."""
    ana = person("Ana")
    sim = match(monkeypatch, **changes)
    sim.switch_profession(ana, Profession.NEW_GRADUATE)
    return sim, ana


def state_of(sim, user) -> GraduateState:
    state = sim.get_profession_state(user.client_id).state
    assert isinstance(state, GraduateState)
    return state


def save(sim, user, state: GraduateState) -> None:
    sim._profession_book.save_state(user.id, state)


def budget_of(sim, user) -> LifeBudget:
    return sim._life_budget(sim._life, user.id)


def page_of(sim, user) -> GraduateMechanicDTO:
    mechanic = sim.get_profession_page(user.client_id).mechanic
    assert isinstance(mechanic, GraduateMechanicDTO)
    return mechanic


def actions_of(sim, user, key: str):
    return [r for r in life_history(sim, user.client_id) if r.life_event_key == key]


def test_the_segment_is_a_straight_line_between_its_points():
    segment = CurveSegment(
        start=START,
        start_multiple=Decimal(1),
        end=START + timedelta(days=100),
        end_multiple=Decimal(2),
    )

    assert segment.multiple_on(START) == 1
    assert segment.multiple_on(START + timedelta(days=50)) == Decimal("1.5")
    assert segment.multiple_on(START + timedelta(days=500)) == 2


def test_the_routes_enroll_and_leave_home(monkeypatch):
    sim, ana = new_graduate(monkeypatch)
    app = FastAPI()
    app.include_router(simulation_router)
    app.dependency_overrides[get_client_id] = lambda: ana.client_id
    client = TestClient(app)

    wrong_order = client.post("/api/simulation/enroll-step", json={"step": "MASTERS"})
    enroll = client.post("/api/simulation/enroll-step", json={"step": "SPECIALIZATION"})
    twice = client.post("/api/simulation/enroll-step", json={"step": "SPECIALIZATION"})
    leave = client.post("/api/simulation/leave-home")
    leave_again = client.post("/api/simulation/leave-home")

    assert wrong_order.status_code == 409
    assert enroll.status_code == 200
    assert twice.status_code == 409
    assert leave.status_code == 200
    assert leave_again.status_code == 409
    state = state_of(sim, ana)
    assert state.current is not None and state.left_home_on is not None
