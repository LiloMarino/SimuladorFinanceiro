"""`/api/settings` mostra o modo debug do servidor e nunca o grava no usuário."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend import config
from backend.core import repository
from backend.core.dependencies import get_client_id
from backend.core.runtime.user_manager import UserManager
from backend.routes.settings import settings_router

PREFERENCES = {
    "orders": {"executed": False, "partial": True},
    "players": {"join_exit": True},
}


class _FakeSettingsRepository:
    def __init__(self) -> None:
        self.stored: dict[str, Any] = {}

    def get_by_user_id(self, _user_id: int) -> dict[str, Any]:
        return self.stored

    def update_by_user_id(self, _user_id: int, settings: dict[str, Any]) -> None:
        self.stored = settings


@pytest.fixture
def stored(monkeypatch: pytest.MonkeyPatch) -> _FakeSettingsRepository:
    fake = _FakeSettingsRepository()
    monkeypatch.setattr(repository, "settings", fake)
    monkeypatch.setattr(UserManager, "get_user_id", classmethod(lambda *_: 1))
    return fake


@pytest.fixture
def client(stored: _FakeSettingsRepository) -> Iterator[TestClient]:
    app = FastAPI()
    app.include_router(settings_router)
    app.dependency_overrides[get_client_id] = uuid4
    yield TestClient(app)


@pytest.mark.parametrize("enabled", [False, True])
def test_get_reports_the_server_debug_mode(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, enabled: bool
) -> None:
    monkeypatch.setattr(config.toml.debug, "enabled", enabled)

    assert client.get("/api/settings").json()["debug"] is enabled


def test_put_does_not_store_a_debug_sent_by_the_client(
    client: TestClient, stored: _FakeSettingsRepository, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(config.toml.debug, "enabled", False)

    response = client.put("/api/settings", json={**PREFERENCES, "debug": True})

    assert "debug" not in stored.stored
    assert response.json()["debug"] is False


def test_server_value_wins_over_a_stale_stored_one(
    client: TestClient, stored: _FakeSettingsRepository, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(config.toml.debug, "enabled", False)
    stored.stored = {**PREFERENCES, "debug": True}

    assert client.get("/api/settings").json()["debug"] is False
