"""Rotas da preparação: a última escolha fica no perfil e quem fundou volta fundando na sala nova."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core import repository
from backend.core.dto.preparation import PartyIdentityDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import PreparationKind, VoterValue
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.government.room_preparation import RoomPreparation
from backend.routes import simulation as routes
from backend.routes.dependencies.auth import get_client_id
from tests.fakes import client, simulation_settings

ANA = UserDTO(id=1, client_id=client("ana"), nickname="Ana")
BIA = UserDTO(id=2, client_id=client("bia"), nickname="Bia")
PARTY = PartyIdentityDTO(
    name="Partido Alfa",
    abbr="ALF",
    color="#dc2626",
    flags=[VoterValue.STABILITY, VoterValue.DEVELOPMENT, VoterValue.SAVER_PROTECTION],
)


class _Profile:
    def __init__(self) -> None:
        self.choice: dict[int, PreparationKind] = {}

    def get_my_party(self, _user_id: int) -> PartyIdentityDTO:
        return PARTY

    def get_preparation_choice(self, user_id: int) -> PreparationKind:
        return self.choice.get(user_id, PreparationKind.NONE)

    def set_preparation_choice(self, user_id: int, kind: PreparationKind) -> None:
        self.choice[user_id] = kind


@pytest.fixture
def profile(monkeypatch: pytest.MonkeyPatch) -> _Profile:
    fake = _Profile()
    monkeypatch.setattr(repository, "settings", fake)
    return fake


@pytest.fixture
def http(monkeypatch: pytest.MonkeyPatch, profile: _Profile) -> Iterator[TestClient]:
    rules = simulation_settings().model_copy(update={"government_enabled": True})
    monkeypatch.setattr(SettingsManager, "_settings", rules)
    monkeypatch.setattr(SettingsManager, "_selected_simulation_id", None)
    monkeypatch.setattr(SimulationManager, "_active_simulation", None)
    monkeypatch.setattr(RoomPreparation, "_entries", {})
    monkeypatch.setattr(RoomPreparation, "_left", {})
    monkeypatch.setattr(UserManager, "list_active_players", lambda: [ANA, BIA])
    monkeypatch.setattr(
        UserManager, "get_user", lambda cid: ANA if cid == ANA.client_id else BIA
    )
    monkeypatch.setattr(routes, "notify", lambda *_args, **_kwargs: None)
    app = FastAPI()
    app.include_router(routes.simulation_router)
    app.dependency_overrides[get_client_id] = lambda: ANA.client_id
    yield TestClient(app)


def test_founding_is_remembered_and_joining_comes_back_as_no_party(
    http: TestClient, profile: _Profile
):
    http.put("/api/simulation/players/me/preparation", json={"kind": "FOUND"})
    assert profile.choice == {ANA.id: PreparationKind.FOUND}

    RoomPreparation.choose(
        BIA,
        PreparationKind.FOUND,
        [ANA, BIA],
        identity=PARTY.model_copy(update={"abbr": "BET", "name": "Beta"}),
        founder=None,
        candidate=None,
        vice=None,
    )
    http.put(
        "/api/simulation/players/me/preparation",
        json={"kind": "JOIN", "founder": "Bia"},
    )
    assert profile.choice == {ANA.id: PreparationKind.NONE}


def test_the_founder_of_the_last_room_comes_back_founding(
    http: TestClient, profile: _Profile
):
    profile.choice[ANA.id] = PreparationKind.FOUND

    answer = http.get("/api/simulation/players/me/preparation")

    assert answer.status_code == 200
    [ana] = RoomPreparation.snapshot([ANA, BIA]).players
    assert (ana.kind, ana.candidate) == (PreparationKind.FOUND, "Ana")


def test_who_chose_no_party_stays_without_one(http: TestClient):
    http.get("/api/simulation/players/me/preparation")

    assert RoomPreparation.snapshot([ANA, BIA]).players == []
