"""O Auxílio: a tarifa social, o depósito do Pé-de-Meia, a liberação a cada 2 anos, o curso técnico, o patrimônio travado, a política dos bots e a leitura da página."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from backend.core.dates import add_months
from backend.core.dto.profession import (
    ENROLL_COURSE,
    SAVINGS_POSTPONED,
    SAVINGS_RELEASED,
    CltState,
    EnrollCourse,
    WelfareState,
)
from backend.core.dto.profession_page import WelfareMechanicDTO
from backend.core.enum import (
    LifeHistoryKind,
    LockedAssetKind,
    MechanicStatus,
    Profession,
)
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.life_budget import LifeBudget, no_mechanic_state
from backend.core.locked_assets import LOCKED_EXITS
from backend.core.professions import PROFESSIONS, LifeLevers
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.user_manager import UserManager
from backend.core.welfare import (
    COURSE_MONTHS,
    course_concluded,
    course_months_done,
    deposit_amount,
    releases_reached,
    spending_factor,
)
from backend.features.profession.mechanics import apply_action
from backend.features.profession.welfare import (
    apply_welfare,
    mark_negative_cash,
    month_turn,
    policy_enroll,
    release,
)
from backend.features.strategy.bots import resolve_bot
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

GROWING = macro_month("0.03")
START = date(2004, 1, 2)
REFERENCE = Decimal("0.015")

pytestmark = pytest.mark.usefixtures("room")


def welfare(monkeypatch, **changes):
    """A partida com a Ana no Auxílio; devolve a partida e a jogadora."""
    ana = person("Ana")
    sim = match(monkeypatch, **changes)
    sim.switch_profession(ana, Profession.WELFARE)
    return sim, ana


def state_of(sim, user) -> WelfareState:
    state = sim.get_profession_state(user.client_id).state
    assert isinstance(state, WelfareState)
    return state


def save(sim, user, **fields) -> None:
    """Grava o estado do Auxílio com os campos dados."""
    sim._profession_book.save_state(user.id, WelfareState(**fields))


def budget_of(sim, user) -> LifeBudget:
    return sim._life_budget(sim._life, user.id)


def page_of(sim, user) -> WelfareMechanicDTO:
    mechanic = sim.get_profession_page(user.client_id).mechanic
    assert isinstance(mechanic, WelfareMechanicDTO)
    return mechanic


def at(sim, day: date) -> None:
    """Leva o relógio da partida para `day`, sem rodar os pregões entre."""
    sim._current_date = day


def actions_of(sim, user, key: str):
    return [r for r in life_history(sim, user.client_id) if r.life_event_key == key]


# --- A tarifa social


def test_only_the_welfare_has_a_discount_on_the_paid_expense():
    discounts = {p: rule.expense_discount for p, rule in PROFESSIONS.items()}

    assert discounts.pop(Profession.WELFARE) == Decimal("0.15")
    assert set(discounts.values()) == {Decimal(0)}


def test_the_paid_expense_has_the_discount_and_the_goal_keeps_the_full_expense(
    monkeypatch,
):
    sim, ana = welfare(monkeypatch)
    budget = budget_of(sim, ana)
    clt = budget.for_profession(Profession.CLT)

    assert budget.expense_on(START) == Decimal(5000)
    assert budget.paid_expense_on(START) == Decimal(4250)
    assert clt.paid_expense_on(START) == Decimal(5000)
    assert budget.goal_on(START) == clt.goal_on(START)


def test_the_month_debits_the_paid_expense_from_the_cash(monkeypatch):
    sim, ana = welfare(monkeypatch)
    before = sim.get_cash(ana.client_id)

    day = turn_of_month(sim)

    budget = budget_of(sim, ana)
    income = budget.net_salary_on(day)
    assert sim.get_cash(ana.client_id) == before + income - Decimal(4250)


def test_the_unexpected_is_charged_by_the_full_expense(monkeypatch):
    sim, ana = welfare(monkeypatch)
    budget = budget_of(sim, ana)
    health = next(e for e in sim.settings.life_events if e.key == "HEALTH")

    assert health.expense_multiple * budget.expense_on(START) == (
        health.expense_multiple * Decimal(5000)
    )
    assert budget.paid_expense_on(START) != budget.expense_on(START)


# --- O depósito do Pé-de-Meia


def test_the_spending_factor_goes_from_half_to_double():
    assert spending_factor(REFERENCE) == 1
    assert spending_factor(Decimal("0.0075")) == Decimal("0.5")
    assert spending_factor(Decimal("0.001")) == Decimal("0.5")
    assert spending_factor(Decimal("0.03")) == 2
    assert spending_factor(Decimal("0.2")) == 2


def test_a_positive_surplus_deposits_twenty_percent_of_it():
    assert deposit_amount(Decimal(600), Decimal(2000), Decimal(1)) == 120


def test_a_zero_or_negative_surplus_deposits_nothing():
    assert deposit_amount(Decimal(0), Decimal(2000), Decimal(1)) == 0
    assert deposit_amount(Decimal(-300), Decimal(2000), Decimal(1)) == 0


def test_the_deposit_stops_at_ten_percent_of_the_net_income():
    assert deposit_amount(Decimal(100000), Decimal(2000), Decimal(1)) == 200


def test_the_factor_multiplies_the_rate_and_the_cap():
    half, double = Decimal("0.5"), Decimal(2)

    assert deposit_amount(Decimal(600), Decimal(2000), half) == 60
    assert deposit_amount(Decimal(600), Decimal(2000), double) == 240
    assert deposit_amount(Decimal(100000), Decimal(2000), half) == 100
    assert deposit_amount(Decimal(100000), Decimal(2000), double) == 400


def test_the_month_turn_deposits_the_surplus_and_keeps_the_wealth_as_the_new_start():
    state = WelfareState(balance=Decimal(1000), month_start_wealth=Decimal(10000))

    turn = month_turn(state, Decimal(10600), Decimal(2000), REFERENCE)

    assert turn.deposit == 120
    assert turn.state.balance == 1120
    assert turn.state.month_start_wealth == 10600


def test_the_first_turn_of_a_saved_match_only_stores_the_start_of_the_month():
    turn = month_turn(WelfareState(), Decimal(10600), Decimal(2000), REFERENCE)

    assert turn.deposit == 0
    assert turn.state.balance == 0
    assert turn.state.month_start_wealth == 10600


def test_the_state_of_a_saved_match_has_no_start_of_the_month():
    assert WelfareState().month_start_wealth is None
    assert WelfareState.model_validate({}).month_start_wealth is None


def test_the_turn_of_the_month_deposits_without_taking_money_from_the_cash(
    monkeypatch,
):
    sim, ana = welfare(monkeypatch)
    cash = sim.get_cash(ana.client_id)
    save(sim, ana, month_start_wealth=cash - Decimal(600))

    day = turn_of_month(sim)

    budget = budget_of(sim, ana)
    assert state_of(sim, ana).balance == 120
    assert sim.get_cash(ana.client_id) == cash + budget.net_salary_on(day) - 4250


def test_the_turn_stores_the_wealth_before_the_salary_as_the_start_of_the_next_month(
    monkeypatch,
):
    sim, ana = welfare(monkeypatch)
    cash = sim.get_cash(ana.client_id)
    save(sim, ana, month_start_wealth=cash)

    turn_of_month(sim)

    assert state_of(sim, ana).month_start_wealth == cash
    assert state_of(sim, ana).balance == 0


def test_a_loss_in_the_month_deposits_nothing(monkeypatch):
    sim, ana = welfare(monkeypatch)
    cash = sim.get_cash(ana.client_id)
    save(sim, ana, balance=Decimal(500), month_start_wealth=cash + Decimal(900))

    turn_of_month(sim)

    assert state_of(sim, ana).balance == 500


def test_the_liquid_wealth_is_cash_and_fixed_income_without_the_shares(monkeypatch):
    sim, ana = welfare(monkeypatch)
    engine = sim._engine
    cash = sim.get_cash(ana.client_id)
    monkeypatch.setattr(engine, "broker", None)
    monkeypatch.setattr(engine, "fixed_market_value", lambda positions: Decimal(700))

    assert engine.liquid_wealth(ana.client_id) == cash + 700


# --- A liberação a cada 2 anos


def test_the_release_dates_come_every_two_years_from_the_start_of_the_match():
    assert releases_reached(START, add_months(START, 23)) == 0
    assert releases_reached(START, add_months(START, 24)) == 1
    assert releases_reached(START, add_months(START, 47)) == 1
    assert releases_reached(START, add_months(START, 48)) == 2


def test_the_release_pays_the_whole_balance_when_the_cash_was_never_negative():
    state = WelfareState(balance=Decimal(1840))

    result = release(state, START, add_months(START, 24))

    assert (result.released, result.postponed) == (1840, False)
    assert result.state.balance == 0
    assert result.state.releases_done == 1


def test_the_release_is_postponed_when_the_cash_was_negative_and_both_cases_clear_the_mark():
    state = WelfareState(balance=Decimal(1840), cash_was_negative=True)

    postponed = release(state, START, add_months(START, 24))

    assert (postponed.released, postponed.postponed) == (0, True)
    assert postponed.state.balance == 1840
    assert postponed.state.cash_was_negative is False
    paid = release(postponed.state, START, add_months(START, 48))
    assert (paid.released, paid.postponed) == (1840, False)
    assert paid.state.releases_done == 2


def test_the_mark_comes_from_a_negative_cash_and_stays_until_the_release():
    state = WelfareState()

    assert mark_negative_cash(state, Decimal(0)) is state
    assert mark_negative_cash(state, Decimal(10)) is state
    marked = mark_negative_cash(state, Decimal("-0.01"))
    assert marked.cash_was_negative
    assert mark_negative_cash(marked, Decimal(500)).cash_was_negative


def test_the_date_pays_the_balance_into_the_cash_and_writes_the_history(monkeypatch):
    sim, ana = welfare(monkeypatch)
    save(sim, ana, balance=Decimal(1840))
    cash = sim.get_cash(ana.client_id)
    at(sim, add_months(sim.settings.start_date, 24))

    sim._run_welfare_savings([ana])

    assert sim.get_cash(ana.client_id) == cash + 1840
    assert state_of(sim, ana).balance == 0
    [row] = actions_of(sim, ana, SAVINGS_RELEASED)
    assert row.amount == 1840
    assert not actions_of(sim, ana, SAVINGS_POSTPONED)
    assert sim.get_portfolio(ana.client_id).locked_value == 0


def test_a_negative_cash_in_the_period_postpones_and_the_next_date_releases(
    monkeypatch,
):
    sim, ana = welfare(monkeypatch)
    start = sim.settings.start_date
    save(sim, ana, balance=Decimal(1840))
    sim._engine.pay_expense(ana.client_id, sim.get_cash(ana.client_id) + 100)
    assert sim.get_cash(ana.client_id) < 0
    at(sim, add_months(start, 12))
    sim._run_welfare_savings([ana])
    assert state_of(sim, ana).cash_was_negative

    sim._engine.pay_salary(ana.client_id, Decimal(5000))
    at(sim, add_months(start, 24))
    sim._run_welfare_savings([ana])

    assert state_of(sim, ana).balance == 1840
    assert not state_of(sim, ana).cash_was_negative
    [postponed] = actions_of(sim, ana, SAVINGS_POSTPONED)
    assert postponed.amount is None
    cash = sim.get_cash(ana.client_id)

    at(sim, add_months(start, 48))
    sim._run_welfare_savings([ana])

    assert state_of(sim, ana).balance == 0
    assert sim.get_cash(ana.client_id) == cash + 1840
    [released] = actions_of(sim, ana, SAVINGS_RELEASED)
    assert released.amount == 1840


def test_a_date_before_the_player_joined_the_profession_is_not_logged(monkeypatch):
    sim, ana = welfare(monkeypatch)
    at(sim, add_months(sim.settings.start_date, 60))

    sim._run_welfare_savings([ana])

    assert state_of(sim, ana).releases_done == 2
    assert not actions_of(sim, ana, SAVINGS_RELEASED)
    assert not actions_of(sim, ana, SAVINGS_POSTPONED)


def test_the_release_is_checked_every_day_not_only_on_the_turn_of_the_month(
    monkeypatch,
):
    sim, ana = welfare(monkeypatch)
    save(sim, ana, balance=Decimal(900))
    release_day = add_months(sim.settings.start_date, 24)
    at(sim, release_day + timedelta(days=15))

    sim._run_welfare_savings([ana])

    assert state_of(sim, ana).balance == 0


# --- O curso técnico


def test_the_enrollment_starts_the_course_today(monkeypatch):
    sim, ana = welfare(monkeypatch)

    sim.enroll_course(ana)

    assert state_of(sim, ana).course_enrolled_on == sim.get_current_date()
    [row] = actions_of(sim, ana, ENROLL_COURSE)
    assert row.kind is LifeHistoryKind.PROFESSION_ACTION


def test_the_enrollment_is_refused_twice_and_outside_the_welfare(monkeypatch):
    ana, bia = person("Ana"), person("Bia")
    sim = match(monkeypatch)
    sim.switch_profession(ana, Profession.WELFARE)
    sim.enroll_course(ana)

    assert "já está matriculado" in refusal(lambda: sim.enroll_course(ana))
    assert "Só quem vive do Auxílio" in refusal(lambda: sim.enroll_course(bia))


def test_the_welfare_action_is_refused_by_other_mechanics():
    with pytest.raises(ConflictError, match="não é da mecânica"):
        apply_action(Profession.CLT, CltState(), EnrollCourse(), START, GROWING)
    with pytest.raises(ConflictError, match="já está matriculado"):
        apply_welfare(
            WelfareState(course_enrolled_on=START), EnrollCourse(), START, GROWING
        )


def test_the_course_halves_the_exposed_income_and_keeps_the_whole_benefit(
    monkeypatch,
):
    sim, ana = welfare(monkeypatch)
    budget = budget_of(sim, ana)
    exposed, benefit = budget.income_parts(START)

    save(sim, ana, course_enrolled_on=START)
    in_course = budget_of(sim, ana)
    half_exposed, same_benefit = in_course.income_parts(START)

    assert half_exposed == exposed / 2
    assert same_benefit == benefit
    assert benefit > 0


def test_the_course_months_are_counted_by_the_calendar():
    enrolled = date(2004, 3, 15)

    assert course_months_done(enrolled, date(2004, 3, 31)) == 0
    assert course_months_done(enrolled, date(2004, 4, 1)) == 1
    assert course_months_done(enrolled, date(2005, 2, 28)) == 11
    assert not course_concluded(enrolled, date(2005, 2, 28))
    assert course_concluded(enrolled, date(2005, 3, 1))
    assert course_months_done(enrolled, date(2007, 1, 1)) == COURSE_MONTHS


def test_the_conclusion_turns_the_player_into_clt_and_the_balance_falls_into_the_cash(
    monkeypatch,
):
    sim, ana = welfare(monkeypatch, end_date=date(2005, 12, 31))
    enrolled = add_months(sim.get_current_date(), -COURSE_MONTHS)
    save(sim, ana, balance=Decimal(1840), course_enrolled_on=enrolled)
    cash = sim.get_cash(ana.client_id)

    day = turn_of_month(sim)

    assert UserManager.get_profession(ana.id) is Profession.CLT
    assert isinstance(sim.get_profession_state(ana.client_id).state, CltState)
    clt = budget_of(sim, ana)
    assert clt.profession is Profession.CLT
    # O primeiro salário do mês já é o de CLT e a despesa paga é a cheia
    assert sim.get_cash(ana.client_id) == (
        cash + 1840 + clt.net_salary_on(day) - clt.expense_on(day)
    )
    switch = [
        r
        for r in life_history(sim, ana.client_id)
        if r.kind is LifeHistoryKind.PROFESSION_SWITCHED
    ][-1]
    assert switch.amount == 1840
    kinds = [a.kind for a in sim.get_portfolio(ana.client_id).locked_assets]
    assert LockedAssetKind.WELFARE_SAVINGS not in kinds


def test_the_course_in_progress_does_not_conclude_before_the_twelve_months(
    monkeypatch,
):
    sim, ana = welfare(monkeypatch)
    enrolled = add_months(sim.get_current_date(), -(COURSE_MONTHS - 2))
    save(sim, ana, course_enrolled_on=enrolled, balance=Decimal(500))

    turn_of_month(sim)

    assert UserManager.get_profession(ana.id) is Profession.WELFARE
    assert state_of(sim, ana).balance >= 500


def test_the_savings_and_the_discount_keep_going_during_the_course(monkeypatch):
    sim, ana = welfare(monkeypatch)
    cash = sim.get_cash(ana.client_id)
    save(
        sim,
        ana,
        balance=Decimal(1000),
        course_enrolled_on=sim.get_current_date(),
        month_start_wealth=cash - Decimal(600),
    )

    day = turn_of_month(sim)

    assert state_of(sim, ana).balance == Decimal(1000) + 120
    budget = budget_of(sim, ana)
    assert budget.paid_expense_on(day) == Decimal(4250)


# --- O patrimônio e a Carteira


def test_the_savings_enter_the_networth_and_the_portfolio_as_a_locked_asset(
    monkeypatch,
):
    sim, ana = welfare(monkeypatch)
    cash = sim.get_cash(ana.client_id)
    save(sim, ana, balance=Decimal(1840))

    portfolio = sim.get_portfolio(ana.client_id)

    assert portfolio.locked_value == 1840
    [asset] = portfolio.locked_assets
    assert asset.kind is LockedAssetKind.WELFARE_SAVINGS
    assert asset.exit_rule == LOCKED_EXITS[LockedAssetKind.WELFARE_SAVINGS].rule
    assert portfolio.total_networth == cash + 1840


def test_the_switch_of_profession_turns_the_whole_balance_into_cash(monkeypatch):
    sim, ana = welfare(monkeypatch)
    save(sim, ana, balance=Decimal(1840))
    cash = sim.get_cash(ana.client_id)

    sim.switch_profession(ana, Profession.PUBLIC_SERVANT)

    assert sim.get_cash(ana.client_id) == cash + 1840
    assert sim.get_portfolio(ana.client_id).locked_value == 0


def test_the_exit_of_the_savings_pays_the_whole_balance_any_day():
    payout = LOCKED_EXITS[LockedAssetKind.WELFARE_SAVINGS].payout

    assert payout(Decimal("1840.00"), None, START) == Decimal("1840.00")


# --- A política dos bots


def test_the_policy_enrolls_with_ten_years_or_more_and_not_below():
    state = WelfareState()

    assert policy_enroll(state, START, date(2014, 1, 2))
    assert policy_enroll(state, START, date(2020, 1, 1))
    assert not policy_enroll(state, START, date(2013, 12, 31))
    assert not policy_enroll(
        WelfareState(course_enrolled_on=START), START, date(2020, 1, 1)
    )


def test_the_bot_enrolls_in_the_first_month_of_a_long_match(monkeypatch):
    end = date(2014, 12, 31)
    monkeypatch.setattr(SettingsManager, "_settings", professions_rules(end_date=end))
    person("Ana")
    bot = UserManager.add_bot(
        "Robô", resolve_bot("cdi_100", {}, profession=Profession.WELFARE)
    )
    sim = match(monkeypatch, end_date=end)

    turn_of_month(sim)

    assert state_of(sim, bot).course_enrolled_on is not None
    assert actions_of(sim, bot, ENROLL_COURSE)


def test_the_bot_does_not_enroll_in_a_short_match(monkeypatch):
    end = date(2006, 12, 31)
    monkeypatch.setattr(SettingsManager, "_settings", professions_rules(end_date=end))
    person("Ana")
    bot = UserManager.add_bot(
        "Robô", resolve_bot("cdi_100", {}, profession=Profession.WELFARE)
    )
    sim = match(monkeypatch, end_date=end)

    turn_of_month(sim)

    assert state_of(sim, bot).course_enrolled_on is None


# --- A página


def test_the_page_reads_the_block_with_the_savings_the_deposit_and_the_discount(
    monkeypatch,
):
    sim, ana = welfare(monkeypatch)
    cash = sim.get_cash(ana.client_id)
    save(
        sim,
        ana,
        balance=Decimal(1840),
        month_start_wealth=cash - Decimal(600),
    )

    block = page_of(sim, ana)

    assert block.status is MechanicStatus.ACTIVE
    assert block.balance == 1840
    assert block.next_release_on == add_months(sim.settings.start_date, 24)
    assert not block.cash_was_negative
    assert (block.surplus, block.deposit, block.deposit_rate) == (
        600,
        120,
        Decimal("0.2"),
    )
    assert block.deposit_cap > block.deposit
    assert block.deposit_factor == spending_factor(
        budget_of(sim, ana).levers_on(sim.get_current_date()).welfare_spending
    )
    assert (block.full_expense, block.paid_expense, block.discount) == (
        5000,
        4250,
        750,
    )
    clt = budget_of(sim, ana).with_mechanic_state(no_mechanic_state)
    assert block.gig_income == clt.exposed_net_on(sim.get_current_date())
    assert block.gig_income_in_course == block.gig_income / 2
    assert block.clt_salary == clt.for_profession(Profession.CLT).net_salary_on(
        sim.get_current_date()
    )
    assert not block.in_course
    assert block.course_months_done is None and block.course_ends_on is None


def test_the_page_reads_the_course_in_progress(monkeypatch):
    sim, ana = welfare(monkeypatch)
    enrolled = add_months(sim.get_current_date(), -7)
    save(sim, ana, balance=Decimal(1840), course_enrolled_on=enrolled)

    block = page_of(sim, ana)

    assert block.in_course
    assert (block.course_months, block.course_months_done) == (12, 7)
    assert block.course_ends_on == add_months(enrolled, 12)
    assert block.gig_income == block_gig_without_course(sim, ana)


def block_gig_without_course(sim, ana) -> Decimal:
    clt = budget_of(sim, ana).with_mechanic_state(no_mechanic_state)
    return clt.exposed_net_on(sim.get_current_date())


def test_the_header_income_does_not_go_negative_with_the_course(monkeypatch):
    sim, ana = welfare(monkeypatch)
    save(sim, ana, course_enrolled_on=sim.get_current_date())

    header = sim.get_profession_page(ana.client_id).header

    assert header.mechanic_income == 0


def test_the_levers_scale_the_benefit_but_not_the_course_cut():
    budget = LifeBudget(
        monthly_salary=Decimal(8000),
        monthly_expense=Decimal(5000),
        withdrawal_rate=Decimal("0.04"),
        inflation_adjusted=False,
        start_date=START,
        profession=Profession.WELFARE,
        levers_on=lambda day: LifeLevers(welfare_spending=Decimal("0.03")),
    )
    course = budget.with_mechanic_state(lambda: WelfareState(course_enrolled_on=START))

    assert course.income_parts(START)[1] == budget.income_parts(START)[1]
    assert course.income_parts(START)[0] == budget.income_parts(START)[0] / 2
