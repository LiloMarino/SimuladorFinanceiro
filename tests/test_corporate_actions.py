"""Desdobramentos, bonificações e dividendos aplicados à posição de cada jogador."""

from __future__ import annotations

import threading
from datetime import date
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.corporate_event import CorporateEventDTO
from backend.core.dto.events.base_event import BaseEventDTO
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.enum import AssetClass, CorporateEventKind, EquityEventType
from backend.core.runtime.user_manager import UserManager
from backend.features.variable_income.broker import Broker, load_positions
from backend.features.variable_income.entities.position import Position
from tests.fakes import FakeSimulationEngine, client

HOLDER = client("holder")
OTHER = client("other")
EX_DATE = date(2020, 1, 6)
CLOSE = Decimal("20")


def _event(kind: CorporateEventKind, value: float, day: date = EX_DATE):
    return CorporateEventDTO(stock_id=1, ex_date=day, kind=kind, value=value)


def _split(ratio: float) -> CorporateEventDTO:
    return _event(CorporateEventKind.SPLIT, ratio)


def _dividend(per_share: float) -> CorporateEventDTO:
    return _event(CorporateEventKind.DIVIDEND, per_share)


def _setup(size: int | str, price: str = "10") -> tuple[Broker, FakeSimulationEngine]:
    engine = FakeSimulationEngine()
    broker = Broker(engine, threading.RLock())
    position = Position("ABCD")
    position.update_buy(Decimal(price), Decimal(size))
    broker._positions[HOLDER] = {"ABCD": position}
    broker._positions[OTHER] = {}
    return broker, engine


def _apply(
    broker: Broker,
    events: list[CorporateEventDTO],
    asset_class: AssetClass = AssetClass.STOCK,
):
    return broker.apply_corporate_events(
        events,
        {1: "ABCD"},
        {"ABCD": asset_class},
        {"ABCD": CLOSE},
        [HOLDER, OTHER],
    )


def _equity(events: list[BaseEventDTO]) -> list[EquityEventDTO]:
    return [e for e in events if isinstance(e, EquityEventDTO)]


def test_two_for_one_doubles_the_position_without_changing_its_value(
    captured_events,
):
    broker, engine = _setup(100, "10")

    applied = _apply(broker, [_split(2.0)])

    position = broker.get_positions(HOLDER)["ABCD"]
    assert position.size == 200
    assert position.avg_price == Decimal("5")
    assert position.total_cost == Decimal("1000")
    split = applied[HOLDER].splits[0]
    assert (split.size_before, split.size_after) == (100, 200)
    assert (split.avg_price_before, split.avg_price_after) == (10, 5)
    assert engine.cash[HOLDER] == 0
    [event] = _equity(captured_events)
    assert (event.event_type, event.quantity, event.price) == (
        EquityEventType.SPLIT,
        Decimal(100),
        Decimal(0),
    )


def test_bonus_of_ten_percent_sells_the_fraction_at_the_close(captured_events):
    """15 ações com bonificação de 10% viram 16,5: ficam 16 e meia ação vai ao caixa."""
    broker, engine = _setup(15, "10")

    applied = _apply(broker, [_split(1.1)])

    position = broker.get_positions(HOLDER)["ABCD"]
    assert position.size == 16
    assert engine.cash[HOLDER] == Decimal("10")
    split = applied[HOLDER].splits[0]
    assert (split.fraction_sold, split.fraction_amount) == (Decimal("0.5"), 10)
    assert [(e.event_type, e.quantity, e.price) for e in _equity(captured_events)] == [
        (EquityEventType.SPLIT, Decimal("1.5"), Decimal(0)),
        (EquityEventType.FRACTION_SELL, Decimal("0.5"), CLOSE),
    ]


def test_reverse_split_shrinks_the_position_and_keeps_the_cost(captured_events):
    broker, engine = _setup(100, "2")

    _apply(broker, [_split(0.1)])

    position = broker.get_positions(HOLDER)["ABCD"]
    assert position.size == 10
    assert position.total_cost == Decimal("200")
    assert position.avg_price == Decimal("20")
    assert engine.cash[HOLDER] == 0
    [event] = _equity(captured_events)
    assert event.quantity == Decimal("-90")


def test_reverse_split_leaving_less_than_one_share_sells_it_all(captured_events):
    broker, engine = _setup(5, "2")

    _apply(broker, [_split(0.1)])

    assert broker.get_positions(HOLDER) == {}
    assert engine.cash[HOLDER] == Decimal("10")


def test_crypto_keeps_the_fraction(captured_events):
    broker, engine = _setup("1.5", "100")

    _apply(broker, [_split(3.0)], AssetClass.CRYPTO)

    assert broker.get_positions(HOLDER)["ABCD"].size == Decimal("4.5")
    assert engine.cash[HOLDER] == 0
    assert [e.event_type for e in _equity(captured_events)] == [EquityEventType.SPLIT]


def test_dividend_pays_the_value_times_the_opening_position(captured_events):
    broker, engine = _setup(150)

    applied = _apply(broker, [_dividend(0.45)])

    # 150 cotas a 0,45 por cota dão 67,50; quem não tem a ação não recebe
    assert engine.dividends == [(HOLDER, "ABCD", Decimal("67.50"))]
    assert engine.cash[OTHER] == 0
    assert OTHER not in applied
    assert applied[HOLDER].dividends[0].amount == Decimal("67.50")
    assert _equity(captured_events) == []


def test_dividend_truncates_to_the_cent(captured_events):
    broker, engine = _setup(3)

    _apply(broker, [_dividend(0.3333)])

    assert engine.dividends == [(HOLDER, "ABCD", Decimal("0.99"))]


def test_dividend_smaller_than_a_cent_is_not_paid(captured_events):
    broker, engine = _setup(1)

    applied = _apply(broker, [_dividend(0.004)])

    assert engine.dividends == []
    assert applied[HOLDER].dividends == []


def test_dividend_on_the_split_day_is_paid_on_the_new_quantity(captured_events):
    broker, engine = _setup(100)

    _apply(broker, [_dividend(0.1), _split(2.0)])

    assert engine.dividends == [(HOLDER, "ABCD", Decimal("20.00"))]


def test_replay_reaches_the_same_state_as_the_live_game(
    captured_events, monkeypatch: pytest.MonkeyPatch
):
    broker, _ = _setup(15, "10")
    buy = EquityEventDTO(
        simulation_id=1,
        user_id=1,
        event_date=date(2020, 1, 2),
        ticker="ABCD",
        event_type=EquityEventType.BUY,
        quantity=Decimal(15),
        price=Decimal(10),
    )

    _apply(broker, [_split(1.1), _split(0.5), _dividend(0.2)])
    live = broker.get_positions(HOLDER)["ABCD"]

    history = [buy, *_equity(captured_events)]
    monkeypatch.setattr(UserManager, "get_user_id", lambda _: 1)
    monkeypatch.setattr(repository.portfolio, "get_equity_events", lambda _: history)
    replayed = load_positions(HOLDER)["ABCD"]

    assert (replayed.size, replayed.total_cost, replayed.avg_price) == (
        live.size,
        live.total_cost,
        live.avg_price,
    )
