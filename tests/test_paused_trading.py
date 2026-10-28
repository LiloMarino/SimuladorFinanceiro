"""Operações HTTP de dois jogadores, sem depender de um tick para atualizar o estado."""

from __future__ import annotations

import threading
import uuid
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from backend.core import repository
from backend.core.dto.simulation import SimulationDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import PauseReason
from backend.core.player_colors import PLAYER_COLORS
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.simulation.simulation import Simulation
from backend.routes.operation import operation_router
from backend.routes.portfolio import portfolio_router
from backend.routes.timespeed import timespeed_router
from tests.fakes import simulation_settings


@pytest.fixture
def paused_match(
    market: Engine, monkeypatch: pytest.MonkeyPatch
) -> Iterator[tuple[Simulation, list[UserDTO], TestClient]]:
    users = [repository.user.create_user(uuid.uuid4(), name) for name in ("Ana", "Bia")]
    monkeypatch.setattr(UserManager, "_active_players", {u.client_id: u for u in users})
    monkeypatch.setattr(
        UserManager, "_client_user_cache", {u.client_id: u for u in users}
    )
    monkeypatch.setattr(SimulationManager, "_active_simulation", None)
    monkeypatch.setattr(SimulationManager, "_simulation_id", None)
    monkeypatch.setattr(EventManager, "_events", [])
    monkeypatch.setattr(EventManager, "_touched_users", set())
    monkeypatch.setattr(
        RealtimeBrokerManager,
        "get_broker",
        lambda: SimpleNamespace(notify=lambda *_a, **_kw: None),
    )
    settings = simulation_settings().model_copy(
        update={"start_date": date(2003, 3, 31), "end_date": date(2003, 6, 30)}
    )
    simulation_id = repository.simulation.create_simulation(settings)
    repository.simulation_player.save(
        simulation_id, {u.id: PLAYER_COLORS[i] for i, u in enumerate(users)}
    )
    repository.user.seed_simulation_users(
        simulation_id,
        [u.id for u in users],
        settings.start_date,
        settings.starting_cash,
    )
    SimulationManager.set_simulation_id(simulation_id)
    sim = Simulation(
        SimulationDTO(id=simulation_id, **settings.model_dump()), random_seed=7
    )
    SimulationManager.register_simulation(sim)
    app = FastAPI()
    app.include_router(operation_router)
    app.include_router(portfolio_router)
    app.include_router(timespeed_router)
    with TestClient(app) as client:
        yield sim, users, client


def test_two_players_can_buy_sell_and_read_history_while_paused(paused_match):
    sim, users, client = paused_match
    today = sim.get_current_date()
    for user in users:
        client.cookies.set("client_id", str(user.client_id))
        for action, held in [("buy", 0), ("sell", 1)]:
            preview = client.post(
                "/api/variable-income/BANK_A/order-preview",
                json={"action": action, "quantity": 1},
            )
            assert preview.status_code == 200, preview.text
            assert Decimal(preview.json()["held"]) == held
            result = client.post(
                "/api/variable-income/BANK_A/orders",
                json={"action": action, "type": "market", "quantity": 1},
            )
            assert result.status_code == 200, result.text
            assert result.json()["status"] == "EXECUTED"
            assert Decimal(result.json()["total"]) == Decimal(
                preview.json()["total"]
            ).quantize(Decimal("0.01"))
            position = client.get("/api/portfolio/BANK_A").json()
            assert Decimal(position["size"]) == (1 if action == "buy" else 0)
        assert sim.get_speed() == 0
        assert sim.get_current_date() == today
    trades = client.get("/api/variable-income/BANK_A/trades").json()
    assert len(trades) == 4
    assert {row["player_nickname"] for row in trades} == {"Ana", "Bia"}
    assert {row["event_date"] for row in trades} == {today.isoformat()}


def test_monthly_catalog_refresh_keeps_unmatured_open_offer_usable(paused_match):
    sim, users, client = paused_match
    client.cookies.set("client_id", str(users[0].client_id))
    # O CDB de liquidez diária fica a partida inteira; o resto da vitrine renova
    [original, *_] = [
        a
        for a in client.get("/api/fixed-income").json()
        if not (a["daily_liquidity"] and a["player_cap"] is None)
    ]
    asset_id = original["asset_uuid"]
    sim.next_tick()  # 31/mar -> 1/abr: a vitrine inteira muda.
    assert asset_id not in {
        a["asset_uuid"] for a in client.get("/api/fixed-income").json()
    }
    detail = client.get(f"/api/fixed-income/{asset_id}")
    assert detail.status_code == 200, detail.text
    assert detail.json()["maturity_date"] == original["maturity_date"]
    assert (
        client.get(f"/api/fixed-income/{asset_id}/projection?amount=100").status_code
        == 200
    )
    assert (
        client.post(
            f"/api/fixed-income/{asset_id}/buy", json={"quantity": "100"}
        ).status_code
        == 204
    )
    assert any(
        p["asset"]["asset_uuid"] == asset_id
        for p in client.get("/api/portfolio").json()["fixed_income"]
    )


def test_pause_confirmation_and_stock_read_wait_for_the_whole_day(
    paused_match, monkeypatch
):
    sim, users, client = paused_match
    client.cookies.set("client_id", str(users[0].client_id))
    entered, release, reading, pausing = (threading.Event() for _ in range(4))
    original = sim._engine.update_market_data

    def blocked(stocks):
        assert sim._engine.current_date == sim._current_date
        entered.set()
        assert release.wait(5)
        original(stocks)

    monkeypatch.setattr(sim._engine, "update_market_data", blocked)

    def read():
        reading.set()
        return client.get("/api/variable-income/BANK_A")

    def pause():
        pausing.set()
        return client.post("/api/set-speed", json={"speed": 0})

    with ThreadPoolExecutor(max_workers=3) as executor:
        tick = executor.submit(sim.next_tick)
        assert entered.wait(5)
        stock = executor.submit(read)
        stopped = executor.submit(pause)
        try:
            assert reading.wait(5) and pausing.wait(5)
            assert not stock.done() and not stopped.done()
        finally:
            release.set()
        tick.result(timeout=5)
        assert stock.result(timeout=5).status_code == 200
        assert stopped.result(timeout=5).status_code == 200
    assert sim._current_date == sim._engine.current_date == date(2003, 4, 1)


def test_matured_offer_cannot_be_projected_or_bought(paused_match):
    sim, users, client = paused_match
    client.cookies.set("client_id", str(users[0].client_id))
    asset = sim.get_fixed_assets()[0].model_copy(
        update={"maturity_date": sim.get_current_date()}
    )
    repository.fixed_income.get_or_create_asset(asset)
    asset_id = str(asset.asset_uuid)
    sim._engine.fixed_income_market._issued_assets[asset_id] = asset
    cash = sim.get_cash(users[0].client_id)
    assert (
        client.get(f"/api/fixed-income/{asset_id}/projection?amount=100").status_code
        == 409
    )
    assert (
        client.post(
            f"/api/fixed-income/{asset_id}/buy", json={"quantity": "100"}
        ).status_code
        == 409
    )
    assert sim.get_cash(users[0].client_id) == cash


def test_resting_order_executed_by_new_day_uses_that_days_date(paused_match):
    sim, users, client = paused_match
    client.cookies.set("client_id", str(users[0].client_id))
    sim._engine.matching_engine.market_liquidity._remove_old_orders("BANK_A")
    order = client.post(
        "/api/variable-income/BANK_A/orders",
        json={
            "action": "buy",
            "type": "limit",
            "quantity": 1,
            "limit_price": 10000,
        },
    )
    assert order.status_code == 200, order.text
    assert order.json()["status"] == "PENDING"
    sim.next_tick()
    trades = client.get("/api/variable-income/BANK_A/trades").json()
    assert len(trades) == 1
    assert trades[0]["event_date"] == "2003-04-01"


def test_state_reports_why_the_match_is_paused(paused_match):
    sim, users, client = paused_match
    client.cookies.set("client_id", str(users[0].client_id))

    assert client.get("/api/get-simulation-state").json()["pause_reason"] == "HOST"

    client.post("/api/set-speed", json={"speed": 4})
    assert client.get("/api/get-simulation-state").json()["pause_reason"] is None

    sim.set_speed(0, PauseReason.FIRST_ROUND_RESULT)
    state = client.get("/api/get-simulation-state").json()
    assert (state["speed"], state["pause_reason"]) == (0, "FIRST_ROUND_RESULT")

    # O host que pausa de novo assume o motivo da pausa
    client.post("/api/set-speed", json={"speed": 1})
    client.post("/api/set-speed", json={"speed": 0})
    assert client.get("/api/get-simulation-state").json()["pause_reason"] == "HOST"
