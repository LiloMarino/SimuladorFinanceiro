"""Rotas das equipes: escolher a própria, distribuir quem falta (host) e desfazer as
equipes quando o host volta para todos contra todos."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core.dependencies import get_client_id, verify_host
from backend.core.enum import PlayerGrouping
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.user_manager import UserManager
from backend.routes.simulation import simulation_router
from tests.conftest import Join
from tests.fakes import client


@pytest.fixture
def api(team_room: Join) -> Iterator[tuple[TestClient, Join]]:
    app = FastAPI()
    app.include_router(simulation_router)
    app.dependency_overrides[get_client_id] = lambda: client("Ana")
    app.dependency_overrides[verify_host] = lambda: None
    yield TestClient(app), team_room


def test_player_picks_a_team_and_the_room_list_shows_it(
    api: tuple[TestClient, Join],
):
    http, join = api
    ana = join("Ana")

    assert (
        http.put("/api/simulation/players/me/team", json={"team": 4}).status_code == 204
    )

    listed = http.get("/api/simulation/players").json()
    assert listed == [{"nickname": "Ana", "color": "chart-1", "team": 4}]
    assert UserManager.get_team(ana.id) == 4


def test_unknown_team_is_unprocessable(api: tuple[TestClient, Join]):
    http, join = api
    join("Ana")

    assert (
        http.put("/api/simulation/players/me/team", json={"team": 12}).status_code
        == 422
    )


def test_host_distributes_who_is_missing(api: tuple[TestClient, Join]):
    http, join = api
    join("Ana")
    join("Bia")

    assert http.post("/api/simulation/teams/distribute").status_code == 204

    teams = {
        p["nickname"]: p["team"] for p in http.get("/api/simulation/players").json()
    }
    assert teams == {"Ana": 1, "Bia": 2}


def settings_body(grouping: PlayerGrouping) -> dict[str, object]:
    return {
        "name": "Sala",
        "start_date": "2020-01-01",
        "end_date": "2020-12-31",
        "starting_cash": "10000",
        "goal_net_worth": "100000",
        "monthly_contribution": "0",
        "price_impact_k": 0.02,
        "price_impact_decay_days": 20,
        "player_grouping": grouping.value,
    }


def test_going_back_to_individual_clears_the_teams(api: tuple[TestClient, Join]):
    http, join = api
    ana = join("Ana")
    UserManager.set_team(ana.client_id, 2)

    response = http.put(
        "/api/simulation/settings", json=settings_body(PlayerGrouping.INDIVIDUAL)
    )

    assert response.status_code == 200
    assert response.json()["player_grouping"] == "INDIVIDUAL"
    assert http.get("/api/simulation/players").json()[0]["team"] is None


def test_keeping_the_grouping_keeps_the_teams(api: tuple[TestClient, Join]):
    http, join = api
    ana = join("Ana")
    UserManager.set_team(ana.client_id, 2)
    assert SettingsManager.get().player_grouping is PlayerGrouping.TEAMS

    http.put("/api/simulation/settings", json=settings_body(PlayerGrouping.TEAMS))

    assert http.get("/api/simulation/players").json()[0]["team"] == 2
