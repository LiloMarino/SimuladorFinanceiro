"""Rotas da preparação: a última escolha fica no perfil e quem fundou volta fundando na sala nova."""

from __future__ import annotations

from collections.abc import Iterator
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core import repository
from backend.core.dto.preparation import FundIdentityDTO, PartyIdentityDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import FundPreparationKind, PreparationKind, VoterValue
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.government.room_preparation import RoomPreparation
from backend.features.simulation.room_fund_preparation import RoomFundPreparation
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


FUND = FundIdentityDTO(name="Aurora", ticker="AURA11")


class _Profile:
    def __init__(self) -> None:
        self.choice: dict[int, PreparationKind] = {}
        self.fund: FundIdentityDTO | None = FUND
        self.fund_choice: dict[int, FundPreparationKind] = {}

    def get_my_fund(self, _user_id: int) -> FundIdentityDTO | None:
        return self.fund

    def get_fund_choice(self, user_id: int) -> FundPreparationKind:
        return self.fund_choice.get(user_id, FundPreparationKind.NONE)

    def set_fund_choice(self, user_id: int, kind: FundPreparationKind) -> None:
        self.fund_choice[user_id] = kind

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
    rules = simulation_settings().model_copy(
        update={"government_enabled": True, "funds_enabled": True}
    )
    monkeypatch.setattr(SettingsManager, "_settings", rules)
    monkeypatch.setattr(RoomFundPreparation, "_entries", {})
    monkeypatch.setattr(
        repository, "fund", SimpleNamespace(letters_taken_by_asset=lambda _t: False)
    )
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


def test_a_player_without_a_saved_choice_has_no_fund(http: TestClient):
    http.get("/api/simulation/players/me/preparation")

    assert http.get("/api/simulation/preparations").json()["funds"] == []


def test_founding_a_fund_is_remembered_and_shown_to_the_room(
    http: TestClient, profile: _Profile
):
    answer = http.put(
        "/api/simulation/players/me/fund-preparation", json={"kind": "FOUND"}
    )

    assert answer.status_code == 200
    assert profile.fund_choice == {ANA.id: FundPreparationKind.FOUND}
    assert http.get("/api/simulation/preparations").json()["funds"] == [
        {"nickname": "Ana", "name": "Aurora", "ticker": "AURA11"}
    ]

    http.put("/api/simulation/players/me/fund-preparation", json={"kind": "NONE"})

    assert profile.fund_choice == {ANA.id: FundPreparationKind.NONE}
    assert http.get("/api/simulation/preparations").json()["funds"] == []


def test_founding_a_fund_without_a_saved_one_is_refused(
    http: TestClient, profile: _Profile
):
    profile.fund = None

    answer = http.put(
        "/api/simulation/players/me/fund-preparation", json={"kind": "FOUND"}
    )

    assert answer.status_code == 409
    assert profile.fund_choice == {}


def test_the_fund_founder_of_the_last_room_comes_back_founding(
    http: TestClient, profile: _Profile
):
    profile.fund_choice[ANA.id] = FundPreparationKind.FOUND

    http.get("/api/simulation/players/me/preparation")

    assert [
        f["ticker"] for f in http.get("/api/simulation/preparations").json()["funds"]
    ] == ["AURA11"]


def test_a_taken_ticker_shows_up_among_the_conflicts(http: TestClient):
    RoomFundPreparation.choose(BIA, FundPreparationKind.FOUND, FUND)

    http.put("/api/simulation/players/me/fund-preparation", json={"kind": "FOUND"})

    conflicts = http.get("/api/simulation/preparations").json()["conflicts"]
    assert any("Ana e Bia" in message for message in conflicts)
