"""Os perfis do modo debug gravam o `.prof` de quem trabalha, em qualquer thread."""

from __future__ import annotations

import pstats
import threading
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
from backend.core.profiling import ProfileRequestMiddleware, profile_routes, profiler
from backend.routes.debug import debug_router


def heavy_report() -> int:
    return sum(n * n for n in range(1000))


def worker_tick() -> int:
    return sum(n * n for n in range(1000))


def functions_in(path: Path) -> set[str]:
    return {name for _, _, name in pstats.Stats(str(path)).stats}  # pyright: ignore[reportAttributeAccessIssue]


@pytest.fixture(autouse=True)
def profiles_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    monkeypatch.setattr(profiling, "PROFILES_DIR", tmp_path / "profiles")
    yield tmp_path / "profiles"
    profiler.stop()


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(config.toml.debug, "enabled", True)
    monkeypatch.setattr(config.toml.host, "nickname", "host")
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
    app.add_middleware(ProfileRequestMiddleware)
    return TestClient(app)


def test_request_with_profile_records_the_handler(
    client: TestClient, profiles_dir: Path
) -> None:
    assert client.get("/api/report/a?profile=1").status_code == 200

    (saved,) = profiles_dir.glob("get-api-report-name-*.prof")
    names = functions_in(saved)
    assert "heavy_report" in names
    assert "run_endpoint_function" not in names


def test_request_without_profile_records_nothing(
    client: TestClient, profiles_dir: Path
) -> None:
    client.get("/api/report/a")

    assert not profiles_dir.exists()


def test_engine_profile_sees_the_work_of_another_thread(
    client: TestClient, profiles_dir: Path
) -> None:
    assert client.post("/api/debug/profile/engine/start").status_code == 204
    assert client.get("/api/debug/profile/engine").json() == {"recording": True}

    loop = threading.Thread(target=worker_tick, name="simulation-loop")
    loop.start()
    loop.join()
    saved = client.post("/api/debug/profile/engine/stop").json()["file"]

    assert client.get("/api/debug/profile/engine").json() == {"recording": False}
    assert Path(saved).parent == profiles_dir
    assert "worker_tick" in functions_in(Path(saved))


def test_only_one_profile_runs_at_a_time(client: TestClient) -> None:
    assert client.post("/api/debug/profile/engine/start").status_code == 204
    assert client.post("/api/debug/profile/engine/start").status_code == 409
    # O perfil da requisição não derruba o do motor
    assert client.get("/api/report/a?profile=1").status_code == 200
    assert profiler.active


def test_stop_without_recording_is_refused(client: TestClient) -> None:
    assert client.post("/api/debug/profile/engine/stop").status_code == 409
