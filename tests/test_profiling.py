"""Cada perfil do modo debug grava só o que o dono dele executou, em qualquer thread."""

from __future__ import annotations

import pstats
import threading
from collections import deque
from collections.abc import Iterator
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

from backend import config
from backend.core import profiling
from backend.core.dependencies import get_current_user
from backend.core.dto.user import UserDTO
from backend.core.profiling import mark_engine_thread, profile_routes
from backend.routes.debug import debug_router


def heavy_report() -> int:
    return sum(n * n for n in range(1000))


def engine_tick() -> int:
    return sum(n * n for n in range(1000))


def bystander() -> int:
    return sum(n * n for n in range(1000))


def functions_in(path: str | Path) -> set[str]:
    return {name for _, _, name in pstats.Stats(str(path)).stats}  # pyright: ignore[reportAttributeAccessIssue]


def run_in_thread(target, *, engine: bool = False) -> None:
    def body() -> None:
        if engine:
            mark_engine_thread()
        target()

    thread = threading.Thread(target=body)
    thread.start()
    thread.join()


@pytest.fixture(autouse=True)
def profiles_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    monkeypatch.setattr(profiling, "PROFILES_DIR", tmp_path / "profiles")
    monkeypatch.setattr(profiling, "profiler", profiling.Profiler())
    yield tmp_path / "profiles"
    profiling.profiler.set_routes_enabled(False)
    profiling.profiler.stop_engine()


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(config.toml.debug, "enabled", True)
    monkeypatch.setattr(config.toml.host, "nickname", "host")
    monkeypatch.setattr("backend.routes.debug.profiler", profiling.profiler)
    app = FastAPI()

    # A rota vem de um router incluído, como as da API
    router = APIRouter(prefix="/api")

    @router.get("/report/{name}")
    def report(name: str) -> int:
        return heavy_report()

    app.include_router(router)
    app.include_router(debug_router)
    app.dependency_overrides[get_current_user] = lambda: UserDTO(
        id=1, nickname="host", client_id=uuid4()
    )
    profile_routes(app)
    return TestClient(app)


def route_profiles(client: TestClient) -> list[dict]:
    return client.get("/api/debug/profile/routes").json()["items"]


def test_route_profile_has_only_the_request(client: TestClient) -> None:
    assert (
        client.put("/api/debug/profile/routes", json={"enabled": True}).status_code
        == 204
    )

    client.get("/api/report/a")
    run_in_thread(bystander)

    (entry,) = route_profiles(client)
    assert entry["route"] == "GET /api/report/{name}"
    names = functions_in(entry["file"])
    assert "heavy_report" in names
    assert "bystander" not in names
    assert "run_endpoint_function" not in names


def test_routes_off_records_nothing(client: TestClient, profiles_dir: Path) -> None:
    client.get("/api/report/a")

    assert client.get("/api/debug/profile/routes").json() == {
        "enabled": False,
        "items": [],
    }
    assert not profiles_dir.exists()


def test_route_list_keeps_the_latest(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(profiling.profiler, "_entries", deque(maxlen=2))
    client.put("/api/debug/profile/routes", json={"enabled": True})

    for name in ("a", "b", "c"):
        client.get(f"/api/report/{name}")

    entries = route_profiles(client)
    assert len(entries) == 2
    # O mais antigo sai da lista e do disco
    assert entries[0]["id"] > entries[1]["id"]
    assert len(list(profiling.PROFILES_DIR.glob("*.prof"))) == 2


def test_engine_profile_has_only_the_engine_thread(client: TestClient) -> None:
    assert client.post("/api/debug/profile/engine/start").status_code == 204
    assert client.get("/api/debug/profile/engine").json() == {"recording": True}

    run_in_thread(engine_tick, engine=True)
    run_in_thread(bystander)
    saved = client.post("/api/debug/profile/engine/stop").json()["file"]

    assert client.get("/api/debug/profile/engine").json() == {"recording": False}
    names = functions_in(saved)
    assert "engine_tick" in names
    assert "bystander" not in names


def test_engine_and_routes_record_side_by_side(client: TestClient) -> None:
    client.post("/api/debug/profile/engine/start")
    client.put("/api/debug/profile/routes", json={"enabled": True})

    client.get("/api/report/a")
    run_in_thread(engine_tick, engine=True)
    saved = client.post("/api/debug/profile/engine/stop").json()["file"]

    assert "heavy_report" not in functions_in(saved)
    (entry,) = route_profiles(client)
    assert "engine_tick" not in functions_in(entry["file"])


def test_engine_start_twice_and_stop_without_recording_are_refused(
    client: TestClient,
) -> None:
    assert client.post("/api/debug/profile/engine/stop").status_code == 409
    client.post("/api/debug/profile/engine/start")
    assert client.post("/api/debug/profile/engine/start").status_code == 409


def test_engine_stop_without_any_day_saves_no_file(client: TestClient) -> None:
    client.post("/api/debug/profile/engine/start")

    assert client.post("/api/debug/profile/engine/stop").json() == {"file": None}
