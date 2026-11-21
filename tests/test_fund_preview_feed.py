"""As prévias da gestora entregues pelo tempo real, com o broker de verdade e uma simulação de mentira."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any, cast
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from socketio import AsyncServer

from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.core.runtime.user_manager import UserManager
from backend.features.realtime import ws_broker
from backend.features.realtime.ws_broker import SocketBroker
from backend.features.simulation import fund_preview_feed as feed_module
from backend.features.simulation.fund_preview_feed import (
    BUYBACK,
    DIRECTED,
    ISSUANCE,
    MERGE,
    SUBSCRIPTION,
    FundPreviewFeed,
)

FUND = 7

EVENT_DTOS = (
    "FundIssuancePreviewEventDTO",
    "FundSubscriptionPreviewEventDTO",
    "FundDirectedPreviewEventDTO",
    "FundMergePreviewEventDTO",
    "FundBuybackPreviewEventDTO",
)


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
    """O que o feed lê da partida: cada prévia devolve o que estiver programado, ou recusa."""

    def __init__(self) -> None:
        self.result: Any = "a"
        self.refusal: str | None = None
        self.calls: list[tuple[UUID, tuple]] = []

    def _ensure_funds(self) -> None:
        """A partida tem a expansão ligada."""

    def _answer(self, user: Any, *params: Any) -> Any:
        self.calls.append((user.client_id, params))
        if self.refusal is not None:
            raise HTTPException(409, self.refusal)
        return self.result

    def preview_fund_issuance(self, user: Any, _fund: int, quotas: Any) -> Any:
        return self._answer(user, quotas)

    def preview_fund_subscription(self, user: Any, _fund: int, quotas: Any) -> Any:
        return self._answer(user, quotas)

    def preview_fund_directed(self, user: Any, _fund: int, quotas: Any) -> Any:
        return self._answer(user, quotas)

    def preview_fund_merge(self, user: Any, _fund: int, daughter: Any) -> Any:
        return self._answer(user, daughter)

    def preview_fund_buyback(
        self, user: Any, _fund: int, quantity: Any, price: Any
    ) -> Any:
        return self._answer(user, quantity, price)


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
    # Os eventos reais têm a prévia inteira: o feed só repassa o que recebeu
    for name in EVENT_DTOS:
        monkeypatch.setattr(
            feed_module,
            name,
            lambda preview, refused, **params: Payload(
                {
                    "params": tuple(params.values()),
                    "preview": preview,
                    "refused": refused,
                }
            ),
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
def feed(sim: FakeSimulation) -> FundPreviewFeed:
    return FundPreviewFeed(cast(Any, sim))


def user_of(client: UUID) -> Any:
    return SimpleNamespace(client_id=client, id=1)


PARAMS = {
    ISSUANCE: (10,),
    SUBSCRIPTION: (10,),
    DIRECTED: (10,),
    MERGE: (3,),
    BUYBACK: (5, 12),
}


def event_of(kind: Any) -> str:
    return f"{kind.prefix}:{FUND}"


def test_the_request_answers_now_and_nothing_goes_out_until_something_changes(
    server: RecordingServer, sim: FakeSimulation, feed: FundPreviewFeed
) -> None:
    client = open_tab(server, "a", [event_of(ISSUANCE)])

    assert feed.watch(ISSUANCE, user_of(client), FUND, (10,)) == "a"
    feed.flush()

    assert server.sent == []


@pytest.mark.parametrize("kind", list(PARAMS))
def test_each_preview_is_recalculated_with_the_request_params_for_who_subscribes(
    kind: Any, server: RecordingServer, sim: FakeSimulation, feed: FundPreviewFeed
) -> None:
    mine = open_tab(server, "a", [event_of(kind)])
    open_tab(server, "b", [event_of(kind)])
    feed.watch(kind, user_of(mine), FUND, PARAMS[kind])
    sim.result = "b"

    feed.funds_changed()
    feed.flush()

    [(sid, payload)] = server.of(event_of(kind))
    assert sid == "a"
    assert payload == {"params": PARAMS[kind], "preview": "b", "refused": None}


def test_a_preview_equal_to_the_last_one_is_not_sent_again(
    server: RecordingServer, sim: FakeSimulation, feed: FundPreviewFeed
) -> None:
    client = open_tab(server, "a", [event_of(ISSUANCE)])
    feed.watch(ISSUANCE, user_of(client), FUND, (10,))

    feed.funds_changed()
    feed.flush()

    assert server.of(event_of(ISSUANCE)) == []


def test_a_refused_request_sends_the_reason_once(
    server: RecordingServer, sim: FakeSimulation, feed: FundPreviewFeed
) -> None:
    client = open_tab(server, "a", [event_of(SUBSCRIPTION)])
    feed.watch(SUBSCRIPTION, user_of(client), FUND, (10,))
    sim.refusal = "Oferta encerrada"

    feed.funds_changed()
    feed.flush()
    feed.funds_changed()
    feed.flush()

    [(_, payload)] = server.of(event_of(SUBSCRIPTION))
    assert payload == {
        "params": (10,),
        "preview": None,
        "refused": "Oferta encerrada",
    }


def test_a_request_refused_at_first_is_kept_and_the_preview_comes_when_it_fits(
    server: RecordingServer, sim: FakeSimulation, feed: FundPreviewFeed
) -> None:
    client = open_tab(server, "a", [event_of(DIRECTED)])
    sim.refusal = "Caixa insuficiente"
    with pytest.raises(HTTPException):
        feed.watch(DIRECTED, user_of(client), FUND, (10,))
    sim.refusal = None

    feed.funds_changed()
    feed.flush()

    [(_, payload)] = server.of(event_of(DIRECTED))
    assert payload["preview"] == "a"


def test_a_request_without_permission_is_not_registered(
    server: RecordingServer, sim: FakeSimulation, feed: FundPreviewFeed
) -> None:
    client = open_tab(server, "a", [event_of(DIRECTED)])
    sim.refusal = "Só quem gere a gestora consulta"

    def forbid(*_: Any) -> Any:
        raise HTTPException(403, "Só quem gere a gestora consulta")

    sim.preview_fund_directed = forbid  # type: ignore[method-assign]
    with pytest.raises(HTTPException):
        feed.watch(DIRECTED, user_of(client), FUND, (10,))

    feed.funds_changed()
    feed.flush()

    assert server.of(event_of(DIRECTED)) == []


def test_a_status_that_is_not_a_rule_refusal_does_not_go_out_as_refused(
    server: RecordingServer, sim: FakeSimulation, feed: FundPreviewFeed
) -> None:
    client = open_tab(server, "a", [event_of(DIRECTED)])
    feed.watch(DIRECTED, user_of(client), FUND, (10,))

    def fail(*_: Any) -> Any:
        raise HTTPException(500, "Falha do servidor")

    sim.preview_fund_directed = fail  # type: ignore[method-assign]
    feed.funds_changed()
    feed.flush()

    assert server.of(event_of(DIRECTED)) == []


def test_the_personal_cash_of_who_asked_recalculates_only_the_previews_that_read_it(
    server: RecordingServer, sim: FakeSimulation, feed: FundPreviewFeed
) -> None:
    client = open_tab(
        server,
        "a",
        [event_of(SUBSCRIPTION), event_of(ISSUANCE), event_of(DIRECTED)],
    )
    for kind in cast("tuple[Any, ...]", (SUBSCRIPTION, ISSUANCE, DIRECTED)):
        feed.watch(kind, user_of(client), FUND, (10,))
    sim.result = "b"

    feed.cash_moved((client,), None)
    feed.flush()

    assert [sid for sid, _ in server.of(event_of(SUBSCRIPTION))] == ["a"]
    assert [sid for sid, _ in server.of(event_of(DIRECTED))] == ["a"]
    assert server.of(event_of(ISSUANCE)) == []


def test_the_cash_of_another_player_does_not_recalculate_the_personal_previews(
    server: RecordingServer, sim: FakeSimulation, feed: FundPreviewFeed
) -> None:
    client = open_tab(server, "a", [event_of(SUBSCRIPTION)])
    feed.watch(SUBSCRIPTION, user_of(client), FUND, (10,))
    sim.result = "b"

    feed.cash_moved((uuid4(),), None)
    feed.flush()

    assert server.sent == []


def test_the_fund_cash_recalculates_the_previews_that_read_it_for_every_subscriber(
    server: RecordingServer, sim: FakeSimulation, feed: FundPreviewFeed
) -> None:
    client = open_tab(
        server, "a", [event_of(BUYBACK), event_of(DIRECTED), event_of(MERGE)]
    )
    for kind in cast("tuple[Any, ...]", (BUYBACK, DIRECTED, MERGE)):
        feed.watch(kind, user_of(client), FUND, PARAMS[kind])
    sim.result = "b"

    feed.cash_moved((uuid4(),), FUND)
    feed.flush()

    assert [sid for sid, _ in server.of(event_of(BUYBACK))] == ["a"]
    assert [sid for sid, _ in server.of(event_of(DIRECTED))] == ["a"]
    assert server.of(event_of(MERGE)) == []


def test_the_close_of_the_day_recalculates_every_preview(
    server: RecordingServer, sim: FakeSimulation, feed: FundPreviewFeed
) -> None:
    client = open_tab(server, "a", [event_of(kind) for kind in PARAMS])
    for kind, params in PARAMS.items():
        feed.watch(kind, user_of(client), FUND, params)
    sim.result = "b"

    feed.day_passed()
    feed.flush()

    assert len(server.sent) == len(PARAMS)


def test_a_closed_dialog_is_no_longer_recalculated(
    server: RecordingServer, sim: FakeSimulation, feed: FundPreviewFeed
) -> None:
    client = open_tab(server, "a", [event_of(ISSUANCE)])
    feed.watch(ISSUANCE, user_of(client), FUND, (10,))
    assert server.broker is not None
    server.broker.update_subscription("a", [])
    calls = len(sim.calls)

    feed.day_passed()
    feed.flush()

    assert server.sent == []
    assert len(sim.calls) == calls


def test_a_failure_in_one_preview_does_not_stop_the_others(
    server: RecordingServer,
    sim: FakeSimulation,
    feed: FundPreviewFeed,
) -> None:
    first = open_tab(server, "a", [event_of(ISSUANCE)])
    second = open_tab(server, "b", [event_of(MERGE)])
    feed.watch(ISSUANCE, user_of(first), FUND, (10,))
    feed.watch(MERGE, user_of(second), FUND, (3,))
    sim.result = "b"

    def broken(*_args: Any) -> Any:
        raise RuntimeError("falhou")

    sim.preview_fund_issuance = broken  # type: ignore[method-assign]
    feed.day_passed()
    feed.flush()

    assert [sid for sid, _ in server.of(event_of(MERGE))] == ["b"]
