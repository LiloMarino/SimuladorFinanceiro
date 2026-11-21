"""Os avisos por ativo da página do ativo, com o broker de verdade e uma simulação de mentira."""

from __future__ import annotations

import asyncio
from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace
from typing import Any, cast
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from socketio import AsyncServer

from backend.core.dto.candle import CandleDTO
from backend.core.dto.order_preview import OrderPreviewDTO, OrderPreviewRequest
from backend.core.dto.state_company import StateCompanyDetailDTO
from backend.core.dto.stock_price_history import StockPriceHistoryDTO
from backend.core.dto.technical_indicators import IndicatorsRequestDTO
from backend.core.enum import (
    AssetClass,
    DividendPolicy,
    OrderAction,
    StateCompanyOrigin,
    StateCompanyStatus,
)
from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.core.runtime.user_manager import UserManager
from backend.features.realtime import ws_broker
from backend.features.realtime.ws_broker import SocketBroker
from backend.features.simulation.asset_page_feed import AssetPageFeed

START = date(2023, 1, 2)
DAYS = 60
TICKER = "PETR4"
D = Decimal


class RecordingServer:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str, Any]] = []
        self.broker: SocketBroker | None = None

    async def emit(self, event: str, payload: Any, to: str) -> None:
        self.sent.append((event, to, payload))

    def of(self, event: str) -> list[tuple[str, Any]]:
        return [(sid, payload) for name, sid, payload in self.sent if name == event]


def history(days: int) -> list[StockPriceHistoryDTO]:
    rows = []
    for day in range(days):
        price = 30 + (day % 7) * 0.4 + day * 0.05
        rows.append(
            StockPriceHistoryDTO(
                price_date=START + timedelta(days=day),
                open=price,
                high=price + 0.5,
                low=price - 0.5,
                close=price + (0.2 if day % 2 else -0.2),
                volume=1000,
            )
        )
    return rows


def candle_of(row: StockPriceHistoryDTO) -> CandleDTO:
    return CandleDTO(
        id=1,
        ticker=TICKER,
        name="Petro",
        asset_class=AssetClass.STOCK,
        open=row.open,
        high=row.high,
        low=row.low,
        close=row.close,
        volume=row.volume,
        price_date=row.price_date,
        change=row.close - row.open,
        change_pct=0,
    )


def preview(cash_after: Decimal) -> OrderPreviewDTO:
    return OrderPreviewDTO(
        price=D(10),
        quantity=D(10),
        total=D(100),
        cash_before=D(1000),
        cash_after=cash_after,
        max_quantity=D(100),
        held=D(0),
        reserved=D(0),
        held_after=D(10),
        networth_share_after=D("0.1"),
        profit=None,
        tax=None,
        month_sales_after=None,
        exemption_limit=D(20000),
        tax_due_date=None,
    )


def state_detail(ticker: str) -> StateCompanyDetailDTO:
    return StateCompanyDetailDTO(
        ticker=ticker,
        origin=StateCompanyOrigin.FOUNDED,
        status=StateCompanyStatus.ACTIVE,
        founded_on=None,
        size=None,
        government_share=D("0.51"),
        shares=1000,
        price=D("12.50"),
        fair_value=None,
        dividends=D(0),
        dividend_policy=DividendPolicy.NORMAL,
        policies=[],
        beta=None,
        months=[],
        holders=None,
    )


class FakeSimulation:
    """O que o feed lê da partida: histórico, caixa, prévia e a estatal."""

    def __init__(self, rows: list[StockPriceHistoryDTO]) -> None:
        self.rows = rows
        self.settings = SimpleNamespace(show_chart_hints=True)
        self.cash = D(1000)
        self.refuse: str | None = None
        self.refuse_status = 422
        self.details_calls = 0
        self.preview_calls = 0
        self.state_calls: list[Any] = []
        self._engine = SimpleNamespace(
            broker=SimpleNamespace(get_positions=lambda _client: {}),
            get_cash=lambda _client: self.cash,
            estimated_price=lambda _ticker, _action, _limit: D(10),
        )

    def acting_client(self, requester: UUID, _account: int | None) -> UUID:
        return requester

    def preview_order(self, *_args: Any) -> OrderPreviewDTO:
        self.preview_calls += 1
        if self.refuse:
            raise HTTPException(status_code=self.refuse_status, detail=self.refuse)
        return preview(self.cash - 100)

    def get_stock_details(self, _ticker: str) -> Any:
        self.details_calls += 1
        return SimpleNamespace(history=self.rows)

    def get_state_company_detail(self, user: Any, ticker: str) -> Any:
        self.state_calls.append(user)
        return state_detail(ticker)


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
        UserManager, "get_user", lambda client_id: SimpleNamespace(client=client_id)
    )
    recording.broker = broker
    return recording


def open_tab(server: RecordingServer, sid: str, events: list[str]) -> UUID:
    assert server.broker is not None
    broker = server.broker
    client = uuid4()
    broker.register_client(client, sid)
    broker.update_subscription(sid, events)
    return client


@pytest.fixture
def sim() -> FakeSimulation:
    return FakeSimulation(history(DAYS))


@pytest.fixture
def feed(sim: FakeSimulation) -> AssetPageFeed:
    return AssetPageFeed(cast(Any, sim))


REQUEST = OrderPreviewRequest(action=OrderAction.BUY, quantity=D(10))
INDICATORS = IndicatorsRequestDTO(series=["rsi"])


def publish(feed: AssetPageFeed, sim: FakeSimulation) -> None:
    feed.publish_day([candle_of(sim.rows[-1])])


def test_the_preview_is_recalculated_on_the_daily_publish_for_its_client(
    server: RecordingServer, sim: FakeSimulation, feed: AssetPageFeed
):
    ana = open_tab(server, "ana", [f"order_preview:{TICKER}"])
    open_tab(server, "bia", [f"order_preview:{TICKER}"])
    feed.watch_preview(ana, None, TICKER, REQUEST)
    calls = sim.preview_calls

    publish(feed, sim)

    assert sim.preview_calls == calls + 1
    [(sid, payload)] = server.of(f"order_preview:{TICKER}")
    assert sid == "ana"
    assert D(payload["preview"]["cash_after"]) == D(900)
    assert payload["request"]["action"] == "buy"
    assert payload["account"] is None


def test_the_indicators_are_recalculated_on_the_daily_publish_for_its_client(
    server: RecordingServer, sim: FakeSimulation, feed: AssetPageFeed
):
    ana = open_tab(server, "ana", [f"indicators_update:{TICKER}"])
    open_tab(server, "bia", [f"indicators_update:{TICKER}"])
    first = feed.watch_indicators(ana, TICKER, INDICATORS)
    assert first is not None and first.series.rsi

    publish(feed, sim)

    [(sid, payload)] = server.of(f"indicators_update:{TICKER}")
    assert sid == "ana"
    last = sim.rows[-1].price_date.isoformat()
    assert payload["update"]["summary"]["date"] == last
    assert [p["date"] for p in payload["update"]["series"]["rsi"]] == [last]
    assert payload["previous_date"] == sim.rows[-2].price_date.isoformat()
    assert payload["request"]["series"] == ["rsi"]


def test_nothing_is_calculated_without_a_subscriber(
    server: RecordingServer, sim: FakeSimulation, feed: AssetPageFeed
):
    # O cliente pediu por HTTP, mas nenhuma aba assina os eventos
    ana = uuid4()
    assert server.broker is not None
    server.broker.register_client(ana, "ana")
    feed.watch_preview(ana, None, TICKER, REQUEST)
    feed.watch_indicators(ana, TICKER, INDICATORS)
    previews, details = sim.preview_calls, sim.details_calls

    publish(feed, sim)

    assert (sim.preview_calls, sim.details_calls) == (previews, details)
    assert server.sent == []


def test_a_client_that_stopped_subscribing_is_no_longer_served(
    server: RecordingServer, sim: FakeSimulation, feed: AssetPageFeed
):
    assert server.broker is not None
    broker = server.broker
    ana = open_tab(server, "ana", [f"indicators_update:{TICKER}"])
    feed.watch_indicators(ana, TICKER, INDICATORS)
    broker.update_subscription("ana", [])
    details = sim.details_calls

    publish(feed, sim)

    assert sim.details_calls == details
    assert server.sent == []


def test_the_patterns_go_to_every_subscriber_of_the_asset_only(
    server: RecordingServer, sim: FakeSimulation, feed: AssetPageFeed
):
    open_tab(server, "ana", [f"candle_patterns_update:{TICKER}"])
    open_tab(server, "bia", [f"candle_patterns_update:{TICKER}"])
    open_tab(server, "cris", ["candle_patterns_update:VALE3"])

    publish(feed, sim)

    received = server.of(f"candle_patterns_update:{TICKER}")
    assert sorted(sid for sid, _ in received) == ["ana", "bia"]
    assert received[0][1] == received[1][1]
    assert server.of("candle_patterns_update:VALE3") == []
    # O frame sai de uma leitura só do histórico, para os dois assinantes
    assert sim.details_calls == 1


def test_the_patterns_follow_the_chart_hints_setting(
    server: RecordingServer, sim: FakeSimulation, feed: AssetPageFeed
):
    sim.settings.show_chart_hints = False
    open_tab(server, "ana", [f"candle_patterns_update:{TICKER}"])

    publish(feed, sim)

    assert server.sent == []
    assert sim.details_calls == 0


def test_the_state_company_goes_to_each_subscriber_of_the_asset(
    server: RecordingServer, sim: FakeSimulation, feed: AssetPageFeed
):
    ana = open_tab(server, "ana", [f"state_company_update:{TICKER}"])
    open_tab(server, "bia", ["state_company_update:VALE3"])

    publish(feed, sim)

    [(sid, payload)] = server.of(f"state_company_update:{TICKER}")
    assert sid == "ana"
    assert payload["detail"]["ticker"] == TICKER
    assert [user.client for user in sim.state_calls] == [ana]


def test_a_preview_that_stopped_fitting_goes_out_with_the_reason(
    server: RecordingServer, sim: FakeSimulation, feed: AssetPageFeed
):
    ana = open_tab(server, "ana", [f"order_preview:{TICKER}"])
    feed.watch_preview(ana, None, TICKER, REQUEST)
    sim.refuse = "O valor não paga uma unidade"

    publish(feed, sim)

    [(_, payload)] = server.of(f"order_preview:{TICKER}")
    assert payload["preview"] is None
    assert payload["refused"] == "O valor não paga uma unidade"


def test_the_refusal_goes_out_once_per_reason(
    server: RecordingServer, sim: FakeSimulation, feed: AssetPageFeed
):
    ana = open_tab(server, "ana", [f"order_preview:{TICKER}"])
    feed.watch_preview(ana, None, TICKER, REQUEST)
    sim.refuse = "Motivo um"
    feed.refresh_previews()
    sim.cash = D(500)
    feed.refresh_previews()
    sim.refuse = "Motivo dois"
    sim.cash = D(400)
    feed.refresh_previews()

    reasons = [
        payload["refused"] for _, payload in server.of(f"order_preview:{TICKER}")
    ]
    assert reasons == ["Motivo um", "Motivo dois"]


def test_a_refused_request_is_registered_and_its_reason_is_not_resent_on_the_next_day(
    server: RecordingServer, sim: FakeSimulation, feed: AssetPageFeed
):
    ana = open_tab(server, "ana", [f"order_preview:{TICKER}"])
    sim.refuse = "Motivo um"
    with pytest.raises(HTTPException):
        feed.watch_preview(ana, None, TICKER, REQUEST)

    feed.refresh_previews()
    assert server.of(f"order_preview:{TICKER}") == []

    sim.refuse = None
    sim.cash = D(500)
    feed.refresh_previews()

    [(_, payload)] = server.of(f"order_preview:{TICKER}")
    assert payload["preview"] is not None
    assert payload["refused"] is None


def test_a_status_that_is_not_a_rule_refusal_is_not_registered(
    server: RecordingServer, sim: FakeSimulation, feed: AssetPageFeed
):
    ana = open_tab(server, "ana", [f"order_preview:{TICKER}"])
    sim.refuse = "Sem permissão"
    sim.refuse_status = 403
    with pytest.raises(HTTPException):
        feed.watch_preview(ana, None, TICKER, REQUEST)
    sim.refuse = None
    sim.cash = D(500)

    feed.refresh_previews()

    assert server.of(f"order_preview:{TICKER}") == []


def test_a_status_that_is_not_a_rule_refusal_does_not_go_out_as_refused(
    server: RecordingServer, sim: FakeSimulation, feed: AssetPageFeed
):
    ana = open_tab(server, "ana", [f"order_preview:{TICKER}"])
    feed.watch_preview(ana, None, TICKER, REQUEST)
    sim.refuse = "Falha do servidor"
    sim.refuse_status = 500

    feed.refresh_previews()

    assert server.of(f"order_preview:{TICKER}") == []


def test_outside_the_day_the_preview_is_sent_only_when_what_it_reads_changed(
    server: RecordingServer, sim: FakeSimulation, feed: AssetPageFeed
):
    ana = open_tab(server, "ana", [f"order_preview:{TICKER}"])
    feed.watch_preview(ana, None, TICKER, REQUEST)

    feed.refresh_previews()
    assert server.of(f"order_preview:{TICKER}") == []

    sim.cash = D(500)
    feed.refresh_previews()
    assert len(server.of(f"order_preview:{TICKER}")) == 1

    feed.refresh_previews()
    assert len(server.of(f"order_preview:{TICKER}")) == 1


def test_the_day_that_is_not_saved_yet_still_enters_the_chart(
    server: RecordingServer, sim: FakeSimulation, feed: AssetPageFeed
):
    # O banco só chega até ontem (cotas e estatais): o pregão de hoje vem da vela
    today = history(DAYS + 1)[-1]
    ana = open_tab(server, "ana", [f"indicators_update:{TICKER}"])
    feed.watch_indicators(ana, TICKER, INDICATORS)

    feed.publish_day([candle_of(today)])

    [(_, payload)] = server.of(f"indicators_update:{TICKER}")
    assert payload["update"]["summary"]["date"] == today.price_date.isoformat()
    assert payload["previous_date"] == sim.rows[-1].price_date.isoformat()
