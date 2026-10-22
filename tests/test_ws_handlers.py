"""Conexão, desconexão e inscrição do Socket.IO, com o servidor substituído."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import Any, cast
from uuid import UUID

import pytest
from socketio import AsyncServer

from backend.core.enum import PlayerActivity
from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.core.runtime.user_manager import UserManager
from backend.features.realtime.ws_broker import SocketBroker
from backend.features.realtime.ws_handlers import register_ws_handlers
from tests.fakes import client

ANA = client("Ana")


class _FakeServer:
    """Guarda os handlers pelo nome, como o `@sio.event`, e grava o que emite."""

    def __init__(self) -> None:
        self.handlers: dict[str, Callable[..., Any]] = {}
        self.sent: list[tuple[str, object, str]] = []

    def event(self, handler: Callable[..., Any]) -> Callable[..., Any]:
        self.handlers[handler.__name__] = handler
        return handler

    async def emit(self, event: str, data: object, to: str) -> None:
        self.sent.append((event, data, to))


class _Socket:
    def __init__(self, server: _FakeServer, broker: SocketBroker) -> None:
        self.server = server
        self.broker = broker
        self.unregistered: list[UUID] = []

    def connect(self, sid: str, cookie: str | None) -> bool:
        environ = {} if cookie is None else {"HTTP_COOKIE": cookie}
        return asyncio.run(self.server.handlers["connect"](sid, environ))

    def disconnect(self, sid: str) -> None:
        asyncio.run(self.server.handlers["disconnect"](sid))

    def subscribe(self, sid: str, events: list[str]) -> None:
        asyncio.run(self.server.handlers["subscribe"](sid, {"events": events}))

    def presence(self, sid: str, data: object) -> None:
        asyncio.run(self.server.handlers["presence"](sid, data))


@pytest.fixture
def activities(monkeypatch: pytest.MonkeyPatch) -> list[tuple[UUID, str, object]]:
    """O que o handler `presence` entrega ao UserManager: (client_id, sid, atividade)."""
    received: list[tuple[UUID, str, object]] = []
    monkeypatch.setattr(
        UserManager,
        "set_activity",
        lambda client_id, sid, activity: received.append((client_id, sid, activity)),
    )
    return received


@pytest.fixture
def dropped(monkeypatch: pytest.MonkeyPatch) -> list[tuple[UUID, str]]:
    received: list[tuple[UUID, str]] = []
    monkeypatch.setattr(
        UserManager,
        "drop_activity",
        lambda client_id, sid: received.append((client_id, sid)),
    )
    return received


@pytest.fixture
def socket(monkeypatch: pytest.MonkeyPatch) -> _Socket:
    server = _FakeServer()
    broker = SocketBroker(cast(AsyncServer, server))
    register_ws_handlers(cast(AsyncServer, server))
    monkeypatch.setattr(RealtimeBrokerManager, "get_broker", lambda: broker)

    fake = _Socket(server, broker)
    monkeypatch.setattr(UserManager, "unregister", fake.unregistered.append)
    return fake


def test_connection_without_cookie_is_refused(socket, caplog):
    with caplog.at_level(logging.WARNING):
        assert socket.connect("tab-1", None) is False

    assert "sem client_id" in caplog.text
    assert socket.broker.get_client_id_by_sid("tab-1") is None


@pytest.mark.parametrize("cookie", ["client_id=abc", "client_id="])
def test_client_id_that_is_not_a_uuid_is_refused(socket, caplog, cookie):
    with caplog.at_level(logging.WARNING):
        assert socket.connect("tab-1", cookie) is False

    assert "client_id inválido" in caplog.text
    assert socket.broker.get_client_id_by_sid("tab-1") is None


def test_valid_cookie_connects_the_tab_to_the_client(socket):
    assert socket.connect("tab-1", f"tema=escuro; client_id={ANA}") is True

    assert socket.broker.get_client_id_by_sid("tab-1") == ANA


def test_closing_one_of_two_tabs_keeps_the_player(socket):
    socket.connect("tab-1", f"client_id={ANA}")
    socket.connect("tab-2", f"client_id={ANA}")

    socket.disconnect("tab-2")

    assert socket.unregistered == []
    assert socket.broker.get_client_id_by_sid("tab-1") == ANA


def test_closing_the_last_tab_takes_the_player_out(socket):
    socket.connect("tab-1", f"client_id={ANA}")
    socket.connect("tab-2", f"client_id={ANA}")

    socket.disconnect("tab-2")
    socket.disconnect("tab-1")

    assert socket.unregistered == [ANA]


def test_disconnect_of_an_unknown_tab_leaves_everyone(socket):
    socket.disconnect("tab-1")

    assert socket.unregistered == []


def test_subscription_of_an_unknown_tab_is_ignored(socket):
    socket.subscribe("tab-1", ["simulation_update"])

    assert socket.server.sent == []


def test_subscription_routes_events_to_the_tab(socket, monkeypatch):
    socket.connect("tab-1", f"client_id={ANA}")

    socket.subscribe("tab-1", ["simulation_update"])

    assert socket.server.sent == [
        ("subscribed", {"events": ["simulation_update"]}, "tab-1")
    ]
    # O broker passa a mandar o evento assinado para a aba
    socket.broker.bind_event_loop(cast(asyncio.AbstractEventLoop, object()))
    monkeypatch.setattr(
        "backend.features.realtime.ws_broker.asyncio.run_coroutine_threadsafe",
        lambda coro, _loop: asyncio.run(coro),
    )
    socket.broker.notify("simulation_update", {})
    assert socket.server.sent[-1] == ("simulation_update", {}, "tab-1")


def test_presence_hands_the_activity_of_the_tab_to_the_room(socket, activities):
    socket.connect("tab-1", f"client_id={ANA}")

    socket.presence("tab-1", {"activity": "settings"})

    assert activities == [(ANA, "tab-1", PlayerActivity.SETTINGS)]


def test_presence_with_null_activity_means_online(socket, activities):
    socket.connect("tab-1", f"client_id={ANA}")

    socket.presence("tab-1", {"activity": None})

    assert activities == [(ANA, "tab-1", None)]


@pytest.mark.parametrize(
    "data",
    [{"activity": "dancing"}, {"activity": 3}, {"activity": ["lobby"]}, "lobby", None],
)
def test_presence_outside_the_catalog_is_ignored(socket, activities, data):
    socket.connect("tab-1", f"client_id={ANA}")

    socket.presence("tab-1", data)

    assert activities == []


def test_presence_of_an_unknown_tab_is_ignored(socket, activities):
    socket.presence("tab-1", {"activity": "lobby"})

    assert activities == []


def test_closing_one_of_two_tabs_drops_only_its_activity(socket, dropped):
    socket.connect("tab-1", f"client_id={ANA}")
    socket.connect("tab-2", f"client_id={ANA}")

    socket.disconnect("tab-2")

    assert dropped == [(ANA, "tab-2")]


def test_closing_the_last_tab_leaves_the_activity_to_the_unregister(socket, dropped):
    socket.connect("tab-1", f"client_id={ANA}")

    socket.disconnect("tab-1")

    assert dropped == []
