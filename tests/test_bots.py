"""Bots na sala: um jogador sem pessoa por trás, com carteira própria, que o motor roda a cada pregão."""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from backend import config
from backend.core import repository
from backend.core.dependencies import get_client_id
from backend.core.dto.user import UserDTO
from backend.core.enum import PlayerGrouping, StrategyLogKind
from backend.core.exceptions.http_exceptions import ForbiddenError
from backend.core.player_colors import PLAYER_COLORS
from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.achievements import evaluator
from backend.features.simulation.saved_bots import saved_bots
from backend.features.simulation.simulation_loader import SimulationLoader
from backend.features.statistics.bots import bot_orders, build_bots_report
from backend.features.strategy import catalog
from backend.routes.simulation import simulation_router
from tests.fakes import simulation_settings
from tests.test_simulation_loader import new_user, saved_match, started  # noqa: F401

START = date(2004, 3, 29)


def rules(**changes: object):
    return simulation_settings().model_copy(
        update={"start_date": START, "end_date": date(2004, 12, 31), **changes}
    )


@pytest.fixture
def room(started, monkeypatch: pytest.MonkeyPatch) -> list[str]:  # noqa: F811
    """Sala vazia com as regras no período do histórico de teste."""
    monkeypatch.setattr(SettingsManager, "_settings", rules())
    return started


def person(nickname: str) -> UserDTO:
    user = new_user(nickname)
    UserManager.player_auth(user.client_id)
    return user


def refusal(call, status: int = 409) -> str:
    with pytest.raises(HTTPException) as error:
        call()
    assert error.value.status_code == status
    return str(error.value.detail)


def bot_named(nickname: str) -> UserDTO:
    return next(b for b, _ in UserManager.room_bots() if b.nickname == nickname)


def test_the_catalog_suggests_names_for_every_strategy(room):
    infos = catalog.infos(START, None, catalog.known_tickers())

    assert infos
    assert all(info.bot_names for info in infos)


def test_adding_a_bot_puts_a_new_bot_user_in_the_room(room):
    ana = person("Ana")

    bot = UserManager.add_bot("Tio Patinhas", "buy_and_hold", {})

    assert bot.is_bot
    stored = repository.user.get_by_client_id(bot.client_id)
    assert stored is not None
    assert stored.is_bot
    colors = UserManager.room_colors()
    assert colors[ana.id] != colors[bot.id]
    info = UserManager.room_bot(bot)
    assert info is not None
    assert (info.strategy_name, info.locked) == ("Comprar e segurar", False)
    assert "asset" in info.params
    assert UserManager.room_bot(ana) is None


def test_configuring_a_bot_changes_name_strategy_and_color(room):
    UserManager.add_bot("Tio Patinhas", "buy_and_hold", {}, color="chart-1")

    UserManager.update_bot(
        "Tio Patinhas", "Rentista", "cdi_100", {}, color="chart-5", team=None
    )

    bot = bot_named("Rentista")
    assert UserManager.room_colors()[bot.id] == "chart-5"
    info = UserManager.room_bot(bot)
    assert info is not None
    assert info.strategy_key == "cdi_100"
    renamed = repository.user.get_by_client_id(bot.client_id)
    assert renamed is not None
    assert renamed.nickname == "Rentista"


def test_removing_a_bot_frees_the_color_and_deletes_the_user(room):
    bot = UserManager.add_bot("Tio Patinhas", "buy_and_hold", {}, color="chart-3")

    UserManager.remove_bot("Tio Patinhas")

    assert UserManager.room_bots() == []
    assert bot.id not in UserManager.room_colors()
    assert repository.user.get_by_client_id(bot.client_id) is None
    again = UserManager.add_bot("Outro", "buy_and_hold", {}, color="chart-3")
    assert UserManager.room_colors()[again.id] == "chart-3"


def test_the_eleventh_player_is_refused(room):
    person("Ana")
    for i in range(len(PLAYER_COLORS) - 1):
        UserManager.add_bot(f"Bot {i}", "buy_and_hold", {})

    detail = refusal(
        lambda: UserManager.add_bot("Bot extra", "buy_and_hold", {}), status=423
    )

    assert "A sala está cheia" in detail


def test_a_repeated_name_is_refused_for_people_and_bots(room):
    person("Ana")
    UserManager.add_bot("Rentista", "cdi_100", {})

    assert "Já tem um jogador com esse nome" in refusal(
        lambda: UserManager.add_bot("rentista", "cdi_100", {})
    )
    assert "Já tem um jogador com esse nome" in refusal(
        lambda: UserManager.add_bot("Ana", "cdi_100", {})
    )


def test_a_taken_color_is_refused(room):
    UserManager.add_bot("Um", "cdi_100", {}, color="chart-2")

    assert "Um pegou essa cor antes" in refusal(
        lambda: UserManager.add_bot("Dois", "cdi_100", {}, color="chart-2")
    )


def test_invalid_parameters_are_refused_with_the_strategy_message(room):
    refusal(lambda: UserManager.add_bot("Rompedor", "rsi", {"period": 1}), status=422)


def test_bots_are_spread_over_teams_in_a_team_room(room, monkeypatch):
    monkeypatch.setattr(
        SettingsManager, "_settings", rules(player_grouping=PlayerGrouping.TEAMS)
    )
    UserManager.add_bot("Um", "cdi_100", {}, team=3)

    assert UserManager.room_teams()[bot_named("Um").id] == 3
    refusal(lambda: UserManager.add_bot("Dois", "cdi_100", {}, team=99), status=422)


def test_a_nickname_is_not_owned_by_a_bot(room):
    UserManager.add_bot("Rentista", "cdi_100", {})

    # Bot repete nome de uma partida para outra; a pessoa com esse apelido é só a pessoa
    human = repository.user.create_user(uuid.uuid4(), "Rentista")

    assert not human.is_bot
    found = repository.user.get_by_nickname("Rentista")
    assert found is not None
    assert found.id == human.id
    assert UserManager.has_room_name("rentista")


def test_only_the_host_manages_bots(room):
    ana = person("Ana")
    app = FastAPI()
    app.include_router(simulation_router)
    app.dependency_overrides[get_client_id] = lambda: ana.client_id
    http = TestClient(app)

    answer = http.post(
        "/api/simulation/bots", json={"nickname": "X", "strategy_key": "cdi_100"}
    )

    assert answer.status_code == 403


def test_the_bot_routes_add_configure_and_remove(room):
    host = person(config.toml.host.nickname)
    app = FastAPI()
    app.include_router(simulation_router)
    app.dependency_overrides[get_client_id] = lambda: host.client_id
    http = TestClient(app)

    strategies = http.get("/api/simulation/bots/strategies")
    assert strategies.status_code == 200
    assert {s["key"] for s in strategies.json()} >= {"buy_and_hold", "cdi_100"}

    tickers = http.get("/api/simulation/bots/tickers")
    assert tickers.status_code == 200
    assert tickers.json() == sorted(tickers.json())

    added = http.post(
        "/api/simulation/bots",
        json={"nickname": "O Grafista", "strategy_key": "moving_average_cross"},
    )
    assert added.status_code == 201
    assert added.json()["bot"]["strategy_name"] == "Cruzamento de médias 50/200"

    listed = {p["nickname"]: p for p in http.get("/api/simulation/players").json()}
    assert listed["O Grafista"]["bot"]["locked"] is False
    assert listed[host.nickname]["bot"] is None

    assert (
        http.put(
            "/api/simulation/bots/O Grafista",
            json={"nickname": "Rentista", "strategy_key": "cdi_100"},
        ).status_code
        == 204
    )
    assert http.delete("/api/simulation/bots/Rentista").status_code == 204
    assert http.delete("/api/simulation/bots/Rentista").status_code == 404


def test_starting_the_match_moves_the_bots_out_of_the_room(room):
    ana = person("Ana")
    bot = UserManager.add_bot("Tio Patinhas", "buy_and_hold", {})

    SimulationLoader.create(rules(starting_cash=Decimal(10000)))

    assert UserManager.room_bots() == []
    assert [p.nickname for p in UserManager.list_active_players()] == ["Ana"]
    simulation_id = SimulationManager.get_active_simulation_id()
    players = repository.simulation_player.participants(simulation_id)
    assert {p.nickname for p in players} == {"Ana", "Tio Patinhas"}
    assert repository.simulation_player.colors(simulation_id)[bot.id]
    assert repository.user.get_by_client_id(bot.client_id) is not None
    assert ana.id in repository.simulation_player.colors(simulation_id)


def test_starting_the_match_emits_no_exit_for_the_bots(room, monkeypatch):
    person("Ana")
    UserManager.add_bot("Tio Patinhas", "buy_and_hold", {})
    sent: list[str] = []
    monkeypatch.setattr(
        RealtimeBrokerManager,
        "get_broker",
        lambda: SimpleNamespace(notify=lambda event, *_a, **_k: sent.append(event)),
    )

    SimulationLoader.create(rules())

    assert "player_exit" not in sent
    assert UserManager.room_bots() == []


def test_removing_a_bot_emits_its_exit(room, monkeypatch):
    UserManager.add_bot("Tio Patinhas", "buy_and_hold", {})
    sent: list[str] = []
    monkeypatch.setattr(
        RealtimeBrokerManager,
        "get_broker",
        lambda: SimpleNamespace(notify=lambda event, *_a, **_k: sent.append(event)),
    )

    UserManager.remove_bot("Tio Patinhas")

    assert sent == ["player_exit"]


def test_the_bot_runs_its_strategy_and_receives_the_contribution(room):
    ana = person("Ana")
    bot = UserManager.add_bot("Tio Patinhas", "buy_and_hold", {})
    SimulationLoader.create(
        rules(starting_cash=Decimal(10000), monthly_contribution=Decimal(1000))
    )
    sim = SimulationManager.get_active_simulation()
    assert sim.get_my_strategy(bot).active is not None

    # 29/03 é o primeiro pregão; 01/04 vira o mês e traz o aporte
    for _ in range(5):
        sim.next_tick()

    assert sim.get_portfolio(bot.client_id).variable_income
    # O aporte vale para o bot como para a pessoa
    assert repository.user.get_total_contribution(bot.id) > 0
    assert repository.user.get_total_contribution(
        bot.id
    ) == repository.user.get_total_contribution(ana.id)


def test_a_bot_never_unlocks_achievements(room):
    ana = person("Ana")
    bot = UserManager.add_bot("Tio Patinhas", "buy_and_hold", {})
    SimulationLoader.create(rules())
    sim = SimulationManager.get_active_simulation()

    for _ in range(3):
        sim.next_tick()
    sim.end_match()

    assert repository.achievements.unlocked_codes(bot.id) == set()
    assert repository.achievements.unlocked_codes(ana.id) is not None


def _overview(first_is_bot: bool, in_teams: bool = False):
    players = [
        SimpleNamespace(player_nickname="Robô" if first_is_bot else "Ana", team=1),
        SimpleNamespace(player_nickname="Ana" if first_is_bot else "Robô", team=2),
    ]
    teams = [SimpleNamespace(team=1)] if in_teams else []
    return SimpleNamespace(players=players, teams=teams)


def test_a_bot_in_first_place_gives_the_victory_to_nobody(monkeypatch):
    ana = UserDTO(id=1, client_id=uuid.uuid4(), nickname="Ana")
    robot = UserDTO(id=2, client_id=uuid.uuid4(), nickname="Robô", is_bot=True)
    monkeypatch.setattr(
        evaluator, "build_overview_report", lambda _ids: _overview(first_is_bot=True)
    )

    result = evaluator.match_result(1, [ana, robot], False)

    assert result.winners == frozenset()
    assert result.players_count == 2


def test_a_person_in_first_place_wins_against_the_bot(monkeypatch):
    ana = UserDTO(id=1, client_id=uuid.uuid4(), nickname="Ana")
    robot = UserDTO(id=2, client_id=uuid.uuid4(), nickname="Robô", is_bot=True)
    monkeypatch.setattr(
        evaluator, "build_overview_report", lambda _ids: _overview(first_is_bot=False)
    )

    assert evaluator.match_result(1, [ana, robot], False).winners == {1}


def test_in_teams_the_people_of_the_winning_team_win_with_the_bot(monkeypatch):
    ana = UserDTO(id=1, client_id=uuid.uuid4(), nickname="Ana")
    robot = UserDTO(id=2, client_id=uuid.uuid4(), nickname="Robô", is_bot=True)
    both = SimpleNamespace(
        players=[
            SimpleNamespace(player_nickname="Robô", team=1),
            SimpleNamespace(player_nickname="Ana", team=1),
        ],
        teams=[SimpleNamespace(team=1)],
    )
    monkeypatch.setattr(evaluator, "build_overview_report", lambda _ids: both)

    assert evaluator.match_result(1, [ana, robot], False).winners == {1}


def test_the_bot_log_opens_only_when_the_match_ends(room):
    person("Ana")
    UserManager.add_bot("Tio Patinhas", "buy_and_hold", {})
    SimulationLoader.create(rules())
    sim = SimulationManager.get_active_simulation()
    simulation_id = SimulationManager.get_active_simulation_id()
    for _ in range(3):
        sim.next_tick()

    [during] = build_bots_report([simulation_id])
    assert not during.log_open
    assert during.strategy_name == "Comprar e segurar"
    assert [p.label for p in during.params] == ["Ativo"]
    with pytest.raises(ForbiddenError):
        bot_orders(simulation_id, "Tio Patinhas", 0, 50)

    SimulationManager.clear_simulation()

    [after] = build_bots_report([simulation_id])
    assert after.log_open
    page = bot_orders(simulation_id, "Tio Patinhas", 0, 50)
    assert page.total > 0
    assert {row.kind for row in page.items} == {StrategyLogKind.ORDER}


def test_a_saved_match_brings_its_bots_locked_and_parks_the_new_ones(room):
    ana = person("Ana")
    UserManager.add_bot("O Grafista", "moving_average_cross", {})
    SimulationLoader.create(rules())
    simulation_id = SimulationManager.get_active_simulation_id()
    SimulationManager.clear_simulation()

    # Sala nova: a Ana volta e o host já tinha posto outro bot
    UserManager._active_players.clear()
    UserManager._colors.clear()
    UserManager._bots.clear()
    UserManager.player_auth(ana.client_id)
    novo = UserManager.add_bot("Novato", "cdi_100", {}, color="chart-7")

    UserManager.apply_saved_colors(
        repository.simulation_player.colors(simulation_id),
        repository.simulation_player.teams(simulation_id),
        saved_bots(simulation_id),
    )

    names = {b.nickname for b, _ in UserManager.room_bots()}
    assert names == {"O Grafista"}
    grafista = bot_named("O Grafista")
    info = UserManager.room_bot(grafista)
    assert info is not None
    assert info.locked
    refusal(lambda: UserManager.remove_bot("O Grafista"))
    refusal(lambda: UserManager.update_bot("O Grafista", "X", "cdi_100", {}))
    refusal(lambda: UserManager.add_bot("Outro", "cdi_100", {}))

    UserManager.release_saved_colors()

    assert {b.nickname for b, _ in UserManager.room_bots()} == {"Novato"}
    assert repository.user.get_by_client_id(novo.client_id) is not None


def test_resuming_a_match_brings_the_bot_back_with_the_same_parameters(room):
    person("Ana")
    UserManager.add_bot("O Grafista", "moving_average_cross", {"short_window": 20})
    SimulationLoader.create(rules())
    simulation_id = SimulationManager.get_active_simulation_id()
    sim = SimulationManager.get_active_simulation()
    for _ in range(3):
        sim.next_tick()
    bot = next(
        p for p in repository.simulation_player.participants(simulation_id) if p.is_bot
    )
    before = sim.get_my_strategy(bot).active
    assert before is not None
    SimulationManager.clear_simulation()

    UserManager.apply_saved_colors(
        repository.simulation_player.colors(simulation_id),
        repository.simulation_player.teams(simulation_id),
        saved_bots(simulation_id),
    )
    summary = repository.simulation.get_simulation(simulation_id)
    assert summary is not None
    SimulationLoader.load(summary)

    resumed = SimulationManager.get_active_simulation().get_my_strategy(bot).active
    assert resumed is not None
    assert (resumed.key, resumed.params) == (before.key, before.params)
    assert UserManager.room_bots() == []
