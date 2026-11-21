from __future__ import annotations

import asyncio
from typing import Any, cast
from uuid import uuid4

import pytest
from socketio import AsyncServer

from backend.core.metrics import Metrics
from backend.features.realtime import ws_broker
from backend.features.realtime.ws_broker import SocketBroker


class _RecordingServer:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    async def emit(self, event: str, _payload: object, to: str) -> None:
        self.sent.append((event, to))


@pytest.fixture
def broker(monkeypatch: pytest.MonkeyPatch) -> tuple[SocketBroker, _RecordingServer]:
    """Broker com as emissões executadas na hora, sem event loop rodando."""
    server = _RecordingServer()
    socket_broker = SocketBroker(cast(AsyncServer, server))
    socket_broker.bind_event_loop(cast(asyncio.AbstractEventLoop, object()))

    def run_now(coro: Any, _loop: object) -> None:
        asyncio.run(coro)

    monkeypatch.setattr(ws_broker.asyncio, "run_coroutine_threadsafe", run_now)
    return socket_broker, server


def test_closing_one_tab_keeps_the_player_while_another_is_open(broker):
    socket_broker, _ = broker
    client = uuid4()
    socket_broker.register_client(client, "tab-1")
    socket_broker.register_client(client, "tab-2")

    assert socket_broker.remove_client(client, "tab-2") is False
    assert socket_broker.remove_client(client, "tab-1") is True


def test_each_tab_receives_the_events_it_subscribed(broker):
    socket_broker, server = broker
    client = uuid4()
    socket_broker.register_client(client, "carteira")
    socket_broker.register_client(client, "meta")
    socket_broker.update_subscription(
        "carteira", ["portfolio_update", "simulation_ended"]
    )
    socket_broker.update_subscription(
        "meta", ["goal_progress_update", "simulation_ended"]
    )

    socket_broker.notify("portfolio_update", {}, to=client)
    socket_broker.notify("simulation_ended", {})

    assert sorted(server.sent) == [
        ("portfolio_update", "carteira"),
        ("simulation_ended", "carteira"),
        ("simulation_ended", "meta"),
    ]


def test_a_closed_tab_stops_receiving_events(broker):
    socket_broker, server = broker
    client = uuid4()
    socket_broker.register_client(client, "tab-1")
    socket_broker.register_client(client, "tab-2")
    socket_broker.update_subscription("tab-1", ["simulation_ended"])
    socket_broker.update_subscription("tab-2", ["simulation_ended"])

    socket_broker.remove_client(client, "tab-2")
    socket_broker.notify("simulation_ended", {})

    assert server.sent == [("simulation_ended", "tab-1")]


def test_targeted_event_skips_other_players(broker):
    socket_broker, server = broker
    lilo, bia = uuid4(), uuid4()
    socket_broker.register_client(lilo, "lilo")
    socket_broker.register_client(bia, "bia")
    socket_broker.update_subscription("lilo", ["portfolio_update"])
    socket_broker.update_subscription("bia", ["portfolio_update"])

    socket_broker.notify("portfolio_update", {}, to=bia)

    assert server.sent == [("portfolio_update", "bia")]


def test_subscribed_clients_are_only_those_with_a_tab_listening(broker):
    socket_broker, _ = broker
    lilo, bia = uuid4(), uuid4()
    socket_broker.register_client(lilo, "lilo")
    socket_broker.register_client(bia, "bia")
    socket_broker.update_subscription("lilo", ["budget_update"])
    socket_broker.update_subscription("bia", ["portfolio_update"])

    assert socket_broker.subscribed_clients("budget_update") == {lilo}
    assert socket_broker.subscribed_clients("economy_update") == set()

    socket_broker.remove_client(lilo, "lilo")

    assert socket_broker.subscribed_clients("budget_update") == set()


@pytest.fixture
def collector(monkeypatch: pytest.MonkeyPatch) -> Metrics:
    collector = Metrics()
    collector.enabled = True
    monkeypatch.setattr(ws_broker, "metrics", collector)
    return collector


def test_debug_records_each_send_and_its_queue_lag(broker, collector: Metrics):
    socket_broker, server = broker
    lilo, bia = uuid4(), uuid4()
    socket_broker.register_client(lilo, "lilo")
    socket_broker.register_client(bia, "bia")
    socket_broker.update_subscription("lilo", ["stocks_update"])
    socket_broker.update_subscription("bia", ["stocks_update"])

    socket_broker.notify("stocks_update", {"stocks": []})

    (traffic,) = collector.snapshot().traffic
    assert len(server.sent) == 2
    assert (traffic.sends, traffic.unheard) == (1, 0)
    assert traffic.total_bytes == 2 * len('{"stocks": []}')
    assert traffic.queue_p95_ms is not None


def test_debug_counts_a_send_nobody_subscribed(broker, collector: Metrics):
    socket_broker, server = broker

    socket_broker.notify("news_published", {"title": "x"})

    (traffic,) = collector.snapshot().traffic
    assert server.sent == []
    assert (traffic.sends, traffic.unheard, traffic.total_bytes) == (1, 1, 0)


def test_the_request_lives_while_the_client_subscribes_the_event(broker):
    socket_broker, _ = broker
    client = uuid4()
    socket_broker.register_client(client, "tab")
    socket_broker.update_subscription("tab", ["indicators_update:PETR4"])

    socket_broker.remember_request("indicators_update:PETR4", client, "pedido")

    assert socket_broker.requests("indicators_update:PETR4") == {client: "pedido"}


def test_the_request_drops_when_the_client_stops_subscribing(broker):
    socket_broker, _ = broker
    client = uuid4()
    socket_broker.register_client(client, "tab")
    socket_broker.update_subscription("tab", ["indicators_update:PETR4"])
    socket_broker.remember_request("indicators_update:PETR4", client, "pedido")

    socket_broker.update_subscription("tab", ["indicators_update:VALE3"])

    assert socket_broker.requests("indicators_update:PETR4") == {}
    # Assinar o ativo de novo não traz o pedido de volta: ele precisa ser refeito por HTTP
    socket_broker.update_subscription("tab", ["indicators_update:PETR4"])
    assert socket_broker.requests("indicators_update:PETR4") == {}


def test_the_request_drops_when_the_last_connection_closes(broker):
    socket_broker, _ = broker
    client = uuid4()
    socket_broker.register_client(client, "tab-1")
    socket_broker.register_client(client, "tab-2")
    socket_broker.update_subscription("tab-1", ["order_preview:PETR4"])
    socket_broker.update_subscription("tab-2", ["order_preview:PETR4"])
    socket_broker.remember_request("order_preview:PETR4", client, "pedido")

    socket_broker.remove_client(client, "tab-1")
    assert socket_broker.requests("order_preview:PETR4") == {client: "pedido"}

    socket_broker.remove_client(client, "tab-2")
    assert socket_broker.requests("order_preview:PETR4") == {}


def test_a_request_that_arrives_before_the_subscription_waits_for_it(broker):
    socket_broker, _ = broker
    client = uuid4()
    socket_broker.register_client(client, "tab")

    socket_broker.remember_request("order_preview:PETR4", client, "pedido")
    # Uma troca de assinatura que ainda não inclui o evento não derruba o pedido
    socket_broker.update_subscription("tab", ["portfolio_update"])
    socket_broker.update_subscription(
        "tab", ["order_preview:PETR4", "portfolio_update"]
    )

    assert socket_broker.requests("order_preview:PETR4") == {client: "pedido"}

    socket_broker.update_subscription("tab", ["portfolio_update"])
    assert socket_broker.requests("order_preview:PETR4") == {}


def test_only_the_requests_of_subscribed_clients_are_listed(broker):
    socket_broker, _ = broker
    ana, bia = uuid4(), uuid4()
    socket_broker.register_client(ana, "ana")
    socket_broker.register_client(bia, "bia")
    socket_broker.update_subscription("ana", ["order_preview:PETR4"])
    socket_broker.update_subscription("bia", ["order_preview:PETR4"])
    socket_broker.remember_request("order_preview:PETR4", ana, "da ana")
    socket_broker.remember_request("order_preview:PETR4", bia, "da bia")

    socket_broker.update_subscription("bia", [])

    assert socket_broker.requests("order_preview:PETR4") == {ana: "da ana"}


def test_the_notice_of_a_request_reaches_only_its_client(broker):
    socket_broker, server = broker
    ana, bia = uuid4(), uuid4()
    socket_broker.register_client(ana, "ana")
    socket_broker.register_client(bia, "bia")
    socket_broker.update_subscription("ana", ["order_preview:PETR4"])
    socket_broker.update_subscription("bia", ["order_preview:PETR4"])

    socket_broker.notify("order_preview:PETR4", {}, to=bia)

    assert server.sent == [("order_preview:PETR4", "bia")]
