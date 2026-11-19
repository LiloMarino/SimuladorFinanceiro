"""Rota do automático: os parâmetros com que o jogador liga a estratégia ficam salvos no perfil."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core import repository
from backend.core.dto.strategy import StrategyParamValue
from backend.core.dto.user import UserDTO
from backend.core.exceptions.http_exceptions import UnprocessableEntityError
from backend.routes.dependencies import get_current_user
from backend.routes.dependencies.simulation import get_active_simulation
from backend.routes.funds import funds_router
from backend.routes.strategy import strategy_router
from tests.fakes import client

ALICE = UserDTO(id=1, client_id=client("alice"), nickname="Alice")
CROSS = {"short_window": 20, "long_window": 100, "cash_pct": 30, "tickers": ["PETR4"]}


class _Simulation:
    def set_my_strategy(
        self, _user: UserDTO, _key: str | None, params: dict[str, StrategyParamValue]
    ) -> None:
        if params.get("short_window") == 1:
            raise UnprocessableEntityError("A média curta vai de 5 a 100.")


class _Profile:
    def __init__(self) -> None:
        self.saved: dict[int, dict[str, dict[str, StrategyParamValue]]] = {}

    def set_strategy_params(
        self, user_id: int, key: str, params: dict[str, StrategyParamValue]
    ) -> None:
        self.saved.setdefault(user_id, {})[key] = params


@pytest.fixture
def profile(monkeypatch: pytest.MonkeyPatch) -> _Profile:
    fake = _Profile()
    monkeypatch.setattr(repository, "settings", fake)
    return fake


@pytest.fixture
def http(profile: _Profile) -> Iterator[TestClient]:
    app = FastAPI()
    app.include_router(strategy_router)
    app.dependency_overrides[get_active_simulation] = _Simulation
    app.dependency_overrides[get_current_user] = lambda: ALICE
    yield TestClient(app)


def test_turning_on_saves_the_params_in_the_profile(
    http: TestClient, profile: _Profile
):
    http.put(
        "/api/strategies/me", json={"key": "moving_average_cross", "params": CROSS}
    )

    assert profile.saved == {ALICE.id: {"moving_average_cross": CROSS}}


def test_going_back_to_manual_keeps_the_saved_params(
    http: TestClient, profile: _Profile
):
    http.put("/api/strategies/me", json={"key": None})

    assert profile.saved == {}


def test_params_the_match_refuses_are_not_saved(http: TestClient, profile: _Profile):
    answer = http.put(
        "/api/strategies/me",
        json={"key": "moving_average_cross", "params": {**CROSS, "short_window": 1}},
    )

    assert answer.status_code == 422
    assert profile.saved == {}


class _FundSimulation:
    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def get_strategies(self, for_fund: bool = False) -> list:
        self.calls.append(("list", for_fund))
        return []

    def set_fund_strategy(
        self,
        user: UserDTO,
        fund_id: int,
        key: str | None,
        params: dict[str, StrategyParamValue],
    ) -> None:
        self.calls.append(("set", user.id, fund_id, key, params))


def test_the_fund_strategy_is_set_without_touching_the_player_profile(
    profile: _Profile,
):
    fake = _FundSimulation()
    app = FastAPI()
    app.include_router(strategy_router)
    app.include_router(funds_router)
    app.dependency_overrides[get_active_simulation] = lambda: fake
    app.dependency_overrides[get_current_user] = lambda: ALICE
    http = TestClient(app)

    listed = http.get("/api/strategies", params={"fund": True})
    answer = http.put(
        "/api/funds/5/strategy",
        json={"key": "moving_average_cross", "params": CROSS},
    )

    assert listed.status_code == 200
    assert answer.status_code == 204
    assert fake.calls == [
        ("list", True),
        ("set", ALICE.id, 5, "moving_average_cross", CROSS),
    ]
    assert profile.saved == {}
