"""Rotas das gestoras sem banco: expansão desligada, permissões, tetos de taxa e a conta que opera."""

from __future__ import annotations

import threading
from collections.abc import Iterator
from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import Any, ClassVar, cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core.dto.simulation import SimulationDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import AssetClass, OrderAction
from backend.core.exceptions.http_exceptions import ConflictError
from backend.features.simulation.simulation import Simulation
from backend.features.variable_income.entities.order import MarketOrder
from backend.routes.dependencies import ActingClient, get_current_user
from backend.routes.dependencies.auth import get_client_id
from backend.routes.dependencies.simulation import get_active_simulation
from backend.routes.funds import funds_router
from tests.fakes import client

ANA = UserDTO(id=1, client_id=client("ana"), nickname="Ana")
BRUNO = UserDTO(id=2, client_id=client("bruno"), nickname="Bruno")
ANA_FUND = client("fundo-da-ana")
FOUND_BODY = {
    "name": "Aura",
    "ticker": "AURA11",
    "management_fee": "0.01",
    "performance_fee": "0.10",
}
DISABLED = "Esta partida não usa a expansão Gestoras."


class _Book:
    """O livro de gestoras com o que as rotas leem: a gestora da Ana, de id 5."""

    client_ids: ClassVar[list] = [ANA_FUND]

    def by_id(self, fund_id: int) -> Any:
        if fund_id != 5:
            raise ConflictError("Gestora não encontrada")
        return SimpleNamespace(
            terms=SimpleNamespace(manager_user_id=ANA.id),
            account=SimpleNamespace(client_id=ANA_FUND),
        )


def _simulation(funds: object | None) -> Simulation:
    simulation = object.__new__(Simulation)
    simulation._engine = SimpleNamespace(  # type: ignore[assignment]
        _lock=threading.RLock(), asset_class=lambda _ticker: AssetClass.FUND
    )
    simulation.settings = cast(
        "SimulationDTO",
        SimpleNamespace(
            fund_max_management_fee=Decimal("0.02"),
            fund_max_performance_fee=Decimal("0.20"),
        ),
    )
    simulation._funds = funds  # type: ignore[assignment]
    simulation._client_of_user = lambda user_id: (
        ANA.client_id if user_id == ANA.id else BRUNO.client_id
    )
    return simulation


def _app(simulation: Simulation, user: UserDTO) -> TestClient:
    app = FastAPI()
    app.include_router(funds_router)

    @app.get("/acting")
    def acting(account: ActingClient) -> str:
        return str(account)

    app.dependency_overrides[get_active_simulation] = lambda: simulation
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_client_id] = lambda: user.client_id
    return TestClient(app)


@pytest.fixture
def disabled() -> Iterator[TestClient]:
    yield _app(_simulation(None), ANA)


@pytest.fixture
def with_funds() -> Iterator[TestClient]:
    yield _app(_simulation(_Book()), ANA)


@pytest.mark.parametrize(
    ("method", "path", "body"),
    [
        ("get", "/api/funds", None),
        ("get", "/api/funds/5", None),
        ("post", "/api/funds", FOUND_BODY),
        ("post", "/api/funds/5/contributions", {"cash": "100"}),
        ("post", "/api/funds/5/offer", {"quotas": 10}),
        ("delete", "/api/funds/5/offer", None),
        (
            "put",
            "/api/funds/5/fees",
            {"management_fee": "0.01", "performance_fee": "0.10"},
        ),
    ],
)
def test_every_route_is_refused_when_the_expansion_is_off(
    disabled: TestClient, method: str, path: str, body: dict | None
):
    response = disabled.request(method, path, json=body)

    assert response.status_code == 409
    assert response.json()["detail"] == DISABLED


@pytest.mark.parametrize("ticker", ["ABC11", "ABCD12", "abcd11", "ABCD3", "ABCDE11"])
def test_ticker_outside_four_letters_and_suffix_eleven_is_unprocessable(
    with_funds: TestClient, ticker: str
):
    response = with_funds.post("/api/funds", json={**FOUND_BODY, "ticker": ticker})

    assert response.status_code == 422


def test_fee_above_the_match_ceiling_is_unprocessable(with_funds: TestClient):
    response = with_funds.post(
        "/api/funds", json={**FOUND_BODY, "management_fee": "0.03"}
    )

    assert response.status_code == 422
    assert "administração" in response.json()["detail"]


def test_performance_fee_above_the_match_ceiling_is_unprocessable(
    with_funds: TestClient,
):
    response = with_funds.put(
        "/api/funds/5/fees",
        json={"management_fee": "0.01", "performance_fee": "0.25"},
    )

    assert response.status_code == 422
    assert "performance" in response.json()["detail"]


@pytest.mark.parametrize(
    ("method", "path", "body"),
    [
        ("post", "/api/funds/5/contributions", {"cash": "100"}),
        ("post", "/api/funds/5/offer", {"quotas": 10}),
        ("delete", "/api/funds/5/offer", None),
        (
            "put",
            "/api/funds/5/fees",
            {"management_fee": "0.01", "performance_fee": "0.10"},
        ),
    ],
)
def test_only_the_manager_operates_the_fund(method: str, path: str, body: dict | None):
    other = _app(_simulation(_Book()), BRUNO)

    response = other.request(method, path, json=body)

    assert response.status_code == 403


def test_acting_client_without_the_header_is_the_player(with_funds: TestClient):
    assert with_funds.get("/acting").json() == str(ANA.client_id)


def test_acting_client_with_the_header_is_the_fund_of_the_manager(
    with_funds: TestClient,
):
    response = with_funds.get("/acting", headers={"X-Account": "5"})

    assert response.json() == str(ANA_FUND)


def test_acting_client_with_the_header_of_a_fund_run_by_someone_else_is_forbidden():
    other = _app(_simulation(_Book()), BRUNO)

    response = other.get("/acting", headers={"X-Account": "5"})

    assert response.status_code == 403


def test_fund_account_does_not_buy_fund_quotas(monkeypatch: pytest.MonkeyPatch):
    simulation = _simulation(_Book())
    monkeypatch.setattr(Simulation, "_ensure_can_operate", lambda *_: None)
    order = MarketOrder(
        client_id=ANA_FUND,
        ticker="ZETA11",
        size=Decimal(1),
        action=OrderAction.BUY,
        placed_on=date(2020, 1, 6),
    )

    with pytest.raises(ConflictError, match="não compra cota de gestora"):
        simulation.create_order(order)
