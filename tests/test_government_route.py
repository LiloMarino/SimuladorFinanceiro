"""Rotas do partido: a contribuição escolhida na partida fica salva no perfil do jogador."""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core import repository
from backend.core.dependencies import get_current_user
from backend.core.dependencies.simulation import get_active_simulation
from backend.core.dto.user import UserDTO
from backend.routes.government import government_router
from tests.fakes import client

ALICE = UserDTO(id=1, client_id=client("alice"), nickname="Alice")


class _Simulation:
    def join_party(self, *_args: object) -> None:
        pass

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
def http(profile: _Profile) -> Iterator[TestClient]:
    app = FastAPI()
    app.include_router(government_router)
    app.dependency_overrides[get_active_simulation] = _Simulation
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
