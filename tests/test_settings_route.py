"""`/api/settings` mostra o modo debug do servidor e nunca o grava no usuário."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend import config
from backend.config.paths import app_files_dir
from backend.core import repository
from backend.core.dependencies import get_client_id, get_current_user, verify_host
from backend.core.dto.user import UserDTO
from backend.core.runtime.user_manager import UserManager
from backend.routes import settings as settings_route
from backend.routes.settings import settings_router

PREFERENCES = {
    "notifications": {
        "news_position": "STRIP",
        "news": {"TERM_STARTED": "WINDOW"},
        "toasts": {"ORDER_EXECUTED": False},
    },
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


def test_settings_stored_before_the_indicators_get_them_with_nothing_on(
    client: TestClient, stored: _FakeSettingsRepository
) -> None:
    stored.stored = PREFERENCES

    indicators = client.get("/api/settings").json()["indicators"]

    assert indicators["visible"] == []
    assert indicators["params"]["rsi_period"] == 14


def test_put_stores_the_chosen_indicators(
    client: TestClient, stored: _FakeSettingsRepository
) -> None:
    chosen = {"visible": ["rsi"], "params": {"rsi_period": 9}}

    client.put("/api/settings", json={**PREFERENCES, "indicators": chosen})

    assert stored.stored["indicators"]["visible"] == ["rsi"]
    assert stored.stored["indicators"]["params"]["rsi_period"] == 9


def test_server_value_wins_over_a_stale_stored_one(
    client: TestClient, stored: _FakeSettingsRepository, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(config.toml.debug, "enabled", False)
    stored.stored = {**PREFERENCES, "debug": True}

    assert client.get("/api/settings").json()["debug"] is False


def test_notifications_fill_every_type_with_the_registry_default(
    client: TestClient, stored: _FakeSettingsRepository
) -> None:
    stored.stored = PREFERENCES

    notifications = client.get("/api/settings").json()["notifications"]

    assert notifications["news_position"] == "STRIP"
    assert notifications["news"]["TERM_STARTED"] == "WINDOW"
    assert notifications["news"]["PARTY_LIFE"] == "JOURNAL"
    assert notifications["toasts"]["ORDER_EXECUTED"] is False
    assert notifications["toasts"]["ORDER_PARTIAL"] is True


def test_a_fixed_news_type_keeps_its_level(
    client: TestClient, stored: _FakeSettingsRepository
) -> None:
    stored.stored = {"notifications": {"news": {"ELECTION_RESULT": "OFF"}}}

    news = client.get("/api/settings").json()["notifications"]["news"]

    assert news["ELECTION_RESULT"] == "WINDOW"


def test_put_stores_the_notification_choices_as_json(
    client: TestClient, stored: _FakeSettingsRepository
) -> None:
    client.put("/api/settings", json=PREFERENCES)

    assert stored.stored["notifications"]["news"] == {"TERM_STARTED": "WINDOW"}
    assert stored.stored["notifications"]["toasts"] == {"ORDER_EXECUTED": False}


def test_notification_types_list_the_registry_in_importance_order(
    client: TestClient,
) -> None:
    catalog = client.get("/api/settings/notification-types").json()

    assert catalog["news"][0]["type"] == "ELECTION_RESULT"
    assert catalog["news"][0]["fixed"] is True
    assert [s["section"] for s in catalog["sections"]] == [
        "ECONOMY",
        "COMPANIES",
        "POLITICS",
        "HISTORY",
    ]
    assert catalog["default_position"] == "BOTTOM_LEFT"


class _FolderOpener:
    def __init__(self) -> None:
        self.opened: list[Path] = []
        self.succeeds = True

    def __call__(self, folder: Path) -> bool:
        self.opened.append(folder)
        return self.succeeds


@pytest.fixture
def opener(monkeypatch: pytest.MonkeyPatch) -> _FolderOpener:
    fake = _FolderOpener()
    monkeypatch.setattr(settings_route, "open_in_file_manager", fake)
    return fake


def _folder_client(host: str, *, is_host: bool = True) -> TestClient:
    app = FastAPI()
    app.include_router(settings_router)
    app.dependency_overrides[get_client_id] = uuid4
    if is_host:
        app.dependency_overrides[verify_host] = lambda: None
    else:
        app.dependency_overrides[get_current_user] = lambda: UserDTO(
            id=1, client_id=uuid4(), nickname="convidado"
        )
    return TestClient(app, client=(host, 50000))


@pytest.mark.parametrize(
    ("target", "expected"),
    [
        ("config", app_files_dir().resolve()),
        ("logs", (app_files_dir() / config.toml.logging.logs_path).resolve()),
    ],
)
def test_open_folder_opens_the_requested_folder(
    opener: _FolderOpener, target: str, expected: Path
) -> None:
    response = _folder_client("127.0.0.1").post(
        "/api/settings/open-folder", params={"target": target}
    )

    assert response.status_code == 204
    assert opener.opened == [expected]


def test_open_folder_accepts_ipv6_loopback(opener: _FolderOpener) -> None:
    response = _folder_client("::1").post("/api/settings/open-folder")

    assert response.status_code == 204


def test_open_folder_refuses_a_request_from_another_ip(opener: _FolderOpener) -> None:
    response = _folder_client("192.168.0.20").post("/api/settings/open-folder")

    assert response.status_code == 403
    assert opener.opened == []


def test_open_folder_refuses_who_is_not_the_host(
    opener: _FolderOpener, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(config.toml.host, "nickname", "dono")

    response = _folder_client("127.0.0.1", is_host=False).post(
        "/api/settings/open-folder"
    )

    assert response.status_code == 403
    assert opener.opened == []


def test_open_folder_answers_409_with_the_path_when_it_cannot_open(
    opener: _FolderOpener,
) -> None:
    opener.succeeds = False

    response = _folder_client("127.0.0.1").post("/api/settings/open-folder")

    assert response.status_code == 409
    assert str(app_files_dir().resolve()) in response.json()["detail"]


def test_folders_lists_the_paths_for_the_host(opener: _FolderOpener) -> None:
    response = _folder_client("127.0.0.1").get("/api/settings/folders")

    assert response.json() == {
        "config": str(app_files_dir().resolve()),
        "logs": str((app_files_dir() / config.toml.logging.logs_path).resolve()),
    }
