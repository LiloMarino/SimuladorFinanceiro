"""A versão do app vem do `pyproject.toml`, a única fonte."""

import re
import tomllib
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core.version import get_version
from backend.routes.version import version_router

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def test_version_matches_pyproject() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    assert get_version() == pyproject["project"]["version"]


def test_version_is_semver() -> None:
    assert SEMVER.match(get_version())


def test_version_route_returns_version() -> None:
    app = FastAPI()
    app.include_router(version_router)

    response = TestClient(app).get("/api/version")

    assert response.status_code == 200
    assert response.json() == {"version": get_version()}
