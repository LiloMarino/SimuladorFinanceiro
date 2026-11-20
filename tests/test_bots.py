"""Bots na sala: um jogador sem pessoa por trás, com carteira própria, que o motor roda a cada pregão."""

from __future__ import annotations

import uuid
from datetime import date
from decimal import ROUND_CEILING, Decimal
from types import SimpleNamespace

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from backend import config
from backend.core import repository
from backend.core.dto.user import UserDTO
from backend.core.enum import (
    GameType,
    PlayerGrouping,
    Profession,
    SalaryMode,
    StrategyLogKind,
)
from backend.core.exceptions.http_exceptions import ForbiddenError
from backend.core.life_budget import LifeBudget
from backend.core.player_colors import PLAYER_COLORS
from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import BotConfig, UserManager
from backend.features.achievements import evaluator
from backend.features.simulation.saved_bots import saved_bots
from backend.features.simulation.simulation_loader import SimulationLoader
from backend.features.statistics.bots import bot_orders, build_bots_report
from backend.features.strategy import catalog
from backend.features.strategy.bots import resolve_bot
from backend.routes.dependencies import get_client_id
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
    infos = catalog.infos(
        START,
        None,
        catalog.known_tickers(),
        funds_enabled=True,
        government_enabled=True,
    )

    assert infos
    assert all(info.bot_names for info in infos)


def test_the_fund_strategy_is_in_the_catalog_only_with_the_funds_expansion(room):
    with_funds = catalog.infos(
        START,
        None,
        catalog.known_tickers(),
        funds_enabled=True,
        government_enabled=False,
    )
    without_funds = catalog.infos(
        START,
        None,
        catalog.known_tickers(),
        funds_enabled=False,
        government_enabled=False,
    )

    assert "fund_quotas" in {info.key for info in with_funds}
    assert "fund_quotas" not in {info.key for info in without_funds}


def test_a_room_without_funds_refuses_the_fund_strategy_for_bots(room, monkeypatch):
    monkeypatch.setattr(SettingsManager, "_settings", rules(funds_enabled=False))

    message = refusal(lambda: resolve_bot("fund_quotas", {}), status=422)

    assert "Gestoras" in message


def test_a_room_with_funds_accepts_the_fund_strategy_for_bots(room, monkeypatch):
    monkeypatch.setattr(SettingsManager, "_settings", rules(funds_enabled=True))

    assert resolve_bot("fund_quotas", {}).strategy_key == "fund_quotas"


def test_the_backtest_refuses_the_fund_strategy_even_in_a_room_with_funds(
    room, monkeypatch
):
    monkeypatch.setattr(SettingsManager, "_settings", rules(funds_enabled=True))

    refusal(lambda: resolve_bot("fund_quotas", {}, funds_enabled=False), status=422)


def test_the_state_strategy_is_in_the_catalog_only_with_the_government_expansion(
    room,
):
    def keys(government: bool) -> set[str]:
        return {
            info.key
            for info in catalog.infos(
                START,
                None,
                catalog.known_tickers(),
                funds_enabled=False,
                government_enabled=government,
            )
        }

    assert "state_companies" in keys(True)
    assert "state_companies" not in keys(False)


def test_a_room_without_government_refuses_the_state_strategy_for_bots(
    room, monkeypatch
):
    monkeypatch.setattr(SettingsManager, "_settings", rules(government_enabled=False))

    message = refusal(lambda: resolve_bot("state_companies", {}), status=422)

    assert "Governo" in message


def test_a_room_with_government_accepts_the_state_strategy_for_bots(room, monkeypatch):
    monkeypatch.setattr(SettingsManager, "_settings", rules(government_enabled=True))

    assert resolve_bot("state_companies", {}).strategy_key == "state_companies"


def test_the_backtest_refuses_the_state_strategy_even_in_a_room_with_government(
    room, monkeypatch
):
    monkeypatch.setattr(SettingsManager, "_settings", rules(government_enabled=True))

    refusal(
        lambda: resolve_bot("state_companies", {}, government_enabled=False),
        status=422,
    )


def test_adding_a_bot_puts_a_new_bot_user_in_the_room(room):
    ana = person("Ana")

    bot = UserManager.add_bot("Tio Patinhas", resolve_bot("buy_and_hold", {}))

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
    UserManager.add_bot(
        "Tio Patinhas", resolve_bot("buy_and_hold", {}), color="chart-1"
    )

    UserManager.update_bot(
        "Tio Patinhas",
        "Rentista",
        resolve_bot("cdi_100", {}),
        color="chart-5",
        team=None,
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
    bot = UserManager.add_bot(
        "Tio Patinhas", resolve_bot("buy_and_hold", {}), color="chart-3"
    )

    UserManager.remove_bot("Tio Patinhas")

    assert UserManager.room_bots() == []
    assert bot.id not in UserManager.room_colors()
    assert repository.user.get_by_client_id(bot.client_id) is None
    again = UserManager.add_bot(
        "Outro", resolve_bot("buy_and_hold", {}), color="chart-3"
    )
    assert UserManager.room_colors()[again.id] == "chart-3"


def test_a_player_beyond_the_room_limit_is_refused(room):
    person("Ana")
    for i in range(len(PLAYER_COLORS) - 1):
        UserManager.add_bot(f"Bot {i}", resolve_bot("buy_and_hold", {}))

    detail = refusal(
        lambda: UserManager.add_bot("Bot extra", resolve_bot("buy_and_hold", {})),
        status=423,
    )

    assert "A sala está cheia" in detail


def test_a_repeated_name_is_refused_for_people_and_bots(room):
    person("Ana")
    UserManager.add_bot("Rentista", resolve_bot("cdi_100", {}))

    assert "Já tem um jogador com esse nome" in refusal(
        lambda: UserManager.add_bot("rentista", resolve_bot("cdi_100", {}))
    )
    assert "Já tem um jogador com esse nome" in refusal(
        lambda: UserManager.add_bot("Ana", resolve_bot("cdi_100", {}))
    )


def test_a_bot_name_with_hash_or_slash_is_refused_and_a_numbered_one_is_accepted(room):
    person("Ana")

    for name in ("Bot #2", "Bot/2"):
        assert "sem # nem /" in refusal(
            lambda name=name: UserManager.add_bot(name, resolve_bot("cdi_100", {})),
            status=422,
        )

    UserManager.add_bot("Rentista 2", resolve_bot("cdi_100", {}))
    assert bot_named("Rentista 2")


def test_a_taken_color_is_refused(room):
    UserManager.add_bot("Um", resolve_bot("cdi_100", {}), color="chart-2")

    assert "Um pegou essa cor antes" in refusal(
        lambda: UserManager.add_bot("Dois", resolve_bot("cdi_100", {}), color="chart-2")
    )


def batch(*names: str) -> list[tuple[str, BotConfig]]:
    return [(name, resolve_bot("cdi_100", {})) for name in names]


def test_adding_several_bots_gives_each_one_its_own_color(room):
    person("Ana")

    bots = UserManager.add_bots(batch("Um", "Dois", "Tres"))

    assert [b.nickname for b in bots] == ["Um", "Dois", "Tres"]
    colors = UserManager.room_colors()
    assert len({colors[b.id] for b in bots}) == 3
    assert all(b.is_bot for b in bots)
    assert len(UserManager.room_bots()) == 3


def test_a_batch_beyond_the_free_slots_adds_none(room):
    person("Ana")
    free = len(PLAYER_COLORS) - 1

    detail = refusal(
        lambda: UserManager.add_bots(batch(*(f"Bot {i}" for i in range(free + 1)))),
        status=423,
    )

    assert "A sala está cheia" in detail
    assert UserManager.room_bots() == []
    assert len(UserManager.add_bots(batch(*(f"Bot {i}" for i in range(free))))) == free


def test_a_batch_with_a_repeated_name_adds_none(room):
    person("Ana")

    assert "Já tem um jogador com esse nome" in refusal(
        lambda: UserManager.add_bots(batch("Um", "um"))
    )
    assert "Já tem um jogador com esse nome" in refusal(
        lambda: UserManager.add_bots(batch("Novo", "Ana"))
    )
    assert UserManager.room_bots() == []


def test_the_batch_route_adds_all_and_only_for_the_host(room):
    host = person(config.toml.host.nickname)
    ana = person("Ana")
    app = FastAPI()
    app.include_router(simulation_router)
    http = TestClient(app)
    body = {
        "bots": [
            {"nickname": "Um", "strategy_key": "cdi_100"},
            {"nickname": "Dois", "strategy_key": "buy_and_hold"},
        ]
    }

    app.dependency_overrides[get_client_id] = lambda: ana.client_id
    assert http.post("/api/simulation/bots/batch", json=body).status_code == 403

    app.dependency_overrides[get_client_id] = lambda: host.client_id
    added = http.post("/api/simulation/bots/batch", json=body)
    assert added.status_code == 201
    assert [p["nickname"] for p in added.json()] == ["Um", "Dois"]
    assert added.json()[1]["bot"]["strategy_name"] == "Comprar e segurar"
    assert http.post("/api/simulation/bots/batch", json={"bots": []}).status_code == 422


def test_invalid_parameters_are_refused_with_the_strategy_message(room):
    refusal(
        lambda: UserManager.add_bot("Rompedor", resolve_bot("rsi", {"period": 1})),
        status=422,
    )


def test_bots_are_spread_over_teams_in_a_team_room(room, monkeypatch):
    monkeypatch.setattr(
        SettingsManager, "_settings", rules(player_grouping=PlayerGrouping.TEAMS)
    )
    UserManager.add_bot("Um", resolve_bot("cdi_100", {}), team=3)

    assert UserManager.room_teams()[bot_named("Um").id] == 3
    refusal(
        lambda: UserManager.add_bot("Dois", resolve_bot("cdi_100", {}), team=99),
        status=422,
    )


def test_a_nickname_is_not_owned_by_a_bot(room):
    UserManager.add_bot("Rentista", resolve_bot("cdi_100", {}))

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
    codes = [row["ticker"] for row in tickers.json()]
    assert codes == sorted(codes)
    assert all(row["name"] for row in tickers.json())

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
    bot = UserManager.add_bot("Tio Patinhas", resolve_bot("buy_and_hold", {}))

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
    UserManager.add_bot("Tio Patinhas", resolve_bot("buy_and_hold", {}))
    sent: list[str] = []
    monkeypatch.setattr(
        RealtimeBrokerManager,
        "get_broker",
        lambda: SimpleNamespace(
            subscribed_clients=lambda _event: set(),
            notify=lambda event, *_a, **_k: sent.append(event),
        ),
    )

    SimulationLoader.create(rules())

    assert "player_exit" not in sent
    assert UserManager.room_bots() == []


def test_removing_a_bot_emits_its_exit(room, monkeypatch):
    UserManager.add_bot("Tio Patinhas", resolve_bot("buy_and_hold", {}))
    sent: list[str] = []
    monkeypatch.setattr(
        RealtimeBrokerManager,
        "get_broker",
        lambda: SimpleNamespace(
            subscribed_clients=lambda _event: set(),
            notify=lambda event, *_a, **_k: sent.append(event),
        ),
    )

    UserManager.remove_bot("Tio Patinhas")

    assert sent == ["player_exit"]


def test_the_bot_runs_its_strategy_and_receives_the_contribution(room):
    ana = person("Ana")
    bot = UserManager.add_bot("Tio Patinhas", resolve_bot("buy_and_hold", {}))
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


def test_the_profession_is_saved_in_the_match_and_returns_to_the_room_afterwards(
    room, remembered_professions, monkeypatch: pytest.MonkeyPatch
):
    professions_rules = rules(
        game_type=GameType.FINANCIAL_INDEPENDENCE, salary_mode=SalaryMode.PROFESSIONS
    )
    monkeypatch.setattr(SettingsManager, "_settings", professions_rules)
    ana = person("Ana")
    UserManager.set_profession(ana.client_id, Profession.RETIREE)

    simulation = SimulationLoader.create(professions_rules)

    saved = repository.simulation_player.professions(simulation.id)
    assert saved[ana.id] == Profession.RETIREE
    assert remembered_professions[ana.id] == Profession.RETIREE
    assert UserManager._professions[ana.id] == Profession.RETIREE


def test_a_bot_never_unlocks_achievements(room):
    ana = person("Ana")
    bot = UserManager.add_bot("Tio Patinhas", resolve_bot("buy_and_hold", {}))
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
    return SimpleNamespace(
        players=players,
        teams=teams,
        parties=[],
        game_type=GameType.CLASSIC,
        survivor_nickname=None,
    )


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
        parties=[],
        game_type=GameType.CLASSIC,
        survivor_nickname=None,
    )
    monkeypatch.setattr(evaluator, "build_overview_report", lambda _ids: both)

    assert evaluator.match_result(1, [ana, robot], False).winners == {1}


def test_the_last_standing_player_wins_even_with_a_bot_in_first_place(monkeypatch):
    ana = UserDTO(id=1, client_id=uuid.uuid4(), nickname="Ana")
    robot = UserDTO(id=2, client_id=uuid.uuid4(), nickname="Robô", is_bot=True)
    overview = _overview(first_is_bot=True)
    overview.survivor_nickname = "Ana"
    overview.game_type = GameType.FUND_TAKEOVER
    monkeypatch.setattr(evaluator, "build_overview_report", lambda _ids: overview)

    assert evaluator.match_result(1, [ana, robot], False).winners == {1}


def _political_overview(parties: list[SimpleNamespace]):
    return SimpleNamespace(
        players=[SimpleNamespace(player_nickname="Ana", team=1)],
        teams=[],
        parties=parties,
        game_type=GameType.POLITICAL,
        survivor_nickname=None,
    )


def test_in_the_political_victory_the_people_of_the_first_party_win_and_the_bot_does_not(
    monkeypatch,
):
    ana = UserDTO(id=1, client_id=uuid.uuid4(), nickname="Ana")
    beto = UserDTO(id=2, client_id=uuid.uuid4(), nickname="Beto")
    robot = UserDTO(id=3, client_id=uuid.uuid4(), nickname="Robô", is_bot=True)
    cris = UserDTO(id=4, client_id=uuid.uuid4(), nickname="Cris")
    overview = _political_overview(
        [
            SimpleNamespace(members=["Ana", "Robô"]),
            SimpleNamespace(members=["Beto", "Cris"]),
        ]
    )
    monkeypatch.setattr(evaluator, "build_overview_report", lambda _ids: overview)

    result = evaluator.match_result(1, [ana, beto, robot, cris], False)

    assert result.winners == {1}
    assert result.players_count == 4


def test_in_the_political_victory_without_parties_nobody_wins(monkeypatch):
    ana = UserDTO(id=1, client_id=uuid.uuid4(), nickname="Ana")
    overview = _political_overview([])
    monkeypatch.setattr(evaluator, "build_overview_report", lambda _ids: overview)

    assert evaluator.match_result(1, [ana], False).winners == frozenset()


def test_the_bot_log_opens_only_when_the_match_ends(room):
    person("Ana")
    UserManager.add_bot("Tio Patinhas", resolve_bot("buy_and_hold", {}))
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
    UserManager.add_bot("O Grafista", resolve_bot("moving_average_cross", {}))
    SimulationLoader.create(rules())
    simulation_id = SimulationManager.get_active_simulation_id()
    SimulationManager.clear_simulation()

    # Sala nova: a Ana volta e o host já tinha posto outro bot
    UserManager._active_players.clear()
    UserManager._colors.clear()
    UserManager._bots.clear()
    UserManager.player_auth(ana.client_id)
    novo = UserManager.add_bot("Novato", resolve_bot("cdi_100", {}), color="chart-7")

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
    refusal(
        lambda: UserManager.update_bot("O Grafista", "X", resolve_bot("cdi_100", {}))
    )
    refusal(lambda: UserManager.add_bot("Outro", resolve_bot("cdi_100", {})))

    UserManager.release_saved_colors()

    assert {b.nickname for b, _ in UserManager.room_bots()} == {"Novato"}
    assert repository.user.get_by_client_id(novo.client_id) is not None


def test_resuming_a_match_brings_the_bot_back_with_the_same_parameters(room):
    person("Ana")
    UserManager.add_bot(
        "O Grafista", resolve_bot("moving_average_cross", {"short_window": 20})
    )
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


def professions_rules(**changes: object):
    return rules(
        game_type=GameType.FINANCIAL_INDEPENDENCE,
        salary_mode=SalaryMode.PROFESSIONS,
        **changes,
    )


def test_a_bot_with_a_fixed_profession_keeps_it(room, monkeypatch):
    monkeypatch.setattr(SettingsManager, "_settings", professions_rules())
    person("Ana")

    bot = UserManager.add_bot(
        "Herdeiro",
        resolve_bot("cdi_100", {}, profession=Profession.HEIR),
    )

    assert UserManager.get_profession(bot.id) is Profession.HEIR


def test_a_bot_without_a_profession_draws_one_the_room_allows(room, monkeypatch):
    monkeypatch.setattr(
        SettingsManager, "_settings", professions_rules(inflation_adjusted=False)
    )
    person("Ana")

    drawn = {
        UserManager.get_profession(
            UserManager.add_bot(f"Bot {i}", resolve_bot("cdi_100", {})).id
        )
        for i in range(8)
    }

    assert Profession.FREELANCER not in drawn
    assert drawn <= set(Profession)


def test_a_fixed_profession_the_room_does_not_offer_is_refused(room, monkeypatch):
    monkeypatch.setattr(
        SettingsManager, "_settings", professions_rules(inflation_adjusted=False)
    )

    assert "profissão" in refusal(
        lambda: resolve_bot("cdi_100", {}, profession=Profession.FREELANCER), 422
    )


def test_the_players_start_with_the_capital_of_their_profession(room, monkeypatch):
    # Sem imprevistos: o caixa do primeiro pregão é só o capital, a renda e a despesa
    settings = professions_rules(starting_cash=Decimal(10000), unexpected_per_year=0)
    monkeypatch.setattr(SettingsManager, "_settings", settings)
    ana, bia, caio = person("Ana"), person("Bia"), person("Caio")
    UserManager.set_profession(ana.client_id, Profession.HEIR)
    UserManager.set_profession(bia.client_id, Profession.NEW_GRADUATE)
    UserManager.set_profession(caio.client_id, Profession.CLT)

    SimulationLoader.create(settings)

    sim = SimulationManager.get_active_simulation()
    assert sim.get_portfolio(ana.client_id).cash > Decimal(10000)
    # Quem começa sem capital só tem o que o primeiro pregão paga e cobra
    assert sim.get_portfolio(bia.client_id).cash < Decimal(1000)
    assert sim.get_portfolio(caio.client_id).cash > Decimal(9000)


def heir_capital(settings) -> Decimal:
    return (
        LifeBudget.of(settings)
        .for_profession(Profession.HEIR)
        .starting_capital(
            settings.starting_cash, settings.start_date, settings.end_date
        )
    )


def test_the_goal_must_pass_the_capital_of_a_heir_bot(room, monkeypatch):
    # Despesa de 200 a 4% dá meta de 60.000, abaixo do que o Herdeiro leva consigo
    settings = professions_rules(
        monthly_expense=Decimal(200), withdrawal_rate=Decimal("0.04")
    )
    monkeypatch.setattr(SettingsManager, "_settings", settings)
    ana = person("Ana")
    UserManager.set_profession(ana.client_id, Profession.CLT)
    UserManager.add_bot(
        "Herdeiro", resolve_bot("cdi_100", {}, profession=Profession.HEIR)
    )
    capital = heir_capital(settings)
    assert capital > LifeBudget.of(settings).goal_on(settings.start_date)

    message = refusal(lambda: SimulationLoader.create(settings), status=422)

    minimum = f"{capital.to_integral_value(rounding=ROUND_CEILING):,.0f}".replace(
        ",", "."
    )
    assert message == f"Meta mínima de R$ {minimum} por causa de Herdeiro."
    assert not SimulationManager.has_active_simulation()


def test_the_goal_must_pass_the_capital_of_a_heir_player(room, monkeypatch):
    settings = professions_rules(
        monthly_expense=Decimal(200), withdrawal_rate=Decimal("0.04")
    )
    monkeypatch.setattr(SettingsManager, "_settings", settings)
    ana = person("Ana")
    UserManager.set_profession(ana.client_id, Profession.HEIR)

    message = refusal(lambda: SimulationLoader.create(settings), status=422)

    assert message.startswith("Meta mínima de R$ ")
    assert message.endswith(" por causa de Ana.")


def test_a_goal_above_the_heir_capital_is_accepted(room, monkeypatch):
    settings = professions_rules(
        monthly_expense=Decimal(200), withdrawal_rate=Decimal("0.04")
    )
    capital = heir_capital(settings)
    # A despesa que faz a meta passar do capital do Herdeiro
    settings = settings.model_copy(
        update={"monthly_expense": capital * Decimal("0.04") / 12 + 1}
    )
    monkeypatch.setattr(SettingsManager, "_settings", settings)
    ana = person("Ana")
    UserManager.set_profession(ana.client_id, Profession.HEIR)

    SimulationLoader.create(settings)

    assert SimulationManager.has_active_simulation()


def test_without_a_heir_the_floor_is_the_room_cash(room, monkeypatch):
    settings = professions_rules(
        monthly_expense=Decimal(200), withdrawal_rate=Decimal("0.04")
    )
    monkeypatch.setattr(SettingsManager, "_settings", settings)
    ana = person("Ana")
    UserManager.set_profession(ana.client_id, Profession.CLT)

    SimulationLoader.create(settings)

    assert SimulationManager.has_active_simulation()
