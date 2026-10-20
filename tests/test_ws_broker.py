from __future__ import annotations

import asyncio
from typing import Any, cast
from uuid import uuid4

import pytest
from socketio import AsyncServer

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
