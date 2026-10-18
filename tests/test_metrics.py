"""O coletor do painel de desempenho mede só com o debug ligado."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend import config
from backend.core import metrics as metrics_module
from backend.core.dependencies import get_current_user
from backend.core.dto.user import UserDTO
from backend.core.metrics import (
    SLOW_MS,
    WINDOW_SIZE,
    Metrics,
    MetricsMiddleware,
    percentile_95,
)
from backend.routes import debug as debug_routes
from backend.routes.debug import debug_router


@pytest.fixture
def collector() -> Metrics:
    collector = Metrics()
    collector.enabled = True
    return collector


def stat(collector: Metrics, name: str):
    return next(s for s in collector.snapshot().stats if s.name == name)


def test_percentile_95_is_the_nearest_rank() -> None:
    assert percentile_95([float(n) for n in range(1, 101)]) == 95.0
    assert percentile_95([7.0]) == 7.0


def test_stat_summarises_the_calls(collector: Metrics) -> None:
    for duration in (10.0, 20.0, 30.0, 40.0):
        collector.record("http", "GET /api/x", duration)

    result = stat(collector, "GET /api/x")
    assert (result.calls, result.total_ms, result.mean_ms) == (4, 100.0, 25.0)
    assert (result.p95_ms, result.max_ms) == (40.0, 40.0)


def test_overall_p95_is_over_every_call_of_the_origin(collector: Metrics) -> None:
    for duration in range(1, 51):
        collector.record("http", "GET /api/a", float(duration))
        collector.record("http", "GET /api/b", float(duration + 50))
    collector.record("engine", "dia", 7.0)

    overall = collector.snapshot().overall_p95
    assert overall == {"http": 95.0, "engine": 7.0}


def test_only_the_last_thousand_measurements_count(collector: Metrics) -> None:
    for _ in range(WINDOW_SIZE):
        collector.record("http", "GET /api/x", 1.0)
    collector.record("http", "GET /api/x", 9.0)

    result = stat(collector, "GET /api/x")
    assert result.calls == WINDOW_SIZE
    assert result.total_ms == (WINDOW_SIZE - 1) * 1.0 + 9.0


def test_nothing_is_kept_while_disabled() -> None:
    collector = Metrics()

    collector.record("http", "GET /api/x", 5.0)
    collector.record_sent("event", 3, 100)
    with collector.measure("engine", "dia"):
        pass

    snapshot = collector.snapshot()
    assert snapshot.stats == [] and snapshot.traffic == []


def test_reset_clears_everything(collector: Metrics) -> None:
    collector.record("http", "GET /api/x", 5.0)
    collector.record_sent("event", 1, 10)

    collector.reset()

    snapshot = collector.snapshot()
    assert snapshot.stats == [] and snapshot.traffic == []


def test_sent_traffic_is_per_recipient_and_groups_dynamic_events(
    collector: Metrics,
) -> None:
    collector.record_sent("stock_update:PETR4", 4, 1000)
    collector.record_sent("stock_update:VALE3", 4, 1000)

    (traffic,) = collector.snapshot().traffic
    assert traffic.event == "stock_update:*"
    assert traffic.bytes_per_msg == 1000
    # 8 mensagens e 8.000 bytes sobre a janela mínima de 1 s
    assert (traffic.msgs_per_s, traffic.bytes_per_s) == (8.0, 8000.0)


def test_measure_records_even_when_the_block_raises(collector: Metrics) -> None:
    with pytest.raises(StopIteration), collector.measure("engine", "dia"):
        raise StopIteration

    assert stat(collector, "dia").calls == 1


def test_timed_keeps_the_function_name_and_works_with_sync_and_async(
    collector: Metrics,
) -> None:
    @collector.timed("socket", "sync")
    def sync_handler(value: int) -> int:
        return value + 1

    @collector.timed("socket", "async")
    async def async_handler(value: int) -> int:
        return value + 1

    assert sync_handler.__name__ == "sync_handler"
    assert async_handler.__name__ == "async_handler"
    assert sync_handler(1) == 2
    assert asyncio.run(async_handler(1)) == 2
    assert stat(collector, "sync").calls == stat(collector, "async").calls == 1


def test_slow_call_goes_to_the_slow_logger(
    collector: Metrics, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.WARNING, logger="backend.metrics"):
        collector.record("http", "GET /api/lenta", SLOW_MS + 1)
        collector.record("http", "GET /api/rapida", SLOW_MS - 1)

    assert "GET /api/lenta" in caplog.text
    assert "GET /api/rapida" not in caplog.text


# -- middleware ---------------------------------------------------------------


@pytest.fixture
def live(monkeypatch: pytest.MonkeyPatch) -> Metrics:
    collector = Metrics()
    collector.enabled = True
    monkeypatch.setattr(metrics_module, "metrics", collector)
    monkeypatch.setattr(debug_routes, "metrics", collector)
    return collector


@pytest.fixture
def client(live: Metrics) -> Iterator[TestClient]:
    app = FastAPI()

    @app.get("/api/stocks/{ticker}")
    def stock(ticker: str) -> dict[str, str]:  # type: ignore[reportUnusedFunction]
        return {"ticker": ticker}

    @app.get("/api/stream")
    def stream() -> dict[str, bool]:  # type: ignore[reportUnusedFunction]
        return {"ok": True}

    @app.get("/api/falha")
    def failure() -> None:  # type: ignore[reportUnusedFunction]
        raise RuntimeError("falhou")

    @app.get("/{path:path}")
    def spa(path: str) -> dict[str, str]:  # type: ignore[reportUnusedFunction]
        return {"path": path}

    app.add_middleware(MetricsMiddleware)
    yield TestClient(app, raise_server_exceptions=False)


def test_requests_are_grouped_by_the_declared_route(
    client: TestClient, live: Metrics
) -> None:
    client.get("/api/stocks/PETR4")
    client.get("/api/stocks/VALE3")

    assert stat(live, "GET /api/stocks/{ticker}").calls == 2


def test_response_carries_server_timing(client: TestClient) -> None:
    header = client.get("/api/stocks/PETR4").headers["server-timing"]

    assert header.startswith("app;dur=")


def test_stream_and_the_spa_are_not_measured(client: TestClient, live: Metrics) -> None:
    client.get("/api/stream")
    client.get("/assets/index.js")

    assert live.snapshot().stats == []


def test_a_failing_request_still_counts(client: TestClient, live: Metrics) -> None:
    assert client.get("/api/falha").status_code == 500

    assert stat(live, "GET /api/falha").calls == 1


# -- rota ---------------------------------------------------------------------


def _user(nickname: str) -> UserDTO:
    return UserDTO(id=1, nickname=nickname, client_id=uuid4())  # type: ignore[call-arg]


@pytest.fixture
def debug_client(live: Metrics, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(config.toml.debug, "enabled", True)
    monkeypatch.setattr(config.toml.host, "nickname", "host")
    app = FastAPI()
    app.include_router(debug_router)
    app.dependency_overrides[get_current_user] = lambda: _user("host")
    return TestClient(app)


def test_metrics_endpoint_describes_the_measurements(
    debug_client: TestClient, live: Metrics
) -> None:
    live.record("http", "GET /api/x", 12.0)
    live.set_engine_speed(10)

    body = debug_client.get("/api/debug/metrics").json()

    assert body["engine"] == {"speed": 10.0, "budget_ms": 100.0}
    assert body["items"] == [
        {
            "kind": "http",
            "name": "GET /api/x",
            "calls": 1,
            "total_ms": 12.0,
            "mean_ms": 12.0,
            "p95_ms": 12.0,
            "max_ms": 12.0,
        }
    ]
    assert body["pid"] > 0


def test_paused_engine_has_no_budget(debug_client: TestClient) -> None:
    assert debug_client.get("/api/debug/metrics").json()["engine"]["budget_ms"] is None


def test_reset_endpoint_clears_the_measurements(
    debug_client: TestClient, live: Metrics
) -> None:
    live.record("http", "GET /api/x", 12.0)

    assert debug_client.post("/api/debug/metrics/reset").status_code == 204
    assert debug_client.get("/api/debug/metrics").json()["items"] == []


def test_endpoint_is_gone_when_debug_is_off(
    debug_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(config.toml.debug, "enabled", False)

    assert debug_client.get("/api/debug/metrics").status_code == 404
    assert debug_client.post("/api/debug/metrics/reset").status_code == 404


def test_only_the_host_reads_the_metrics(debug_client: TestClient) -> None:
    app = debug_client.app
    assert isinstance(app, FastAPI)
    app.dependency_overrides[get_current_user] = lambda: _user("convidado")

    assert debug_client.get("/api/debug/metrics").status_code == 403
