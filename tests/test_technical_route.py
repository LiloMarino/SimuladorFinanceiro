"""`/api/variable-income/{ativo}/indicators` calcula sobre o histórico do gráfico do ativo."""

from __future__ import annotations

from datetime import date, timedelta
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core.dependencies.simulation import get_active_simulation
from backend.core.dto.stock_price_history import StockPriceHistoryDTO
from backend.routes.operation import operation_router

START = date(2023, 1, 2)
DAYS = 40


def candle(day: int) -> StockPriceHistoryDTO:
    price = 30 + day * 0.1
    return StockPriceHistoryDTO(
        price_date=START + timedelta(days=day),
        open=price,
        high=price + 0.5,
        low=price - 0.5,
        close=price,
        volume=1000,
    )


@pytest.fixture
def client() -> TestClient:
    # O detalhe da partida já termina na data da simulação: é o histórico do gráfico
    history = [candle(day) for day in range(DAYS)]
    simulation = SimpleNamespace(
        get_stock_details=lambda ticker: (
            SimpleNamespace(history=history) if ticker == "PETR4" else None
        )
    )
    app = FastAPI()
    app.include_router(operation_router)
    app.dependency_overrides[get_active_simulation] = lambda: simulation
    return TestClient(app)


def test_the_summary_and_the_series_end_on_the_last_day_of_the_chart(
    client: TestClient,
):
    response = client.post(
        "/api/variable-income/PETR4/indicators", json={"series": ["rsi", "averages"]}
    )

    body = response.json()
    last_day = (START + timedelta(days=DAYS - 1)).isoformat()
    assert response.status_code == 200
    assert body["summary"]["date"] == last_day
    assert body["series"]["rsi"][-1]["date"] == last_day
    assert body["series"]["averages"][0]["points"][-1]["date"] == last_day
    assert body["series"]["macd"] is None


def test_the_parameters_sent_change_the_reading(client: TestClient):
    response = client.post(
        "/api/variable-income/PETR4/indicators",
        json={"params": {"rsi_period": 9}, "series": []},
    )

    labels = [r["label"] for r in response.json()["summary"]["readings"]]
    assert "IFR 9" in labels


def test_parameters_out_of_order_are_rejected(client: TestClient):
    response = client.post(
        "/api/variable-income/PETR4/indicators",
        json={"params": {"macd_fast": 30, "macd_slow": 26}},
    )

    assert response.status_code == 422


def test_an_unknown_asset_is_not_found(client: TestClient):
    response = client.post("/api/variable-income/XXXX3/indicators", json={})

    assert response.status_code == 404
