"""O host tira uma pessoa da sala no lobby."""

from __future__ import annotations

from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend import config
from backend.core import repository
from backend.core.dependencies import get_client_id
from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.simulation.simulation_loader import SimulationLoader
from backend.routes.simulation import simulation_router
from tests.test_bots import person, refusal, room, rules  # noqa: F401
from tests.test_simulation_loader import started  # noqa: F401


def test_removing_a_person_frees_the_slot_and_the_color(room):  # noqa: F811
    ana = person("Ana")
    color = UserManager.room_colors()[ana.id]

    UserManager.remove_player("Ana")

    assert UserManager.list_active_players() == []
    assert ana.id not in UserManager.room_colors()
    # A conta segue: só a presença na sala acaba
    assert repository.user.get_by_client_id(ana.client_id) is not None
    bia = person("Bia")
    assert UserManager.room_colors()[bia.id] == color


def test_the_removed_player_is_told_directly(room, monkeypatch):  # noqa: F811
    ana = person("Ana")
    sent: list[tuple[str, object]] = []
    monkeypatch.setattr(
        RealtimeBrokerManager,
        "get_broker",
        lambda: SimpleNamespace(
            notify=lambda event, payload, to=None: sent.append((event, to))
        ),
    )

    UserManager.remove_player("Ana")

    assert ("player_removed", ana.client_id) in sent
    assert [to for event, to in sent if event == "player_removed"] == [ana.client_id]


def test_the_host_and_bots_and_strangers_cannot_be_removed(room):  # noqa: F811
    person(config.toml.host.nickname)
    UserManager.add_bot("Tio Patinhas", "buy_and_hold", {})

    assert "host" in refusal(
        lambda: UserManager.remove_player(config.toml.host.nickname)
    )
    assert refusal(lambda: UserManager.remove_player("Tio Patinhas"), 404)
    assert refusal(lambda: UserManager.remove_player("Ninguém"), 404)
    assert len(UserManager.list_active_players()) == 2


def test_a_match_in_progress_keeps_everyone(room):  # noqa: F811
    person("Ana")
    SimulationLoader.create(rules())
    assert SimulationManager.has_active_simulation()

    detail = refusal(lambda: UserManager.remove_player("Ana"))

    assert "lobby" in detail
    assert [p.nickname for p in UserManager.list_active_players()] == ["Ana"]


def test_only_the_host_removes_players(room):  # noqa: F811
    host = person(config.toml.host.nickname)
    ana = person("Ana")
    app = FastAPI()
    app.include_router(simulation_router)
    http = TestClient(app)

    app.dependency_overrides[get_client_id] = lambda: ana.client_id
    assert http.delete("/api/simulation/players/Ana").status_code == 403

    app.dependency_overrides[get_client_id] = lambda: host.client_id
    assert http.delete("/api/simulation/players/Ana").status_code == 204
    assert http.delete("/api/simulation/players/Ana").status_code == 404
    assert [p.nickname for p in UserManager.list_active_players()] == [host.nickname]
