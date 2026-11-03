"""Cada perfil do modo debug grava só o que o dono dele executou, em qualquer thread."""

from __future__ import annotations

import pstats
import threading
import time
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
    def report(name: str, wait: float = 0) -> int:
        time.sleep(wait)
        return heavy_report()

    app.include_router(router)
    app.include_router(debug_router)
    app.dependency_overrides[get_current_user] = lambda: UserDTO(
        id=1, nickname="host", client_id=uuid4()
    )
    profile_routes(app)
    return TestClient(app)


def route_profiles(client: TestClient) -> list[dict]:
    return client.get("/api/debug/profile/routes").json()["routes"]


def test_route_profile_has_only_the_request(client: TestClient) -> None:
    assert (
        client.put("/api/debug/profile/routes", json={"enabled": True}).status_code
        == 204
    )

    client.get("/api/report/a")
    run_in_thread(bystander)

    (group,) = route_profiles(client)
    assert group["route"] == "GET /api/report/{name}"
    (entry,) = group["profiles"]
    names = functions_in(entry["file"])
    assert "heavy_report" in names
    assert "bystander" not in names
    assert "run_endpoint_function" not in names


def test_routes_off_records_nothing(client: TestClient, profiles_dir: Path) -> None:
    client.get("/api/report/a")

    assert client.get("/api/debug/profile/routes").json() == {
        "enabled": False,
        "routes": [],
    }
    assert not profiles_dir.exists()


def test_each_route_keeps_its_slowest_requests(client: TestClient) -> None:
    client.put("/api/debug/profile/routes", json={"enabled": True})

    # O relógio é o de parede: a espera do sleep conta na duração
    for wait in (0.01, 0.06, 0.03, 0.05, 0.02):
        client.get(f"/api/report/a?wait={wait}")

    (group,) = route_profiles(client)
    durations = [entry["duration_ms"] for entry in group["profiles"]]
    assert len(durations) == 3
    assert durations == sorted(durations, reverse=True)
    assert durations[-1] >= 30
    # As que saíram da lista saem também do disco
    assert len(list(profiling.PROFILES_DIR.glob("*.prof"))) == 3


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
    (group,) = route_profiles(client)
    assert "engine_tick" not in functions_in(group["profiles"][0]["file"])


def test_engine_start_twice_and_stop_without_recording_are_refused(
    client: TestClient,
) -> None:
    assert client.post("/api/debug/profile/engine/stop").status_code == 409
    client.post("/api/debug/profile/engine/start")
    assert client.post("/api/debug/profile/engine/start").status_code == 409


def test_engine_stop_without_any_day_saves_no_file(client: TestClient) -> None:
    client.post("/api/debug/profile/engine/start")

    assert client.post("/api/debug/profile/engine/stop").json() == {"file": None}
