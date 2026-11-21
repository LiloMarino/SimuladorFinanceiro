"""Os avisos do pregão das telas de renda fixa, Tesouro e governo, com o broker de verdade e uma simulação de mentira."""

from __future__ import annotations

import asyncio
from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import Any, cast
from uuid import UUID, uuid4

import pytest
from socketio import AsyncServer

from backend.core.dto.treasury import TreasuryHistoryPointDTO
from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.core.runtime.user_manager import UserManager
from backend.features.realtime import ws_broker
from backend.features.realtime.ws_broker import SocketBroker
from backend.features.simulation.day_feed import DayFeed


class RecordingServer:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str, Any]] = []
        self.broker: SocketBroker | None = None

    async def emit(self, event: str, payload: Any, to: str) -> None:
        self.sent.append((event, to, payload))

    def of(self, event: str) -> list[tuple[str, Any]]:
        return [(sid, payload) for name, sid, payload in self.sent if name == event]


class Payload:
    """Um DTO de mentira: o feed só pede o JSON dele."""

    def __init__(self, data: Any) -> None:
        self.data = data

    def to_json(self) -> Any:
        return self.data


class FakeSimulation:
    """O que o feed lê da partida: os títulos, os painéis do governo e do Tesouro."""

    def __init__(self) -> None:
        self._government = object()
        self._funds = None
        self.asset_id = uuid4()
        self.offer_calls = 0
        self.sovereign_calls: list[Any] = []
        self.catalog: dict[str, Any] = {"next_review": "2026-04-01"}
        self.catalog_calls = 0
        self.history_calls = 0
        self.history: list[Any] = [point(date(2026, 3, 1))]
        self.positions_calls: list[UUID] = []
        self.corporate_calls: list[tuple[UUID, str]] = []

    def get_fixed_assets(self) -> list[Any]:
        return [SimpleNamespace(asset_uuid=self.asset_id)]

    def get_fixed_offer(self, _asset_id: str) -> Payload:
        self.offer_calls += 1
        return Payload({"rate": "0.1"})

    def get_sovereign_fund(self, user: Any) -> Payload:
        self.sovereign_calls.append(user.client_id)
        return Payload({"cash": "10"})

    def get_state_companies(self, _user: Any) -> Payload:
        return Payload({"companies": []})

    def get_treasury(self) -> Payload:
        self.catalog_calls += 1
        return Payload(self.catalog)

    def get_treasury_history(self) -> list[Any]:
        self.history_calls += 1
        return self.history

    def get_treasury_positions(self, client_id: UUID) -> list[Any]:
        self.positions_calls.append(client_id)
        return []

    def get_asset_corporate_events(self, client_id: UUID, ticker: str) -> Payload:
        self.corporate_calls.append((client_id, ticker))
        return Payload({"ticker": ticker})


def point(month: date) -> TreasuryHistoryPointDTO:
    return TreasuryHistoryPointDTO(
        month=month,
        selic=Decimal("0.10"),
        ipca=Decimal("0.04"),
        premium=Decimal(0),
        debt=None,
        band_index=None,
        quotes=[],
    )


@pytest.fixture
def server(monkeypatch: pytest.MonkeyPatch) -> RecordingServer:
    recording = RecordingServer()
    broker = SocketBroker(cast(AsyncServer, recording))
    broker.bind_event_loop(cast(asyncio.AbstractEventLoop, object()))
    monkeypatch.setattr(
        ws_broker.asyncio,
        "run_coroutine_threadsafe",
        lambda coro, _loop: asyncio.run(coro),
    )
    monkeypatch.setattr(RealtimeBrokerManager, "get_broker", lambda: broker)
    monkeypatch.setattr(
        UserManager,
        "get_user",
        lambda client_id: SimpleNamespace(client_id=client_id, id=1),
    )
    recording.broker = broker
    return recording


def open_tab(server: RecordingServer, sid: str, events: list[str]) -> UUID:
    assert server.broker is not None
    client = uuid4()
    server.broker.register_client(client, sid)
    server.broker.update_subscription(sid, events)
    return client


@pytest.fixture
def sim() -> FakeSimulation:
    return FakeSimulation()


@pytest.fixture
def feed(sim: FakeSimulation) -> DayFeed:
    return DayFeed(cast(Any, sim))


def test_nothing_is_built_or_sent_without_subscribers(
    server: RecordingServer, sim: FakeSimulation, feed: DayFeed
) -> None:
    feed.publish(month_changed=True)

    assert server.sent == []
    assert sim.offer_calls == 0
    assert sim.catalog_calls == 0
    assert sim.history_calls == 0
    assert sim.positions_calls == []
    assert sim.sovereign_calls == []


def test_the_fixed_income_offer_reaches_whoever_has_the_title_open(
    server: RecordingServer, sim: FakeSimulation, feed: DayFeed
) -> None:
    open_tab(server, "a", [f"fixed_income_offer_update:{sim.asset_id}"])
    open_tab(server, "b", ["fixed_income_offer_update:outro"])

    feed.publish(month_changed=False)

    assert [
        sid for sid, _ in server.of(f"fixed_income_offer_update:{sim.asset_id}")
    ] == ["a"]
    assert sim.offer_calls == 1


def test_the_sovereign_fund_goes_to_each_subscriber_alone(
    server: RecordingServer, sim: FakeSimulation, feed: DayFeed
) -> None:
    first = open_tab(server, "a", ["sovereign_fund_update"])
    second = open_tab(server, "b", ["sovereign_fund_update"])
    open_tab(server, "c", ["state_companies_update"])

    feed.publish(month_changed=False)

    assert sorted(sid for sid, _ in server.of("sovereign_fund_update")) == ["a", "b"]
    assert sorted(sim.sovereign_calls) == sorted([first, second])
    assert [sid for sid, _ in server.of("state_companies_update")] == ["c"]


def test_the_government_screens_wait_for_the_government_expansion(
    server: RecordingServer, sim: FakeSimulation, feed: DayFeed
) -> None:
    sim._government = None
    open_tab(server, "a", ["sovereign_fund_update", "state_companies_update"])

    feed.publish(month_changed=False)

    assert server.sent == []


def test_the_treasury_catalog_goes_out_only_when_it_changed(
    server: RecordingServer, sim: FakeSimulation, feed: DayFeed
) -> None:
    open_tab(server, "a", ["treasury_catalog_update"])

    feed.publish(month_changed=False)
    feed.publish(month_changed=False)
    assert len(server.of("treasury_catalog_update")) == 1

    sim.catalog = {"next_review": "2026-05-01"}
    feed.publish(month_changed=False)
    assert len(server.of("treasury_catalog_update")) == 2


def test_the_treasury_series_receives_the_new_point_only_when_the_month_closes(
    server: RecordingServer, sim: FakeSimulation, feed: DayFeed
) -> None:
    open_tab(server, "a", ["treasury_history_update"])

    feed.publish(month_changed=False)
    assert server.of("treasury_history_update") == []

    feed.publish(month_changed=True)
    [(sid, payload)] = server.of("treasury_history_update")
    assert sid == "a"
    assert payload["point"]["month"] == "2026-03-01"


def test_the_treasury_positions_carry_the_personal_account(
    server: RecordingServer, sim: FakeSimulation, feed: DayFeed
) -> None:
    client = open_tab(server, "a", ["treasury_positions_update"])

    feed.publish(month_changed=False)

    [(sid, payload)] = server.of("treasury_positions_update")
    assert sid == "a"
    assert payload == {"positions": [], "account": None}
    assert sim.positions_calls == [client]


def test_a_new_dividend_updates_the_history_of_the_asset_for_who_holds_it(
    server: RecordingServer, sim: FakeSimulation, feed: DayFeed
) -> None:
    holder = open_tab(server, "a", ["corporate_events_update:PETR4"])
    open_tab(server, "b", ["corporate_events_update:PETR4"])

    feed.publish_corporate_events(holder, ["PETR4", "PETR4", "VALE3"])

    assert [sid for sid, _ in server.of("corporate_events_update:PETR4")] == ["a"]
    assert sim.corporate_calls == [(holder, "PETR4")]


def test_a_failure_in_one_screen_does_not_stop_the_others(
    server: RecordingServer, sim: FakeSimulation, feed: DayFeed
) -> None:
    def broken(_user: Any) -> Payload:
        raise RuntimeError("falhou")

    sim.get_sovereign_fund = broken  # type: ignore[method-assign]
    open_tab(server, "a", ["sovereign_fund_update", "state_companies_update"])

    feed.publish(month_changed=False)

    assert [sid for sid, _ in server.of("state_companies_update")] == ["a"]
