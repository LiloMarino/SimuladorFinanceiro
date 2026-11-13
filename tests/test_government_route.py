"""Rotas do partido: a contribuição escolhida na partida fica salva no perfil do jogador."""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core import repository
from backend.core.dto.user import UserDTO
from backend.routes.dependencies import get_current_user
from backend.routes.dependencies.simulation import get_active_simulation
from backend.routes.government import government_router
from tests.fakes import client

ALICE = UserDTO(id=1, client_id=client("alice"), nickname="Alice")


class _Simulation:
    def __init__(self) -> None:
        self.answers: list[tuple[bool, str | None, str | None]] = []

    def join_party(self, *_args: object) -> None:
        pass

    def answer_deal(
        self, _user: UserDTO, accept: bool, sector: str | None, segment: str | None
    ) -> None:
        self.answers.append((accept, sector, segment))

    def set_contribution(self, *_args: object) -> None:
        pass


class _Profile:
    def __init__(self) -> None:
        self.saved: dict[int, Decimal] = {}

    def set_party_contribution(self, user_id: int, amount: Decimal) -> None:
        self.saved[user_id] = amount


@pytest.fixture
def profile(monkeypatch: pytest.MonkeyPatch) -> _Profile:
    fake = _Profile()
    monkeypatch.setattr(repository, "settings", fake)
    return fake


@pytest.fixture
def simulation() -> _Simulation:
    return _Simulation()


@pytest.fixture
def http(profile: _Profile, simulation: _Simulation) -> Iterator[TestClient]:
    app = FastAPI()
    app.include_router(government_router)
    app.dependency_overrides[get_active_simulation] = lambda: simulation
    app.dependency_overrides[get_current_user] = lambda: ALICE
    yield TestClient(app)


def test_joining_saves_the_contribution_in_the_profile(
    http: TestClient, profile: _Profile
):
    http.post("/api/government/parties/7/members", json={"contribution": "1500"})

    assert profile.saved == {ALICE.id: Decimal(1500)}


def test_changing_the_contribution_saves_it_in_the_profile(
    http: TestClient, profile: _Profile
):
    http.put("/api/government/membership/contribution", json={"contribution": "800"})

    assert profile.saved == {ALICE.id: Decimal(800)}


def test_accepting_a_deal_forwards_the_address_of_the_amendment(
    http: TestClient, simulation: _Simulation
):
    response = http.put(
        "/api/government/deals/answer",
        json={"accept": True, "sector": "Energia", "segment": "Geração"},
    )

    assert response.status_code == 204
    assert simulation.answers == [(True, "Energia", "Geração")]


def test_answering_a_deal_without_an_address_sends_none(
    http: TestClient, simulation: _Simulation
):
    http.put("/api/government/deals/answer", json={"accept": False})

    assert simulation.answers == [(False, None, None)]
