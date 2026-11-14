"""A carteira segue a conta ativa: o header X-Account nas rotas e o tempo real marcado com a gestora."""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core import repository
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.simulation import simulation as simulation_module
from backend.features.simulation import simulation_engine as engine_module
from backend.features.simulation.simulation import Simulation
from backend.features.variable_income import broker as broker_module
from backend.routes.dependencies import get_current_user
from backend.routes.dependencies.auth import get_client_id
from backend.routes.dependencies.simulation import get_active_simulation
from backend.routes.portfolio import portfolio_router
from tests.test_fund_routes import ANA, ANA_FUND, BRUNO, _Book, _simulation
from tests.test_fund_simulation import TICKER, fund_match
from tests.test_simulation_loader import started  # noqa: F401

CASH = {ANA.client_id: Decimal(100), ANA_FUND: Decimal(5000)}


def _client(user: Any) -> TestClient:
    simulation: Simulation = _simulation(_Book())
    queried: list = []
    simulation._engine.get_cash = lambda client_id: CASH[client_id]
    simulation.get_cash = simulation._engine.get_cash
    simulation._engine.get_positions = lambda client_id: queried.append(client_id) or {}
    simulation._queried = queried  # type: ignore[attr-defined]
    app = FastAPI()
    app.include_router(portfolio_router)
    app.dependency_overrides[get_active_simulation] = lambda: simulation
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_client_id] = lambda: user.client_id
    test_client = TestClient(app)
    test_client.simulation = simulation  # type: ignore[attr-defined]
    return test_client


@pytest.fixture
def ana() -> Iterator[TestClient]:
    yield _client(ANA)


def test_cash_without_the_header_is_the_personal_one(ana: TestClient):
    assert ana.get("/api/portfolio/cash").json() == {"cash": "100"}


def test_cash_with_the_header_is_the_fund_cash(ana: TestClient):
    response = ana.get("/api/portfolio/cash", headers={"X-Account": "5"})

    assert response.json() == {"cash": "5000"}


def test_position_with_the_header_is_read_from_the_fund_account(ana: TestClient):
    ana.get("/api/portfolio/PETR4", headers={"X-Account": "5"})
    ana.get("/api/portfolio/PETR4")

    assert ana.simulation._queried == [ANA_FUND, ANA.client_id]  # type: ignore[attr-defined]


def test_portfolio_of_a_fund_run_by_someone_else_is_forbidden():
    other = _client(BRUNO)

    response = other.get("/api/portfolio/cash", headers={"X-Account": "5"})

    assert response.status_code == 403


class _Sent:
    """Os avisos de tempo real da partida, em ordem: (evento, conta do aviso, a quem vai)."""

    def __init__(self) -> None:
        self.items: list[tuple[str, int | None, Any]] = []

    def __call__(self, event: str, payload: dict, to: Any = None) -> None:
        self.items.append((event, payload.get("account"), to))

    def of(self, event: str) -> list[tuple[int | None, Any]]:
        return [(account, to) for name, account, to in self.items if name == event]


@pytest.fixture
def sent(monkeypatch: pytest.MonkeyPatch) -> _Sent:
    sent = _Sent()
    for module in (engine_module, simulation_module, broker_module):
        monkeypatch.setattr(module, "notify", sent)
    return sent


@pytest.fixture
def match(started):  # noqa: F811
    return fund_match()


def test_fund_cash_goes_to_the_manager_marked_with_the_fund(match, sent: _Sent):
    sim, user_id = match
    assert sim._funds is not None
    fund = sim._funds.get(TICKER)
    manager = next(
        u
        for u in repository.simulation_player.participants(sim.settings.id)
        if u.id == user_id
    )

    sim._engine.add_cash(fund.account.client_id, Decimal(10))
    sim._engine.add_cash(manager.client_id, Decimal(10))
    EventManager.flush()

    assert sent.of("cash_update") == [
        (fund.terms.id, manager.client_id),
        (None, manager.client_id),
    ]


def test_tick_sends_one_portfolio_per_account_the_player_runs(match, sent: _Sent):
    sim, user_id = match
    assert sim._funds is not None
    fund = sim._funds.get(TICKER)
    manager = next(
        u
        for u in repository.simulation_player.participants(sim.settings.id)
        if u.id == user_id
    )
    sent.items.clear()

    sim.next_tick()

    assert sent.of("portfolio_update") == [
        (None, manager.client_id),
        (fund.terms.id, manager.client_id),
    ]


def test_fund_portfolio_reads_the_fund_cash(match):
    sim, _ = match
    assert sim._funds is not None
    fund = sim._funds.get(TICKER)

    portfolio = sim.get_portfolio(fund.account.client_id)

    assert portfolio.cash == sim._engine.get_cash(fund.account.client_id)
    assert SimulationManager.find_fund_name(fund.account.client_id) == "Aura"
