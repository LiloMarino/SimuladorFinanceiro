"""A base das mecânicas de profissão: estado por jogador, ações, política do bot, troca no meio da partida e histórico por período."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core import repository
from backend.core.dto.life import DEFAULT_LIFE_EVENTS
from backend.core.dto.profession import (
    STATE_TYPES,
    CltState,
    MechanicAction,
    MechanicState,
    ProfessionPeriodDTO,
    initial_state,
)
from backend.core.enum import (
    CashflowEventType,
    LifeHistoryCategory,
    LifeHistoryKind,
    Profession,
)
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.life_budget import LifeBudget
from backend.core.life_events import BOOM_KEY, life_event_label
from backend.core.player_colors import first_free_color
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.economy.growth import MacroMonth
from backend.features.profession import mechanics, policy
from backend.features.profession.mechanics import MECHANICS, Mechanic, apply_action
from backend.features.profession.policy import POLICIES
from backend.features.profession.profession_book import ProfessionBook
from backend.features.profession.reserve import Reserve
from backend.features.simulation.life_history import HistoryPeriod, build_history
from backend.features.simulation.simulation import Simulation
from backend.features.simulation.simulation_loader import SimulationLoader
from backend.features.strategy.bots import resolve_bot
from backend.routes.dependencies import get_client_id
from backend.routes.simulation import simulation_router
from tests.fakes import macro_month, simulation_settings
from tests.test_bots import (  # noqa: F401
    person,
    professions_rules,
    refusal,
    room,
    started,
)
from tests.test_life_history import event
from tests.test_simulation_loader import new_user

pytestmark = pytest.mark.usefixtures("room")


MACRO = macro_month()


class Bonus(MechanicState):
    """Uma mecânica de teste: um contador que a ação sobe e que dobra a renda quando passa de zero."""

    count: int = 0

    @property
    def income_factor(self) -> Decimal:
        return Decimal(2) if self.count else Decimal(1)


class Bump(MechanicAction):
    kind: str = "bump"


class Other(MechanicAction):
    kind: str = "other"


def bump(
    state: MechanicState, action: MechanicAction, day: date, macro: MacroMonth
) -> MechanicState:
    assert isinstance(state, Bonus)
    if state.count >= 3:
        raise ConflictError("O contador já está no limite.")
    return Bonus(count=state.count + 1)


@pytest.fixture
def bonus_for_clt(monkeypatch: pytest.MonkeyPatch) -> None:
    """A mecânica de teste registrada na profissão CLT."""
    monkeypatch.setitem(STATE_TYPES, Profession.CLT, Bonus)
    monkeypatch.setitem(MECHANICS, Profession.CLT, Mechanic(Bump, bump))


def match(monkeypatch: pytest.MonkeyPatch, **changes: object) -> Simulation:
    settings = professions_rules(unexpected_per_year=0, **changes)
    monkeypatch.setattr(SettingsManager, "_settings", settings)
    SimulationLoader.create(settings)
    return SimulationManager.get_active_simulation()


def life_history(sim: Simulation, client_id: UUID):
    """O histórico da vida já com os eventos que o motor ainda tinha na fila."""
    EventManager.flush()
    return sim.get_life_history(client_id)


def test_every_mechanic_has_a_state_type_and_every_policy_a_mechanic():
    assert set(MECHANICS) <= set(STATE_TYPES)
    assert set(POLICIES) <= set(MECHANICS)
    assert mechanics.MECHANICS is MECHANICS and policy.POLICIES is POLICIES


def test_a_profession_without_mechanic_starts_with_the_empty_base_state():
    state = initial_state(Profession.PUBLIC_SERVANT)

    assert type(state) is MechanicState
    assert state.model_dump() == {}
    assert state.income_factor == Decimal(1)


def test_a_profession_without_mechanic_refuses_actions():
    with pytest.raises(ConflictError, match="não tem mecânica"):
        apply_action(
            Profession.PUBLIC_SERVANT, MechanicState(), Bump(), date(2004, 3, 29), MACRO
        )


def test_an_action_of_another_mechanic_is_refused(bonus_for_clt):
    with pytest.raises(ConflictError, match="não é da mecânica"):
        apply_action(Profession.CLT, Bonus(), Other(), date(2004, 3, 29), MACRO)


def test_the_life_budget_reads_the_state_through_the_injected_callable():
    budget = LifeBudget.of(simulation_settings()).for_profession(Profession.CLT)
    day = date(2004, 3, 29)
    base = budget.income_parts(day)

    assert budget.with_mechanic_state(lambda: MechanicState()).income_parts(day) == base

    doubled = budget.with_mechanic_state(lambda: Bonus(count=1)).income_parts(day)
    assert doubled[0] == base[0] * 2


def test_joining_the_match_opens_the_state_and_the_first_period(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)

    states = repository.profession.states(sim.settings.id)
    periods = repository.profession.periods(sim.settings.id)

    state = states[ana.id]
    assert isinstance(state, CltState)
    assert not state.overtime
    assert periods[ana.id] == [
        ProfessionPeriodDTO(profession=Profession.CLT, start=sim.settings.start_date)
    ]


def test_the_state_is_saved_typed_and_comes_back_typed(bonus_for_clt, monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)

    sim.apply_profession_action(ana, Bump())
    sim.apply_profession_action(ana, Bump())

    assert repository.profession.states(sim.settings.id)[ana.id] == Bonus(count=2)
    # O estado que volta do banco é o mesmo que a partida carrega ao ser retomada
    assert ProfessionBook(sim.settings.id).state_of(ana.id, Profession.CLT) == Bonus(
        count=2
    )


def test_the_action_service_validates_persists_and_records_the_event(
    bonus_for_clt, monkeypatch
):
    ana = person("Ana")
    sim = match(monkeypatch)

    for _ in range(3):
        sim.apply_profession_action(ana, Bump())
    with pytest.raises(ConflictError, match="limite"):
        sim.apply_profession_action(ana, Bump())

    assert sim.get_profession_state(ana.client_id).state == Bonus(count=3)
    rows = [
        r
        for r in life_history(sim, ana.client_id)
        if r.kind is LifeHistoryKind.PROFESSION_ACTION
    ]
    assert [r.life_event_key for r in rows] == ["bump"] * 3
    assert {r.category for r in rows} == {LifeHistoryCategory.PROFESSION}
    assert all(r.amount is None or r.amount == 0 for r in rows)


def test_the_state_changes_the_income_of_the_month(bonus_for_clt, monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)
    life = LifeBudget.of(sim.settings)
    day = sim.get_current_date()
    before = sim._life_budget(life, ana.id).income_parts(day)

    sim.apply_profession_action(ana, Bump())

    after = sim._life_budget(life, ana.id).income_parts(day)
    assert after[0] == before[0] * 2


def test_the_policy_acts_only_for_bots_and_only_on_the_month_turn(
    bonus_for_clt, monkeypatch
):
    ana = person("Ana")
    bot = UserManager.add_bot(
        "Robô", resolve_bot("cdi_100", {}, profession=Profession.CLT)
    )
    monkeypatch.setitem(
        POLICIES, Profession.CLT, lambda state, day, macro, reserve: Bump()
    )
    sim = match(monkeypatch)
    months: set[tuple[int, int]] = set()

    for _ in range(12):
        sim.next_tick()
        today = sim.get_current_date()
        months.add((today.year, today.month))

    robot = sim.get_profession_state(bot.client_id).state
    human = sim.get_profession_state(ana.client_id).state
    assert isinstance(robot, Bonus) and isinstance(human, Bonus)
    assert human.count == 0
    # Uma ação por virada de mês, e o contador trava em 3 pela regra da mecânica de teste
    assert robot.count == min(len(months), 3)


def test_the_policy_gets_the_state_the_day_the_macro_and_the_reserve_of_the_month(
    bonus_for_clt, monkeypatch
):
    person("Ana")
    UserManager.add_bot("Robô", resolve_bot("cdi_100", {}, profession=Profession.CLT))
    seen: list[tuple[MechanicState, date, object, Reserve]] = []

    def record(state, day, macro, reserve):
        seen.append((state, day, macro, reserve))

    monkeypatch.setitem(POLICIES, Profession.CLT, record)
    sim = match(monkeypatch)
    sim.next_tick()

    assert seen
    state, day, macro, reserve = seen[0]
    assert state == Bonus()
    assert day == sim.settings.start_date
    assert hasattr(macro, "unemployment")
    assert reserve.cash > 0
    assert reserve.health_cost == 2 * sim.settings.monthly_expense


def test_switching_in_the_middle_keeps_cash_and_starting_capital(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)
    for _ in range(4):
        sim.next_tick()
    cash = sim.get_cash(ana.client_id)
    locked = sim.get_portfolio(ana.client_id).locked_value
    portfolio = repository.portfolio.ids(sim.settings.id)[ana.id]
    capital = repository.portfolio.starting_cash([portfolio])

    sim.switch_profession(ana, Profession.PUBLIC_SERVANT)

    # O FGTS acumulado cai no caixa pela regra de saída; o resto do caixa fica
    assert locked > 0
    assert sim.get_cash(ana.client_id) == cash + locked
    assert repository.portfolio.starting_cash([portfolio]) == capital
    assert UserManager.get_profession(ana.id) is Profession.PUBLIC_SERVANT
    assert (
        sim.get_profession_state(ana.client_id).profession is Profession.PUBLIC_SERVANT
    )
    assert (
        repository.simulation_player.professions(sim.settings.id)[ana.id]
        is Profession.PUBLIC_SERVANT
    )


def test_switching_writes_the_period_and_the_zero_money_history_event(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)
    for _ in range(4):
        sim.next_tick()
    day = sim.get_current_date()

    sim.switch_profession(ana, Profession.PUBLIC_SERVANT)

    assert repository.profession.periods(sim.settings.id)[ana.id] == [
        ProfessionPeriodDTO(profession=Profession.CLT, start=sim.settings.start_date),
        ProfessionPeriodDTO(profession=Profession.PUBLIC_SERVANT, start=day),
    ]
    [row] = [
        r
        for r in life_history(sim, ana.client_id)
        if r.kind is LifeHistoryKind.PROFESSION_SWITCHED
    ]
    assert row.event_date == day
    assert row.life_event_key == Profession.PUBLIC_SERVANT.value
    assert row.cash_after == sim.get_cash(ana.client_id)


def test_the_switch_starts_the_new_profession_on_its_initial_state(
    bonus_for_clt, monkeypatch
):
    ana = person("Ana")
    sim = match(monkeypatch)
    sim.apply_profession_action(ana, Bump())

    sim.switch_profession(ana, Profession.PUBLIC_SERVANT)
    sim.switch_profession(ana, Profession.CLT)

    assert sim.get_profession_state(ana.client_id).state == Bonus(count=0)


def test_the_switch_refuses_the_party_bound_destination_the_same_profession_and_rooms_without_professions(
    monkeypatch,
):
    ana = person("Ana")
    sim = match(
        monkeypatch,
        government_enabled=True,
        end_date=date(2009, 12, 31),
        first_election=date(2008, 10, 5),
    )

    assert "partido" in refusal(
        lambda: sim.switch_profession(ana, Profession.COMMISSIONED)
    )
    assert "já exerce" in refusal(lambda: sim.switch_profession(ana, Profession.CLT))
    assert repository.profession.periods(sim.settings.id)[ana.id] == [
        ProfessionPeriodDTO(profession=Profession.CLT, start=sim.settings.start_date)
    ]


def test_the_switch_is_refused_in_a_match_without_professions(monkeypatch):
    ana = person("Ana")
    settings = simulation_settings().model_copy(
        update={"start_date": date(2004, 3, 29), "end_date": date(2004, 12, 31)}
    )
    monkeypatch.setattr(SettingsManager, "_settings", settings)
    SimulationLoader.create(settings)
    sim = SimulationManager.get_active_simulation()

    assert "profissões" in refusal(
        lambda: sim.switch_profession(ana, Profession.PUBLIC_SERVANT)
    )


def test_the_late_player_opens_the_first_period_on_the_day_of_joining(monkeypatch):
    person("Ana")
    sim = match(monkeypatch)
    for _ in range(3):
        sim.next_tick()
    late = new_user("Duda")
    UserManager.player_auth(late.client_id)

    UserManager.join_match(
        late.client_id,
        first_free_color(set(UserManager.room_colors().values())),
        profession=Profession.PUBLIC_SERVANT,
    )

    periods = repository.profession.periods(sim.settings.id)[late.id]
    assert periods == [
        ProfessionPeriodDTO(
            profession=Profession.PUBLIC_SERVANT, start=sim.get_current_date()
        )
    ]
    assert type(sim.get_profession_state(late.client_id).state) is MechanicState


def test_the_history_reads_the_profession_of_each_date():
    clt = HistoryPeriod(date(2004, 1, 1), Profession.CLT, None)
    entrepreneur = HistoryPeriod(date(2004, 7, 1), Profession.ENTREPRENEUR, None)

    rows = build_history(
        [
            event(
                date(2004, 3, 1), CashflowEventType.UNEXPECTED_INCOME, "8000", BOOM_KEY
            ),
            event(
                date(2004, 9, 1), CashflowEventType.UNEXPECTED_INCOME, "8000", BOOM_KEY
            ),
        ],
        DEFAULT_LIFE_EVENTS,
        periods=[clt, entrepreneur],
    )

    assert [r.label for r in rows] == [
        life_event_label(BOOM_KEY, "Boa fase da profissão", Profession.CLT),
        life_event_label(BOOM_KEY, "Boa fase da profissão", Profession.ENTREPRENEUR),
    ]


def test_the_route_returns_the_state_of_who_asks(bonus_for_clt, monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)
    sim.apply_profession_action(ana, Bump())
    app = FastAPI()
    app.include_router(simulation_router)
    app.dependency_overrides[get_client_id] = lambda: ana.client_id

    response = TestClient(app).get("/api/simulation/profession-state")

    assert response.status_code == 200
    assert response.json() == {"profession": "CLT", "state": {"count": 1}}
    assert SimulationManager.get_active_simulation() is sim
