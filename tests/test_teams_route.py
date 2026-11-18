"""Rotas das equipes: escolher a própria, distribuir quem falta (host) e desfazer as
equipes quando o host volta para todos contra todos."""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core.dto.simulation import SimulationSettingsDTO
from backend.core.enum import GameType, PlayerGrouping, Profession, SalaryMode
from backend.core.life_budget import LifeBudget
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.routes.dependencies import get_client_id, verify_host
from backend.routes.simulation import simulation_router
from tests.conftest import Join
from tests.fakes import client, simulation_settings


@pytest.fixture
def api(team_room: Join) -> Iterator[tuple[TestClient, Join]]:
    app = FastAPI()
    app.include_router(simulation_router)
    app.dependency_overrides[get_client_id] = lambda: client("Ana")
    app.dependency_overrides[verify_host] = lambda: None
    yield TestClient(app), team_room


def professions_settings() -> SimulationSettingsDTO:
    """Regras do viver de renda com uma profissão para cada jogador."""
    return simulation_settings().model_copy(
        update={
            "game_type": GameType.FINANCIAL_INDEPENDENCE,
            "salary_mode": SalaryMode.PROFESSIONS,
        }
    )


def test_player_picks_a_team_and_the_room_list_shows_it(
    api: tuple[TestClient, Join],
):
    http, join = api
    ana = join("Ana")

    assert (
        http.put("/api/simulation/players/me/team", json={"team": 4}).status_code == 204
    )

    listed = http.get("/api/simulation/players").json()
    assert listed == [
        {
            "nickname": "Ana",
            "color": "chart-1",
            "team": 4,
            "profession": None,
            "party": None,
            "activity": None,
            "bot": None,
        }
    ]
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


def test_profession_is_a_conflict_when_the_room_has_equal_salary(
    api: tuple[TestClient, Join],
):
    http, join = api
    join("Ana")

    response = http.put(
        "/api/simulation/players/me/profession", json={"profession": "RETIREE"}
    )

    assert response.status_code == 409


def test_player_picks_a_profession_in_the_professions_room(
    api: tuple[TestClient, Join], monkeypatch: pytest.MonkeyPatch
):
    http, join = api
    ana = join("Ana")
    settings = simulation_settings().model_copy(
        update={
            "game_type": GameType.FINANCIAL_INDEPENDENCE,
            "salary_mode": SalaryMode.PROFESSIONS,
        }
    )
    monkeypatch.setattr(SettingsManager, "_settings", settings)

    response = http.put(
        "/api/simulation/players/me/profession", json={"profession": "RETIREE"}
    )

    assert response.status_code == 204
    assert UserManager.get_profession(ana.id) == Profession.RETIREE
    listed = http.get("/api/simulation/players").json()
    assert listed[0]["profession"] == "RETIREE"


def test_the_chosen_profession_is_saved_in_the_profile(
    api: tuple[TestClient, Join],
    monkeypatch: pytest.MonkeyPatch,
    remembered_professions: dict[int, Profession],
):
    http, join = api
    ana = join("Ana")
    monkeypatch.setattr(SettingsManager, "_settings", professions_settings())

    http.put("/api/simulation/players/me/profession", json={"profession": "WELFARE"})

    assert remembered_professions == {ana.id: Profession.WELFARE}


def test_the_room_starts_with_the_profession_of_the_profile(
    api: tuple[TestClient, Join],
    monkeypatch: pytest.MonkeyPatch,
    remembered_professions: dict[int, Profession],
):
    _, join = api
    monkeypatch.setattr(SettingsManager, "_settings", professions_settings())
    remembered_professions[1] = Profession.LANDLORD

    ana = join("Ana")

    assert UserManager.get_profession(ana.id) == Profession.LANDLORD


def test_the_profession_of_the_saved_match_wins_over_the_profile(
    api: tuple[TestClient, Join],
    monkeypatch: pytest.MonkeyPatch,
    remembered_professions: dict[int, Profession],
):
    _, join = api
    monkeypatch.setattr(SettingsManager, "_settings", professions_settings())
    monkeypatch.setattr(UserManager, "_saved_professions", {1: Profession.RETIREE})
    monkeypatch.setattr(UserManager, "_professions", {1: Profession.RETIREE})
    remembered_professions[1] = Profession.LANDLORD

    ana = join("Ana")

    assert UserManager.get_profession(ana.id) == Profession.RETIREE


def test_the_profession_of_the_profile_returns_to_the_room_after_the_match_starts(
    api: tuple[TestClient, Join],
    monkeypatch: pytest.MonkeyPatch,
    remembered_professions: dict[int, Profession],
):
    http, join = api
    ana = join("Ana")
    monkeypatch.setattr(SettingsManager, "_settings", professions_settings())
    http.put("/api/simulation/players/me/profession", json={"profession": "WELFARE"})

    UserManager.release_room_teams()

    assert remembered_professions == {ana.id: Profession.WELFARE}
    assert UserManager.chosen_professions() == {ana.id: Profession.WELFARE}


def test_the_heir_capital_is_the_room_cash_plus_the_inheritance_of_the_room_rules(
    api: tuple[TestClient, Join], monkeypatch: pytest.MonkeyPatch
):
    http, join = api
    join("Ana")
    rules = professions_settings()
    monkeypatch.setattr(SettingsManager, "_settings", rules)

    response = http.get("/api/simulation/heir-capital")

    expected = (
        LifeBudget.of(rules)
        .for_profession(Profession.HEIR)
        .starting_capital(rules.starting_cash, rules.start_date, rules.end_date)
    )
    assert response.status_code == 200
    assert Decimal(response.json()["starting_capital"]) == expected
    assert expected > rules.starting_cash


def test_equal_salary_room_neither_saves_nor_seeds_a_profession(
    api: tuple[TestClient, Join], remembered_professions: dict[int, Profession]
):
    http, join = api
    join("Ana")

    http.put("/api/simulation/players/me/profession", json={"profession": "WELFARE"})

    assert remembered_professions == {}


def government_settings() -> SimulationSettingsDTO:
    """Regras com profissões e a expansão Governo & Política, que libera o Comissionado."""
    return professions_settings().model_copy(update={"government_enabled": True})


def test_commissioned_needs_a_party_of_the_room(api: tuple[TestClient, Join]):
    http, join = api
    join("Ana")
    SettingsManager._settings = government_settings()

    # Sem sigla e com sigla que não existe na sala, a escolha é recusada
    without = http.put(
        "/api/simulation/players/me/profession", json={"profession": "COMMISSIONED"}
    )
    unknown = http.put(
        "/api/simulation/players/me/profession",
        json={"profession": "COMMISSIONED", "party": "XYZ"},
    )

    assert without.status_code == 422
    assert unknown.status_code == 422


def test_commissioned_saves_the_party_in_the_room_and_the_profile(
    api: tuple[TestClient, Join],
):
    http, join = api
    ana = join("Ana")
    SettingsManager._settings = government_settings()

    response = http.put(
        "/api/simulation/players/me/profession",
        json={"profession": "COMMISSIONED", "party": "UPR"},
    )

    assert response.status_code == 204
    assert UserManager.get_profession(ana.id) == Profession.COMMISSIONED
    assert UserManager._parties[ana.id] == "UPR"
    listed = http.get("/api/simulation/players").json()
    assert listed[0]["party"] == "UPR"


def test_commissioned_is_not_offered_without_the_government_expansion(
    api: tuple[TestClient, Join], monkeypatch: pytest.MonkeyPatch
):
    http, join = api
    join("Ana")
    monkeypatch.setattr(SettingsManager, "_settings", professions_settings())

    response = http.put(
        "/api/simulation/players/me/profession",
        json={"profession": "COMMISSIONED", "party": "UPR"},
    )

    assert response.status_code == 409


def test_offers_banker_needs_the_funds_expansion(
    api: tuple[TestClient, Join], monkeypatch: pytest.MonkeyPatch
):
    http, join = api
    ana = join("Ana")
    monkeypatch.setattr(SettingsManager, "_settings", professions_settings())
    refused = http.put(
        "/api/simulation/players/me/profession", json={"profession": "OFFERS_BANKER"}
    )
    monkeypatch.setattr(
        SettingsManager,
        "_settings",
        professions_settings().model_copy(update={"funds_enabled": True}),
    )

    accepted = http.put(
        "/api/simulation/players/me/profession", json={"profession": "OFFERS_BANKER"}
    )

    assert refused.status_code == 409
    assert accepted.status_code == 204
    assert UserManager.get_profession(ana.id) == Profession.OFFERS_BANKER


def test_a_profession_without_party_drops_the_party_of_the_player(
    api: tuple[TestClient, Join],
):
    http, join = api
    ana = join("Ana")
    SettingsManager._settings = government_settings()
    http.put(
        "/api/simulation/players/me/profession",
        json={"profession": "COMMISSIONED", "party": "UPR"},
    )

    http.put("/api/simulation/players/me/profession", json={"profession": "RETIREE"})

    assert http.get("/api/simulation/players").json()[0]["party"] is None
    assert ana.id not in UserManager._parties


def test_match_parties_lists_the_parties_of_the_running_match(
    api: tuple[TestClient, Join], monkeypatch: pytest.MonkeyPatch
):
    http, _ = api
    assert http.get("/api/simulation/match-parties").status_code == 409
    running = SimpleNamespace(party_abbrs=lambda: frozenset({"UPR", "ACI"}))
    monkeypatch.setattr(SimulationManager, "has_active_simulation", lambda: True)
    monkeypatch.setattr(SimulationManager, "get_active_simulation", lambda: running)

    response = http.get("/api/simulation/match-parties")

    assert response.json() == ["ACI", "UPR"]
