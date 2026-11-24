"""O console do modo debug: o parser, o catálogo, cada comando na partida e as rotas do host."""

# As fixtures da sala vêm do módulo dos testes dela e entram como parâmetro de cada teste
# ruff: noqa: F401

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend import config
from backend.core import repository
from backend.core.administrator import exam_passed
from backend.core.dto.user import UserDTO
from backend.core.enum import (
    CashflowEventType,
    LifeHistoryKind,
    Profession,
    SelicControl,
    VoterValue,
)
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.debug_console import service
from backend.features.debug_console.commands import COMMANDS
from backend.features.profession.administrator import clear_exam
from backend.features.simulation.simulation import Simulation
from backend.features.simulation.simulation_loader import SimulationLoader
from backend.features.strategy.bots import resolve_bot
from backend.routes.debug import debug_router
from backend.routes.dependencies import get_current_user
from tests.test_administrator import administrator_room, at, state_of
from tests.test_bots import person, room, rules
from tests.test_clt import turn_of_month
from tests.test_profession_mechanics import life_history, match
from tests.test_simulation_loader import started

pytestmark = pytest.mark.usefixtures("room")


def run(sim: Simulation, line: str) -> str:
    return service.run(sim, line).message


def cash_of(sim: Simulation, user: UserDTO) -> Decimal:
    return sim._engine.get_cash(user.client_id)


def cashflows(
    sim: Simulation, user: UserDTO
) -> list[tuple[CashflowEventType, Decimal]]:
    """O extrato do jogador: o tipo e o valor de cada lançamento, na ordem."""
    EventManager.flush()
    rows = repository.event.get_cashflow_events(
        sim.settings.id, SimulationManager.get_portfolio_id(user.id)
    )
    return [(row.event_type, row.amount) for row in rows]


@pytest.fixture
def table(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[Simulation, UserDTO, UserDTO, UserDTO]:
    """A partida com a Ana, a Bia e o bot Robo na sala."""
    ana, bia = person("Ana"), person("Bia")
    bot = UserManager.add_bot("Robo", resolve_bot("cdi_100", {}))
    sim = match(monkeypatch)
    return sim, ana, bia, bot


# O parser


def test_the_unknown_command_is_refused(table):
    sim, *_ = table

    with pytest.raises(UnprocessableEntityError, match="desconhecido"):
        run(sim, "fly ana")


def test_the_empty_line_is_refused(table):
    sim, *_ = table

    with pytest.raises(UnprocessableEntityError, match="Digite um comando"):
        run(sim, "   ")


def test_the_missing_argument_names_it_and_shows_the_usage(table):
    sim, *_ = table

    with pytest.raises(UnprocessableEntityError, match=r"<valor>.*add_cash"):
        run(sim, "add_cash ana")


def test_the_extra_argument_is_refused(table):
    sim, *_ = table

    with pytest.raises(UnprocessableEntityError, match="demais"):
        run(sim, "pass_exam ana ana")


def test_the_invalid_number_is_refused(table):
    sim, *_ = table

    with pytest.raises(UnprocessableEntityError, match="não é um"):
        run(sim, "add_cash ana muito")
    with pytest.raises(UnprocessableEntityError, match="não é um"):
        run(sim, "add_cash ana NaN")


def test_the_unclosed_quote_is_refused(table):
    sim, *_ = table

    with pytest.raises(UnprocessableEntityError, match="Aspas"):
        run(sim, 'add_cash "ana 10')


def test_the_unknown_player_is_refused(table):
    sim, *_ = table

    with pytest.raises(NotFoundError, match="Zeca"):
        run(sim, "add_cash Zeca 10")


def test_the_nickname_and_the_decimal_comma_are_accepted(table):
    sim, ana, *_ = table
    before = cash_of(sim, ana)

    run(sim, "ADD_CASH aNa 10,50")

    assert cash_of(sim, ana) == before + Decimal("10.50")


# help


def test_help_lists_every_command_and_explains_one(table):
    sim, *_ = table

    listing = run(sim, "help")
    assert all(name in listing for name in COMMANDS)
    detail = run(sim, "help add_cash")
    assert "<jogador>" in detail and "<valor>" in detail
    with pytest.raises(UnprocessableEntityError, match="desconhecido"):
        run(sim, "help nada")


# O catálogo


def test_the_catalog_lists_the_choices_of_the_match(table):
    sim, *_ = table

    catalog = {c.name: c for c in service.catalog(sim).commands}

    assert set(catalog) == set(COMMANDS)
    players = catalog["add_cash"].arguments[0].choices
    assert players is not None
    assert [c.value for c in players] == ["Ana", "Bia", "Robo"]
    tickers = catalog["give_stock"].arguments[1].choices
    assert tickers is not None and [c.value for c in tickers] == sim.debug_tickers()
    titles = catalog["give_title"].arguments[1].choices
    assert titles
    events = catalog["give_event"].arguments[1].choices
    assert events and "REPAIR" in [c.value for c in events]
    assert catalog["add_cash"].arguments[1].choices is None
    # Sem o Governo & Política a lista de partidos é vazia, não erro
    assert catalog["join_party"].arguments[1].choices == []


# add_cash e set_cash


def test_add_cash_deposits_and_withdraws_through_the_statement(table):
    sim, ana, *_ = table
    before = cash_of(sim, ana)

    run(sim, "add_cash ana 1000")
    run(sim, "add_cash ana -250")

    assert cash_of(sim, ana) == before + 750
    assert cashflows(sim, ana)[-2:] == [
        (CashflowEventType.DEPOSIT, Decimal("1000.00")),
        (CashflowEventType.WITHDRAW, Decimal("250.00")),
    ]


def test_add_cash_refuses_a_negative_balance_and_zero(table):
    sim, ana, *_ = table
    before = cash_of(sim, ana)

    with pytest.raises(ConflictError, match="negativo"):
        run(sim, f"add_cash ana -{before + 1}")
    with pytest.raises(UnprocessableEntityError, match="zero"):
        run(sim, "add_cash ana 0")

    assert cash_of(sim, ana) == before


def test_set_cash_records_the_difference_as_a_deposit_or_a_withdrawal(table):
    sim, ana, *_ = table

    run(sim, "set_cash ana 50000")
    assert cash_of(sim, ana) == 50000
    assert cashflows(sim, ana)[-1][0] is CashflowEventType.DEPOSIT
    run(sim, "set_cash ana 20000")

    assert cash_of(sim, ana) == 20000
    assert cashflows(sim, ana)[-1] == (CashflowEventType.WITHDRAW, Decimal("30000.00"))


def test_set_cash_at_the_same_value_records_nothing(table):
    sim, ana, *_ = table
    run(sim, "set_cash ana 50000")
    entries = len(cashflows(sim, ana))

    run(sim, "set_cash ana 50000")

    assert len(cashflows(sim, ana)) == entries


def test_set_cash_refuses_a_negative_value(table):
    sim, ana, *_ = table
    before = cash_of(sim, ana)

    with pytest.raises(UnprocessableEntityError, match="negativo"):
        run(sim, "set_cash ana -1")

    assert cash_of(sim, ana) == before


# give_stock


def test_give_stock_costs_the_price_of_the_day_and_keeps_the_cash(table):
    sim, ana, *_ = table
    ticker = sim.debug_tickers()[0]
    before = cash_of(sim, ana)

    message = run(sim, f"give_stock ana {ticker.lower()} 10")

    position = sim.get_portfolio_ticker(ana.client_id, ticker)
    assert position.size == 10
    assert position.avg_price > 0
    assert position.total_cost == position.avg_price * 10
    assert cash_of(sim, ana) == before
    assert ticker in message


def test_give_stock_refuses_an_unknown_ticker_and_a_bad_quantity(table):
    sim, ana, *_ = table
    ticker = sim.debug_tickers()[0]

    with pytest.raises(NotFoundError, match="NADA3"):
        run(sim, "give_stock ana nada3 1")
    with pytest.raises(UnprocessableEntityError, match="maior que zero"):
        run(sim, f"give_stock ana {ticker} 0")
    assert sim.get_portfolio_ticker(ana.client_id, ticker).size == 0


# give_title


def test_give_title_applies_in_the_offered_title_without_debiting_the_cash(table):
    sim, ana, *_ = table
    code = next(iter(sim.debug_titles(None)))
    before = cash_of(sim, ana)

    run(sim, f"give_title ana {code} 1500")

    assert cash_of(sim, ana) == before
    held = sim._engine.fixed_broker.get_fixed_positions(ana.client_id)
    assert sum(p.total_applied for p in held.values()) == Decimal(1500)


def test_give_title_refuses_a_title_out_of_the_offer(table):
    sim, *_ = table

    with pytest.raises(NotFoundError, match="zzzzzzzz"):
        run(sim, "give_title ana zzzzzzzz 100")


# give_event


def test_give_event_applies_the_cash_effect_with_the_game_value(table):
    sim, ana, *_ = table
    before = cash_of(sim, ana)

    run(sim, "give_event ana repair")
    after_loss = cash_of(sim, ana)
    run(sim, "give_event ana raffle")

    assert after_loss < before
    assert cash_of(sim, ana) > after_loss
    keys = [
        row.life_event_key
        for row in repository.event.get_cashflow_events(
            sim.settings.id, SimulationManager.get_portfolio_id(ana.id)
        )
    ]
    assert keys[-2:] == ["REPAIR", "RAFFLE"]


def test_give_event_refuses_an_unknown_event(table):
    sim, *_ = table

    with pytest.raises(NotFoundError, match="NADA"):
        run(sim, "give_event ana nada")


def test_give_event_refuses_a_layoff_the_profession_does_not_feel(table):
    sim, ana, *_ = table
    # O Herdeiro vive de renda: a demissão não tira nada dele
    sim.switch_profession(ana, Profession.HEIR)
    assert sim._life_budget(sim._life, ana.id).income_loss() is None

    with pytest.raises(ConflictError, match="não sente a demissão"):
        run(sim, "give_event ana layoff")


def salaries_of(sim: Simulation, user: UserDTO) -> int:
    return sum(
        1 for kind, _ in cashflows(sim, user) if kind is CashflowEventType.SALARY
    )


def test_a_forced_layoff_skips_the_salary_of_the_next_month_only(table):
    sim, ana, bia, _ = table
    sim.next_tick()
    ana_before, bia_before = salaries_of(sim, ana), salaries_of(sim, bia)

    run(sim, "give_event ana layoff")
    turn_of_month(sim)
    assert salaries_of(sim, ana) == ana_before
    assert salaries_of(sim, bia) == bia_before + 1

    turn_of_month(sim)
    assert salaries_of(sim, ana) == ana_before + 1


def test_a_forced_layoff_pays_out_the_fgts_like_a_drawn_one(table):
    sim, ana, *_ = table
    sim.next_tick()
    turn_of_month(sim)
    assert sim.get_profession_state(ana.client_id).state.fgts_balance > 0
    cash = cash_of(sim, ana)

    run(sim, "give_event ana layoff")

    assert sim.get_profession_state(ana.client_id).state.fgts_balance == 0
    assert cash_of(sim, ana) > cash


def test_a_forced_layoff_shows_in_the_life_status_and_in_the_history(table):
    sim, ana, bia, _ = table
    sim.next_tick()
    day = sim.get_current_date()

    run(sim, "give_event ana layoff")

    status = sim.get_life_status(ana.client_id)
    assert status is not None
    assert status.next_salary_skipped_by == day
    other = sim.get_life_status(bia.client_id)
    assert other is not None
    assert other.next_salary_skipped_by is None
    rows = life_history(sim, ana.client_id)
    layoffs = [row for row in rows if row.kind is LifeHistoryKind.LAYOFF]
    assert [row.event_date for row in layoffs] == [day]

    turn_of_month(sim)
    after = sim.get_life_status(ana.client_id)
    assert after is not None
    assert after.salary_skipped_by == day


def test_the_forced_layoff_is_stored_and_read_back_by_the_match(table):
    sim, ana, bia, _ = table
    sim.next_tick()
    day = sim.get_current_date()

    run(sim, "give_event ana layoff")

    assert repository.simulation_player.forced_layoffs(sim.settings.id) == {
        ana.id: (day,)
    }
    sim._forced_layoffs = None
    assert sim._forced_layoffs_of(ana.id) == (day,)
    assert sim._forced_layoffs_of(bia.id) == ()


def test_give_event_refuses_a_match_without_life_events(monkeypatch):
    person("Ana")
    settings = rules()
    monkeypatch.setattr(SettingsManager, "_settings", settings)
    SimulationLoader.create(settings)
    sim = SimulationManager.get_active_simulation()

    with pytest.raises(ConflictError, match="não tem imprevistos"):
        run(sim, "give_event ana repair")


# pass_exam


def test_pass_exam_forces_the_approval_when_the_result_comes(monkeypatch):
    sim, (ana,) = administrator_room(monkeypatch)
    at(sim, date(2004, 4, 5))
    sim.enroll_exam(ana)
    # A semente de uma sala que reprovaria a inscrição
    sim._random_seed = next(
        seed for seed in range(500) if not exam_passed(seed, ana.id, date(2004, 4, 5))
    )
    at(sim, date(2004, 10, 29))

    run(sim, "pass_exam ana")
    turn_of_month(sim)

    assert UserManager.get_profession(ana.id) is Profession.PUBLIC_SERVANT


def test_pass_exam_keeps_the_result_date(monkeypatch):
    sim, (ana,) = administrator_room(monkeypatch)
    at(sim, date(2004, 4, 5))
    sim.enroll_exam(ana)

    run(sim, "pass_exam ana")

    assert UserManager.get_profession(ana.id) is Profession.ADMINISTRATOR
    assert state_of(sim, ana).exam_approved


def test_pass_exam_refuses_without_an_open_enrollment(monkeypatch):
    sim, _ = administrator_room(monkeypatch)

    with pytest.raises(ConflictError, match="inscrição"):
        run(sim, "pass_exam ana")


def test_pass_exam_refuses_who_is_not_an_administrator(table):
    sim, *_ = table

    with pytest.raises(ConflictError, match="não é Administrador"):
        run(sim, "pass_exam ana")


def test_a_failed_exam_clears_the_forced_approval(monkeypatch):
    sim, (ana,) = administrator_room(monkeypatch)
    at(sim, date(2004, 4, 5))
    sim.enroll_exam(ana)
    run(sim, "pass_exam ana")

    sim._profession_book.save_state(ana.id, clear_exam(state_of(sim, ana)))

    assert not state_of(sim, ana).exam_approved


# unban_fund e a partida sem gestoras


def test_unban_fund_refuses_a_match_without_funds(table):
    sim, *_ = table

    with pytest.raises(ConflictError, match="gestoras"):
        run(sim, "unban_fund ana")


def test_the_lifted_ban_is_stored_per_player(table):
    sim, ana, bia, _ = table
    simulation_id = sim.settings.id

    assert (
        repository.simulation_player.founding_ban_lifted_on(simulation_id, ana.id)
        is None
    )
    repository.simulation_player.lift_founding_ban(
        simulation_id, ana.id, date(2004, 5, 3)
    )

    lifted = repository.simulation_player.founding_ban_lifted_on
    assert lifted(simulation_id, ana.id) == date(2004, 5, 3)
    assert lifted(simulation_id, bia.id) is None


# Governo e política


def test_the_government_commands_refuse_a_match_without_government(table):
    sim, *_ = table

    for line in (
        "give_presidency ana",
        "start_impeachment",
        "set_selic 10",
        "join_party ana AAA",
    ):
        with pytest.raises(ConflictError, match="Governo"):
            run(sim, line)


def test_join_party_refuses_a_bot(table):
    sim, *_ = table

    with pytest.raises(ConflictError, match="Bot"):
        run(sim, "join_party robo AAA")


@pytest.fixture
def senate(monkeypatch: pytest.MonkeyPatch):
    """A partida com o Governo & Política e a SELIC do governo, com o partido AAA da Ana."""
    ana, bia = person("Ana"), person("Bia")
    # O Caio fica sem partido
    person("Caio")
    sim = match(
        monkeypatch,
        government_enabled=True,
        selic_control=SelicControl.GOVERNMENT,
        end_date=date(2009, 12, 31),
        first_election=date(2008, 10, 5),
    )
    assert sim._government is not None
    sim._government.found_party(
        ana,
        sim.get_current_date(),
        name="Partido A",
        abbr="AAA",
        color="#dc2626",
        flags=[
            VoterValue.STABILITY,
            VoterValue.DEVELOPMENT,
            VoterValue.SAVER_PROTECTION,
        ],
        contribution=Decimal(0),
    )
    return sim, ana, bia


def test_the_catalog_lists_the_parties_of_players(senate):
    sim, *_ = senate

    catalog = {c.name: c for c in service.catalog(sim).commands}

    choices = catalog["join_party"].arguments[1].choices
    assert choices is not None and [c.value for c in choices] == ["AAA"]


def test_join_party_and_give_presidency_run_through_the_book(senate):
    sim, _, bia = senate

    run(sim, "join_party bia aaa")
    run(sim, "give_presidency bia")

    president = sim._government.president()
    assert president is not None and president.id == bia.id


def test_give_presidency_refuses_who_has_no_party(senate):
    sim, *_ = senate
    with pytest.raises(ConflictError, match="join_party"):
        run(sim, "give_presidency caio")


def test_start_impeachment_refuses_without_a_president(senate):
    sim, *_ = senate

    with pytest.raises(ConflictError, match="presidente"):
        run(sim, "start_impeachment")


def test_set_selic_decides_from_tomorrow(senate):
    sim, *_ = senate
    today = sim.get_current_date()

    run(sim, "set_selic 13,75")

    board = sim._government.state.selic_board
    assert board.selic_on(today + timedelta(days=1)) == Decimal("0.1375")


def test_set_selic_refuses_a_rate_off_the_step(senate):
    sim, *_ = senate

    with pytest.raises(UnprocessableEntityError, match="0,25"):
        run(sim, "set_selic 13,10")


# As rotas


@pytest.fixture
def host_client(table, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    _, ana, *_ = table
    monkeypatch.setattr(config.toml.debug, "enabled", True)
    monkeypatch.setattr(config.toml.host, "nickname", "Ana")
    app = FastAPI()
    app.include_router(debug_router)
    app.dependency_overrides[get_current_user] = lambda: ana
    return TestClient(app)


def test_the_route_runs_the_line_and_returns_the_message(host_client, table):
    sim, ana, *_ = table
    before = cash_of(sim, ana)

    response = host_client.post("/api/debug/command", json={"line": "add_cash ana 100"})

    assert response.status_code == 200
    assert "Ana" in response.json()["message"]
    assert cash_of(sim, ana) == before + 100


def test_the_route_returns_the_refusal_as_a_project_error(host_client):
    response = host_client.post("/api/debug/command", json={"line": "add_cash ana 0"})

    assert response.status_code == 422
    assert "zero" in response.text


def test_the_route_lists_the_catalog(host_client):
    response = host_client.get("/api/debug/commands")

    assert response.status_code == 200
    assert {c["name"] for c in response.json()["commands"]} == set(COMMANDS)


def test_the_routes_are_gone_when_debug_is_off(host_client, monkeypatch):
    monkeypatch.setattr(config.toml.debug, "enabled", False)

    assert host_client.get("/api/debug/commands").status_code == 404
    assert (
        host_client.post("/api/debug/command", json={"line": "help"}).status_code == 404
    )


def test_only_the_host_uses_the_console(host_client, table):
    _, _, bia, _ = table
    app = host_client.app
    assert isinstance(app, FastAPI)
    app.dependency_overrides[get_current_user] = lambda: bia

    assert host_client.get("/api/debug/commands").status_code == 403
    assert (
        host_client.post("/api/debug/command", json={"line": "help"}).status_code == 403
    )


def test_the_route_needs_a_running_match(monkeypatch):
    monkeypatch.setattr(config.toml.debug, "enabled", True)
    monkeypatch.setattr(config.toml.host, "nickname", "Ana")
    ana = person("Ana")
    monkeypatch.setattr(SimulationManager, "_active_simulation", None)
    app = FastAPI()
    app.include_router(debug_router)
    app.dependency_overrides[get_current_user] = lambda: ana
    client = TestClient(app)

    assert client.post("/api/debug/command", json={"line": "help"}).status_code >= 400
