"""Os avisos que dependem do caixa e do dia, com o broker de verdade e uma simulação de mentira."""

from __future__ import annotations

import asyncio
from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import Any, cast
from uuid import UUID, uuid4

import pytest
from socketio import AsyncServer

from backend.core.dto.fixed_income_projection import FixedIncomeQuoteDTO
from backend.core.exceptions.http_exceptions import NotFoundError
from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.core.runtime.user_manager import UserManager
from backend.features.realtime import ws_broker
from backend.features.realtime.ws_broker import SocketBroker
from backend.features.simulation import cash_feed as cash_feed_module
from backend.features.simulation.cash_feed import CashFeed


class RecordingServer:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str, Any]] = []
        self.broker: SocketBroker | None = None

    async def emit(self, event: str, payload: Any, to: str) -> None:
        self.sent.append((event, to, payload))

    def of(self, event: str) -> list[tuple[str, Any]]:
        return [(sid, payload) for name, sid, payload in self.sent if name == event]


def make_quote(amount: Decimal) -> FixedIncomeQuoteDTO:
    return FixedIncomeQuoteDTO(
        amount=amount,
        index_rate=Decimal("0.1"),
        business_days=252,
        redemption_date=date(2027, 1, 4),
        income_tax_rate=Decimal("0.15"),
        effective_annual_rate=None,
        gross_amount=None,
        gross_return=None,
        gross_return_pct=None,
        income_tax=None,
        income_tax_pct=None,
        net_amount=None,
        net_return=None,
        net_return_pct=None,
        cash_before=Decimal(1000),
        cash_after=Decimal(900),
        max_amount=Decimal(1000),
        cap_used=None,
        income_tax_brackets=[],
    )


class Payload:
    def __init__(self, data: Any) -> None:
        self.data = data

    def to_json(self) -> Any:
        return self.data


class FakeSimulation:
    """O que o feed lê da partida: o título, a cotação, a vida financeira e as pendências."""

    def __init__(self) -> None:
        self.quotes = 0
        self.life_calls: list[UUID] = []
        self.pending_calls: list[UUID] = []
        self.has_asset = True

    def get_fixed_asset(self, asset_id: str) -> Any:
        return object() if self.has_asset else None

    def acting_client(self, requester: UUID, account: int | None) -> UUID:
        return requester

    def quote_fixed_income(self, _acting: UUID, _asset: Any, amount: Decimal) -> Any:
        self.quotes += 1
        return make_quote(amount)

    def get_life_status(self, client_id: UUID) -> Payload | None:
        self.life_calls.append(client_id)
        return Payload({"status": "ok"})

    def get_pending(self, user: Any) -> list[Any]:
        self.pending_calls.append(user.client_id)
        return []


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
    # A vida financeira real tem dezenas de campos: o feed só a repassa
    monkeypatch.setattr(
        cash_feed_module,
        "LifeStatusUpdateEventDTO",
        lambda status: Payload({"status": status.data}),
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
def feed(sim: FakeSimulation) -> CashFeed:
    return CashFeed(cast(Any, sim))


def test_nothing_is_published_while_the_cash_did_not_move(
    server: RecordingServer, sim: FakeSimulation, feed: CashFeed
) -> None:
    open_tab(server, "a", ["life_status_update", "pending_update"])

    feed.flush()

    assert server.sent == []
    assert sim.life_calls == []


def test_a_cash_move_updates_the_life_and_the_pending_of_whose_cash_moved(
    server: RecordingServer, sim: FakeSimulation, feed: CashFeed
) -> None:
    first = open_tab(server, "a", ["life_status_update", "pending_update"])
    open_tab(server, "b", ["life_status_update", "pending_update"])

    feed.cash_moved((first,), None)
    feed.flush()

    assert [sid for sid, _ in server.of("life_status_update")] == ["a"]
    assert [sid for sid, _ in server.of("pending_update")] == ["a"]
    assert sim.life_calls == [first]


def test_a_fund_account_move_does_not_touch_the_personal_screens(
    server: RecordingServer, sim: FakeSimulation, feed: CashFeed
) -> None:
    client = open_tab(server, "a", ["life_status_update", "pending_update"])

    feed.cash_moved((client,), 7)
    feed.flush()

    assert server.sent == []


def test_the_close_of_the_day_updates_every_subscriber(
    server: RecordingServer, sim: FakeSimulation, feed: CashFeed
) -> None:
    open_tab(server, "a", ["life_status_update", "pending_update"])
    open_tab(server, "b", ["life_status_update"])

    feed.day_passed()
    feed.flush()

    assert sorted(sid for sid, _ in server.of("life_status_update")) == ["a", "b"]
    assert [sid for sid, _ in server.of("pending_update")] == ["a"]


def test_several_moves_before_the_flush_publish_once(
    server: RecordingServer, sim: FakeSimulation, feed: CashFeed
) -> None:
    client = open_tab(server, "a", ["life_status_update"])

    feed.cash_moved((client,), None)
    feed.cash_moved((client,), None)
    feed.cash_moved((client,), None)
    feed.flush()
    feed.flush()

    assert len(server.of("life_status_update")) == 1


def test_the_life_is_skipped_for_a_match_without_it(
    server: RecordingServer, sim: FakeSimulation, feed: CashFeed
) -> None:
    client = open_tab(server, "a", ["life_status_update"])
    sim.get_life_status = lambda _client_id: None  # type: ignore[method-assign]

    feed.cash_moved((client,), None)
    feed.flush()

    assert server.sent == []


def test_the_projection_answers_now_and_is_republished_when_the_cash_moves(
    server: RecordingServer, sim: FakeSimulation, feed: CashFeed
) -> None:
    asset = str(uuid4())
    event = f"fixed_income_projection:{asset}"
    client = open_tab(server, "a", [event])

    answer = feed.watch_projection(client, None, asset, Decimal(100))
    assert answer.amount == Decimal(100)
    assert server.sent == []

    feed.cash_moved((client,), None)
    feed.flush()

    [(sid, payload)] = server.of(event)
    assert sid == "a"
    assert payload["account"] is None
    assert Decimal(str(payload["amount"])) == Decimal(100)


def test_the_projection_follows_only_the_account_of_the_boleta(
    server: RecordingServer, sim: FakeSimulation, feed: CashFeed
) -> None:
    asset = str(uuid4())
    event = f"fixed_income_projection:{asset}"
    client = open_tab(server, "a", [event])
    feed.watch_projection(client, 7, asset, Decimal(100))
    quotes = sim.quotes

    feed.cash_moved((client,), None)
    feed.flush()
    assert server.of(event) == []
    assert sim.quotes == quotes

    feed.cash_moved((client,), 7)
    feed.flush()
    assert [payload["account"] for _, payload in server.of(event)] == [7]


def test_the_projection_is_republished_every_day(
    server: RecordingServer, sim: FakeSimulation, feed: CashFeed
) -> None:
    asset = str(uuid4())
    event = f"fixed_income_projection:{asset}"
    client = open_tab(server, "a", [event])
    feed.watch_projection(client, None, asset, Decimal(100))

    feed.day_passed()
    feed.flush()

    assert len(server.of(event)) == 1


def test_a_boleta_closed_is_no_longer_quoted(
    server: RecordingServer, sim: FakeSimulation, feed: CashFeed
) -> None:
    asset = str(uuid4())
    event = f"fixed_income_projection:{asset}"
    client = open_tab(server, "a", [event])
    feed.watch_projection(client, None, asset, Decimal(100))
    assert server.broker is not None
    server.broker.update_subscription("a", [])
    quotes = sim.quotes

    feed.day_passed()
    feed.flush()

    assert server.of(event) == []
    assert sim.quotes == quotes


def test_the_projection_of_an_unknown_title_is_not_found(
    server: RecordingServer, sim: FakeSimulation, feed: CashFeed
) -> None:
    sim.has_asset = False

    with pytest.raises(NotFoundError):
        feed.watch_projection(uuid4(), None, str(uuid4()), Decimal(100))
