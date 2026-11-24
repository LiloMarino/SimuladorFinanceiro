"""O Administrador: a regra do setor, a experiência, a troca de setor, os editais, o concurso para Servidor, a política dos bots e a leitura da página."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest

from backend.core.administrator import (
    EXTRA_EXAM_MONTH,
    SECTORS,
    exam_deadline,
    exam_open,
    exam_passed,
    exam_result_due,
    experience_factor,
    is_senior,
    next_exam_month,
    switch_concluded,
    switch_entry_on,
)
from backend.core.dto.profession import (
    EXAM_FAILED,
    EXAM_PASSED,
    AdministratorState,
    BrokerState,
    EnrollExam,
    SwitchSector,
)
from backend.core.dto.profession_page import AdministratorMechanicDTO
from backend.core.enum import MechanicStatus, Profession
from backend.core.life_budget import LifeBudget
from backend.core.professions import PROFESSIONS
from backend.core.runtime.user_manager import UserManager
from backend.features.government.spending import BASE_SPENDING
from backend.features.profession.administrator import (
    apply_administrator,
    clear_exam,
    conclude_switch,
    grow_experience,
    policy_exam,
    policy_sector,
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

pytestmark = pytest.mark.usefixtures("room")


def administrator_room(monkeypatch, *nicknames: str, **changes):
    """A partida com a Ana no Administrador e os demais jogadores, que a partida precisa conhecer ao nascer; devolve a partida e os jogadores na ordem dos nomes."""
    users = [person(nickname) for nickname in ("Ana", *nicknames)]
    sim = match(monkeypatch, **changes)
    sim.switch_profession(users[0], Profession.ADMINISTRATOR)
    return sim, users


def administrator(monkeypatch, **changes):
    """A partida com a Ana no Administrador; devolve a partida e a jogadora."""
    sim, (ana,) = administrator_room(monkeypatch, **changes)
    return sim, ana


def state_of(sim, user) -> AdministratorState:
    state = sim.get_profession_state(user.client_id).state
    assert isinstance(state, AdministratorState)
    return state


def save(sim, user, **fields) -> None:
    """Grava o estado do Administrador com os campos dados."""
    sim._profession_book.save_state(user.id, AdministratorState(**fields))


def budget_of(sim, user) -> LifeBudget:
    return sim._life_budget(sim._life, user.id)


def page_of(sim, user) -> AdministratorMechanicDTO:
    mechanic = sim.get_profession_page(user.client_id).mechanic
    assert isinstance(mechanic, AdministratorMechanicDTO)
    return mechanic


def at(sim, day: date) -> None:
    """Leva o relógio da partida para `day`, sem rodar os pregões entre."""
    sim._current_date = day


def actions_of(sim, user, key: str):
    return [r for r in life_history(sim, user.client_id) if r.life_event_key == key]


def with_state(budget: LifeBudget, state: AdministratorState) -> LifeBudget:
    return budget.with_mechanic_state(lambda: state)


def close(left: Decimal, right: Decimal) -> bool:
    return abs(left - right) <= Decimal("0.01")


# --- A profissão na lista


def test_the_administrator_is_a_profession_with_the_clt_rule_and_a_mechanic():
    assert PROFESSIONS[Profession.ADMINISTRATOR] == PROFESSIONS[Profession.CLT]
    assert Profession.ADMINISTRATOR in {
        p for p in Profession if p is not Profession.HEIR
    }
    assert set(SECTORS) == {
        Profession.CLT,
        Profession.ENTREPRENEUR,
        Profession.EXPORTER,
        Profession.BANKER,
        Profession.FREELANCER,
        Profession.BROKER,
    }


def test_the_administrator_starts_in_clt_with_no_experience(monkeypatch):
    sim, ana = administrator(monkeypatch)

    state = state_of(sim, ana)

    assert state.sector is Profession.CLT
    assert state.experience == {}
    assert not state.switching and not state.studying


# --- A regra efetiva por setor


@pytest.mark.parametrize(
    "sector",
    [
        Profession.CLT,
        Profession.ENTREPRENEUR,
        Profession.EXPORTER,
        Profession.BANKER,
        Profession.FREELANCER,
        Profession.BROKER,
    ],
)
def test_the_rule_is_the_one_of_the_sector_with_the_multiple_times_the_experience(
    monkeypatch, sector
):
    sim, ana = administrator(monkeypatch)
    budget = budget_of(sim, ana)

    junior = with_state(budget, AdministratorState(sector=sector)).rule
    senior = with_state(
        budget, AdministratorState(sector=sector, experience={sector: 12})
    ).rule

    own = PROFESSIONS[sector]
    assert (junior.tax, junior.loss, junior.driver) == (own.tax, own.loss, own.driver)
    assert junior.income_multiple == own.income_multiple * Decimal("0.85")
    assert senior.income_multiple == own.income_multiple


def test_a_senior_in_clt_earns_what_a_clt_earns(monkeypatch):
    sim, ana = administrator(monkeypatch)
    day = sim.get_current_date()
    budget = budget_of(sim, ana)
    state = AdministratorState(experience={Profession.CLT: 12})

    admin = with_state(budget, state)

    assert admin.net_salary_on(day) == (
        budget.for_profession(Profession.CLT)
        .with_mechanic_state(lambda: state)
        .net_salary_on(day)
    )


def test_the_junior_earns_85_percent_of_the_sector(monkeypatch):
    sim, ana = administrator(monkeypatch)
    day = sim.get_current_date()
    budget = budget_of(sim, ana)
    senior = AdministratorState(experience={Profession.CLT: 12})

    junior = with_state(budget, AdministratorState()).net_salary_on(day)

    assert close(
        junior, with_state(budget, senior).net_salary_on(day) * Decimal("0.85")
    )


def test_the_freelancer_sector_charges_the_reference_price_every_day(monkeypatch):
    sim, ana = administrator(monkeypatch)
    day = sim.get_current_date()
    state = AdministratorState(
        sector=Profession.FREELANCER, experience={Profession.FREELANCER: 12}
    )
    budget = with_state(budget_of(sim, ana), state)

    assert budget.price_on(day) == budget.reference_price_on(day)
    exposed, _ = budget.income_parts(day)
    assert close(exposed, budget.price_on(day) * budget.clients_on(day))


def test_the_broker_sector_pays_the_fixed_part_and_the_split_commission(monkeypatch):
    sim, ana = administrator(monkeypatch)
    day = sim.get_current_date()
    budget = budget_of(sim, ana)
    volume = Decimal("200000000")
    admin = with_state(
        budget,
        AdministratorState(
            sector=Profession.BROKER,
            experience={Profession.BROKER: 12},
            volume=volume,
            brokers=4,
        ),
    )
    broker = budget.for_profession(Profession.BROKER).with_mechanic_state(
        lambda: BrokerState(volume=volume, brokers=4)
    )

    assert admin.broker_commission_on(day).amount > 0
    assert admin.net_salary_on(day) == broker.net_salary_on(day)


def test_the_sector_income_counts_one_more_broker_for_who_is_outside_the_sector(
    monkeypatch,
):
    sim, ana = administrator(monkeypatch)
    day = sim.get_current_date()
    state = AdministratorState(
        experience={Profession.BROKER: 12},
        volume=Decimal("200000000"),
        brokers=3,
    )
    budget = with_state(budget_of(sim, ana), state)

    outside = budget.sector_income_on(Profession.BROKER, day)
    inside = with_state(
        budget_of(sim, ana),
        state.model_copy(update={"sector": Profession.BROKER, "brokers": 4}),
    ).net_salary_on(day)

    assert outside == inside


def test_the_broker_split_counts_the_brokers_and_the_administrators_in_the_sector(
    monkeypatch,
):
    sim, (ana, bia, caio) = administrator_room(monkeypatch, "Bia", "Caio")
    sim.switch_profession(bia, Profession.BROKER)
    sim.switch_profession(caio, Profession.ADMINISTRATOR)
    save(sim, ana, sector=Profession.BROKER)

    day = turn_of_month(sim)
    sim._run_broker_month([ana, bia, caio], day)

    assert state_of(sim, ana).brokers == 2
    assert state_of(sim, caio).brokers == 2
    broker = sim.get_profession_state(bia.client_id).state
    assert isinstance(broker, BrokerState) and broker.brokers == 2


# --- A experiência


def test_the_experience_rises_in_a_line_from_85_to_100_percent_in_twelve_months():
    assert experience_factor(0) == Decimal("0.85")
    assert experience_factor(3) == Decimal("0.8875")
    assert experience_factor(9) == Decimal("0.9625")
    assert experience_factor(12) == Decimal(1)
    assert experience_factor(30) == Decimal(1)


def test_the_senior_starts_at_twelve_months():
    assert not is_senior(11)
    assert is_senior(12)


def test_each_month_adds_one_to_the_current_sector_only():
    state = AdministratorState(experience={Profession.EXPORTER: 5})

    grown = grow_experience(state)

    assert grown.months_in(Profession.CLT) == 1
    assert grown.months_in(Profession.EXPORTER) == 5


def test_the_switch_month_adds_to_no_sector():
    state = AdministratorState(
        switching_to=Profession.EXPORTER, switch_started_on=START
    )

    assert grow_experience(state) == state


def test_the_turn_of_the_month_adds_the_month_worked(monkeypatch):
    sim, ana = administrator(monkeypatch)

    turn_of_month(sim)
    turn_of_month(sim)

    assert state_of(sim, ana).months_in(Profession.CLT) == 2


def test_leaving_a_sector_keeps_its_months_and_coming_back_resumes_them():
    state = AdministratorState(
        sector=Profession.EXPORTER, experience={Profession.EXPORTER: 7}
    )
    leaving = apply_administrator(
        state, SwitchSector(kind="sector_clt"), START, GROWING
    )
    in_clt = conclude_switch(leaving)
    back = conclude_switch(
        apply_administrator(
            in_clt, SwitchSector(kind="sector_exporter"), START, GROWING
        )
    )

    assert in_clt.months_in(Profession.EXPORTER) == 7
    assert back.sector is Profession.EXPORTER
    assert grow_experience(back).months_in(Profession.EXPORTER) == 8


# --- A troca de setor


def test_the_switch_enters_on_the_same_date_of_the_next_month():
    assert switch_entry_on(date(2012, 3, 14)) == date(2012, 4, 14)


def test_the_switch_concludes_on_the_second_turn_of_the_month():
    began = date(2012, 3, 14)

    assert not switch_concluded(began, date(2012, 3, 30))
    assert not switch_concluded(began, date(2012, 4, 2))
    assert switch_concluded(began, date(2012, 5, 2))


def test_the_switch_pays_half_of_the_income_in_the_month_in_between(monkeypatch):
    sim, ana = administrator(monkeypatch)
    day = sim.get_current_date()
    save(sim, ana, experience={Profession.CLT: 12})
    full = budget_of(sim, ana).net_salary_on(day)

    sim.switch_sector(ana, Profession.EXPORTER)

    assert close(budget_of(sim, ana).net_salary_on(day), full / 2)
    assert state_of(sim, ana).switching_to is Profession.EXPORTER


def test_the_switch_pays_the_new_sector_after_the_entry(monkeypatch):
    sim, ana = administrator(monkeypatch)
    sim.switch_sector(ana, Profession.EXPORTER)

    turn_of_month(sim)
    assert state_of(sim, ana).sector is Profession.CLT
    turn_of_month(sim)

    state = state_of(sim, ana)
    assert state.sector is Profession.EXPORTER
    assert state.switching_to is None
    assert state.months_in(Profession.CLT) == 0
    assert state.months_in(Profession.EXPORTER) == 1


def test_the_switch_is_refused_in_the_current_sector_twice_and_for_non_sectors(
    monkeypatch,
):
    sim, ana = administrator(monkeypatch)

    assert "já trabalha" in refusal(lambda: sim.switch_sector(ana, Profession.CLT))
    assert "não existe" in refusal(
        lambda: sim.switch_sector(ana, Profession.PUBLIC_SERVANT)
    )
    sim.switch_sector(ana, Profession.BANKER)
    assert "já está em andamento" in refusal(
        lambda: sim.switch_sector(ana, Profession.EXPORTER)
    )


def test_the_switch_is_refused_outside_the_administrator_and_while_studying(
    monkeypatch,
):
    sim, (ana, bia) = administrator_room(monkeypatch, "Bia")
    at(sim, date(2004, 4, 5))
    sim.enroll_exam(ana)

    assert "Só o Administrador" in refusal(
        lambda: sim.switch_sector(bia, Profession.EXPORTER)
    )
    assert "estudando" in refusal(lambda: sim.switch_sector(ana, Profession.EXPORTER))


# --- Os editais


def test_the_notices_open_in_april_and_october():
    assert exam_open(date(2012, 4, 1), False)
    assert exam_open(date(2012, 10, 31), False)
    assert not exam_open(date(2012, 5, 1), False)
    assert not exam_open(date(2012, 1, 15), True)


def test_the_extra_notice_of_july_needs_the_high_spending():
    july = date(2012, EXTRA_EXAM_MONTH, 10)

    assert exam_open(july, True)
    assert not exam_open(july, False)


def test_the_window_lasts_the_whole_month_and_the_next_one_is_known():
    assert exam_deadline(date(2012, 4, 3)) == date(2012, 4, 30)
    assert next_exam_month(date(2012, 4, 3)) == date(2012, 10, 1)
    assert next_exam_month(date(2012, 10, 3)) == date(2013, 4, 1)
    assert next_exam_month(date(2012, 1, 20)) == date(2012, 4, 1)


def test_the_room_with_government_opens_july_only_when_the_spending_is_above_normal(
    monkeypatch,
):
    sim, _ = administrator(monkeypatch)
    july = date(2004, 7, 6)

    monkeypatch.setattr(
        sim, "_government", SimpleNamespace(spending_on=lambda _day: BASE_SPENDING * 2)
    )
    assert sim._exam_open(july)
    monkeypatch.setattr(
        sim, "_government", SimpleNamespace(spending_on=lambda _day: BASE_SPENDING)
    )
    assert not sim._exam_open(july)
    monkeypatch.setattr(sim, "_government", None)
    assert not sim._exam_open(july)
    assert sim._exam_open(date(2004, 4, 6))


# --- O concurso


def test_the_enrollment_needs_an_open_notice(monkeypatch):
    sim, ana = administrator(monkeypatch)
    at(sim, date(2004, 5, 5))

    assert "edital" in refusal(lambda: sim.enroll_exam(ana))

    at(sim, date(2004, 4, 5))
    sim.enroll_exam(ana)

    assert state_of(sim, ana).exam_enrolled_on == date(2004, 4, 5)


def test_the_enrollment_is_refused_while_switching_and_outside_the_administrator(
    monkeypatch,
):
    sim, (ana, bia) = administrator_room(monkeypatch, "Bia")
    at(sim, date(2004, 4, 5))

    assert "Só o Administrador" in refusal(lambda: sim.enroll_exam(bia))
    sim.switch_sector(ana, Profession.BANKER)
    assert "em andamento" in refusal(lambda: sim.enroll_exam(ana))


def test_the_enrollment_is_refused_twice(monkeypatch):
    sim, ana = administrator(monkeypatch)
    at(sim, date(2004, 4, 5))
    sim.enroll_exam(ana)

    assert "já está inscrito" in refusal(lambda: sim.enroll_exam(ana))


def test_the_study_pays_20_percent_less_and_the_experience_keeps_rising(monkeypatch):
    sim, ana = administrator(monkeypatch)
    day = sim.get_current_date()
    save(sim, ana, experience={Profession.CLT: 12})
    full = budget_of(sim, ana).net_salary_on(day)
    at(sim, date(2004, 4, 5))
    sim.enroll_exam(ana)

    assert close(budget_of(sim, ana).net_salary_on(day), full * Decimal("0.8"))
    assert grow_experience(state_of(sim, ana)).months_in(Profession.CLT) == 13


def test_the_result_comes_on_the_first_turn_after_the_six_months():
    enrolled = date(2012, 4, 15)

    assert not exam_result_due(enrolled, date(2012, 10, 31))
    assert exam_result_due(enrolled, date(2012, 11, 1))


def test_the_draw_is_reproducible_and_near_the_chance():
    day = date(2012, 4, 15)

    assert exam_passed(7, 1, day) == exam_passed(7, 1, day)
    passed = sum(exam_passed(seed, 1, day) for seed in range(2000))
    assert 270 <= passed <= 450


def enrolled_sim(monkeypatch, passed: bool):
    """A partida com a Ana inscrita há 7 meses, com o sorteio já decidido."""
    sim, ana = administrator(monkeypatch)
    enrolled = date(2004, 4, 5)
    save(sim, ana, exam_enrolled_on=enrolled, experience={Profession.CLT: 6})
    sim._random_seed = next(
        seed for seed in range(500) if exam_passed(seed, ana.id, enrolled) is passed
    )
    at(sim, date(2004, 10, 29))
    return sim, ana


def test_the_approval_turns_the_player_into_a_servant(monkeypatch):
    sim, ana = enrolled_sim(monkeypatch, passed=True)

    turn_of_month(sim)

    assert UserManager.get_profession(ana.id) is Profession.PUBLIC_SERVANT
    assert actions_of(sim, ana, EXAM_PASSED)


def test_the_failure_returns_to_the_normal_income_and_frees_a_new_enrollment(
    monkeypatch,
):
    sim, ana = enrolled_sim(monkeypatch, passed=False)

    turn_of_month(sim)

    assert UserManager.get_profession(ana.id) is Profession.ADMINISTRATOR
    state = state_of(sim, ana)
    assert not state.studying
    assert state.months_in(Profession.CLT) >= 6
    assert actions_of(sim, ana, EXAM_FAILED)
    at(sim, date(2004, 4, 5))
    sim.enroll_exam(ana)


def test_the_failure_clears_only_the_enrollment():
    state = AdministratorState(
        sector=Profession.BANKER,
        experience={Profession.BANKER: 4},
        exam_enrolled_on=START,
    )

    assert clear_exam(state) == state.model_copy(update={"exam_enrolled_on": None})


def test_the_enrollment_action_has_the_exam_key():
    state = apply_administrator(AdministratorState(), EnrollExam(), START, GROWING)

    assert state.exam_enrolled_on == START


# --- A política dos bots


def test_the_sector_policy_switches_only_above_20_percent_and_with_the_current_one_senior():
    incomes = {
        Profession.CLT: Decimal(1000),
        Profession.EXPORTER: Decimal(1300),
        Profession.BANKER: Decimal(1100),
    }

    def income_of(sector: Profession) -> Decimal:
        return incomes.get(sector, Decimal(0))

    senior = AdministratorState(experience={Profession.CLT: 12})
    junior = AdministratorState(experience={Profession.CLT: 11})

    assert policy_sector(senior, income_of) is Profession.EXPORTER
    assert policy_sector(junior, income_of) is None
    incomes[Profession.EXPORTER] = Decimal(1200)
    assert policy_sector(senior, income_of) is None
    incomes[Profession.EXPORTER] = Decimal(1201)
    assert policy_sector(senior, income_of) is Profession.EXPORTER


def test_the_sector_policy_waits_while_switching_or_studying():
    def income_of(_sector: Profession) -> Decimal:
        return Decimal(5000)

    experience = {Profession.CLT: 12}

    assert (
        policy_sector(
            AdministratorState(
                experience=experience,
                switching_to=Profession.BANKER,
                switch_started_on=START,
            ),
            lambda s: Decimal(9000) if s is Profession.BANKER else Decimal(1000),
        )
        is None
    )
    assert (
        policy_sector(
            AdministratorState(experience=experience, exam_enrolled_on=START),
            lambda s: Decimal(9000) if s is Profession.BANKER else Decimal(1000),
        )
        is None
    )
    assert policy_sector(AdministratorState(experience=experience), income_of) is None


def test_the_exam_policy_enrolls_when_the_servant_pays_more_and_the_notice_is_open():
    state = AdministratorState()

    assert policy_exam(state, True, Decimal(5001), Decimal(5000))
    assert not policy_exam(state, True, Decimal(5000), Decimal(5000))
    assert not policy_exam(state, False, Decimal(9000), Decimal(5000))
    assert not policy_exam(
        AdministratorState(exam_enrolled_on=START), True, Decimal(9000), Decimal(5000)
    )


def test_the_bot_switches_to_the_better_sector_when_it_is_senior(monkeypatch):
    person("Ana")
    bot = UserManager.add_bot(
        "Robô", resolve_bot("cdi_100", {}, profession=Profession.ADMINISTRATOR)
    )
    sim = match(monkeypatch)
    state = state_of(sim, bot)
    sim._profession_book.save_state(
        bot.id, state.model_copy(update={"experience": {Profession.CLT: 12}})
    )
    day = sim.get_current_date()
    budget = budget_of(sim, bot)
    best = max(
        (s for s in SECTORS if s is not Profession.CLT),
        key=lambda s: budget.sector_income_on(s, day),
    )
    expected = budget.sector_income_on(best, day) > budget.sector_income_on(
        Profession.CLT, day
    ) * Decimal("1.2")

    sim._run_administrator_policy(bot, budget, day)

    assert (state_of(sim, bot).switching_to is best) is expected


def test_the_bot_enrolls_in_the_open_notice_when_the_servant_pays_more(monkeypatch):
    person("Ana")
    bot = UserManager.add_bot(
        "Robô", resolve_bot("cdi_100", {}, profession=Profession.ADMINISTRATOR)
    )
    sim = match(monkeypatch)
    at(sim, date(2004, 4, 5))
    sim._profession_book.save_state(
        bot.id,
        AdministratorState(
            experience={Profession.CLT: 3}, sector=Profession.ENTREPRENEUR
        ),
    )
    day = sim.get_current_date()
    budget = budget_of(sim, bot)
    servant = (
        budget.for_profession(Profession.PUBLIC_SERVANT)
        .with_mechanic_state(lambda: AdministratorState())
        .net_salary_on(day)
    )
    current = budget.sector_income_on(Profession.ENTREPRENEUR, day)

    sim._run_administrator_policy(bot, budget, day)

    assert state_of(sim, bot).studying is (servant > current)


# --- A página


def test_the_page_reads_the_table_with_the_experience_and_the_income_of_each_sector(
    monkeypatch,
):
    sim, ana = administrator(monkeypatch)
    save(sim, ana, experience={Profession.CLT: 12, Profession.EXPORTER: 9})
    day = sim.get_current_date()

    block = page_of(sim, ana)

    assert block.status is MechanicStatus.ACTIVE
    assert [row.sector for row in block.sectors] == list(SECTORS)
    clt = block.sectors[0]
    assert clt.current and clt.senior and clt.level == Decimal(1)
    exporter = next(r for r in block.sectors if r.sector is Profession.EXPORTER)
    assert exporter.months == 9 and not exporter.senior
    assert exporter.level == Decimal("0.9625")
    assert exporter.income == budget_of(sim, ana).sector_income_on(
        Profession.EXPORTER, day
    )
    assert block.senior_months == 12


def test_the_page_reads_the_closed_notice_and_the_next_one(monkeypatch):
    sim, ana = administrator(monkeypatch)
    at(sim, date(2004, 5, 5))

    block = page_of(sim, ana)

    assert block.exam_status == "closed"
    assert block.exam_next_on == date(2004, 10, 1)
    assert block.exam_open_until is None
    assert not block.exam_extra_possible


def test_the_page_reads_the_open_notice_with_the_deadline(monkeypatch):
    sim, ana = administrator(monkeypatch)
    at(sim, date(2004, 4, 5))

    block = page_of(sim, ana)

    assert block.exam_status == "open"
    assert block.exam_open_until == date(2004, 4, 30)
    assert block.exam_pass_chance == Decimal("0.18")
    assert block.exam_study_months == 6


def test_the_page_reads_the_study_in_progress(monkeypatch):
    sim, ana = administrator(monkeypatch)
    at(sim, date(2004, 4, 5))
    sim.enroll_exam(ana)

    block = page_of(sim, ana)

    assert block.exam_status == "studying"
    assert block.exam_result_on == date(2004, 11, 1)
    assert block.exam_income == budget_of(sim, ana).sector_income_on(
        Profession.CLT, sim.get_current_date()
    ) * Decimal("0.8")


def test_the_page_reads_the_switch_in_progress_as_locked(monkeypatch):
    sim, ana = administrator(monkeypatch)
    at(sim, date(2004, 3, 14))
    sim.switch_sector(ana, Profession.EXPORTER)

    block = page_of(sim, ana)

    assert block.status is MechanicStatus.LOCKED
    assert block.switching_to is Profession.EXPORTER
    assert block.switch_entry_on == date(2004, 4, 14)
    assert close(
        block.switch_month_income,
        budget_of(sim, ana).sector_income_on(Profession.CLT, date(2004, 3, 14)) / 2,
    )
