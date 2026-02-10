from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

import backend.features.variable_income.matching_engine as me
from backend.core.exceptions import InsufficentCashError, InsufficentPositionError
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.runtime import user_manager
from backend.features.variable_income.broker import Broker
from backend.features.variable_income.entities.order import (
    LimitOrder,
    MarketOrder,
    OrderAction,
    OrderStatus,
)
from backend.features.variable_income.matching_engine import MatchingEngine


class FakeBroker(Broker):
    def __init__(self, *, raise_exc: Exception | None = None):
        self.raise_exc = raise_exc
        self.calls: list[dict[str, object]] = []

    def execute_trade_atomic(self, **kwargs):
        self.calls.append(kwargs)
        if self.raise_exc:
            raise self.raise_exc


@pytest.fixture(autouse=True)
def disable_side_effects(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(me, "notify", lambda **_: None)
    monkeypatch.setattr(
        user_manager.UserManager,
        "get_user",
        lambda _: None,
    )


def _limit(
    *,
    client_id: str,
    price: float,
    size: int,
    action: OrderAction,
    created_at: datetime | None = None,
) -> LimitOrder:
    order = LimitOrder(
        client_id=client_id,
        ticker="ABCD",
        price=price,
        size=size,
        action=action,
        created_at=created_at or datetime.now(UTC),
    )
    return order


def _market(
    *,
    client_id: str,
    size: int,
    action: OrderAction,
) -> MarketOrder:
    return MarketOrder(
        client_id=client_id,
        ticker="ABCD",
        size=size,
        action=action,
    )


def test_limit_limit_full_fill():
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    sell = _limit(client_id="seller", price=10.0, size=5, action=OrderAction.SELL)
    engine.submit(sell)

    buy = _limit(client_id="buyer", price=12.0, size=5, action=OrderAction.BUY)
    engine.submit(buy)

    assert sell.status == OrderStatus.EXECUTED
    assert buy.status == OrderStatus.EXECUTED
    assert sell.remaining == 0
    assert buy.remaining == 0
    assert engine.order_book.get_orders("ABCD") == []
    assert len(broker.calls) == 1
    assert broker.calls[0]["price"] == 10.0
    assert broker.calls[0]["size"] == 5


def test_limit_partial_fill_rests_in_book():
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    sell = _limit(client_id="seller", price=10.0, size=4, action=OrderAction.SELL)
    engine.submit(sell)

    buy = _limit(client_id="buyer", price=12.0, size=10, action=OrderAction.BUY)
    engine.submit(buy)

    assert sell.status == OrderStatus.EXECUTED
    assert buy.status == OrderStatus.PARTIAL
    assert buy.remaining == 6
    assert engine.order_book.find(buy.id) is buy


def test_market_order_full_fill_no_rest():
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    sell = _limit(client_id="seller", price=10.0, size=5, action=OrderAction.SELL)
    engine.submit(sell)

    buy = _market(client_id="buyer", size=5, action=OrderAction.BUY)
    engine.submit(buy)

    assert buy.status == OrderStatus.EXECUTED
    assert buy.remaining == 0
    assert engine.order_book.get_orders("ABCD") == []


def test_market_order_insufficient_liquidity_raises():
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    sell = _limit(client_id="seller", price=10.0, size=3, action=OrderAction.SELL)
    engine.submit(sell)

    buy = _market(client_id="buyer", size=5, action=OrderAction.BUY)
    with pytest.raises(ConflictError):
        engine.submit(buy)
    assert buy.remaining == 2
    assert buy.status == OrderStatus.PARTIAL
    assert engine.order_book.get_orders("ABCD") == []


def test_limit_price_constraint_blocks_execution():
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    sell = _limit(client_id="seller", price=10.0, size=5, action=OrderAction.SELL)
    engine.submit(sell)

    buy = _limit(client_id="buyer", price=9.0, size=5, action=OrderAction.BUY)
    engine.submit(buy)

    assert buy.status == OrderStatus.PENDING
    assert buy.remaining == 5
    assert engine.order_book.find(buy.id) is buy
    assert engine.order_book.find(sell.id) is sell
    assert broker.calls == []


def test_rejection_removes_maker_and_notifies():
    broker = FakeBroker(raise_exc=InsufficentCashError())
    engine = MatchingEngine(broker)

    sell = _limit(client_id="seller", price=10.0, size=5, action=OrderAction.SELL)
    engine.submit(sell)

    buy = _limit(client_id="buyer", price=11.0, size=5, action=OrderAction.BUY)
    engine.submit(buy)

    assert engine.order_book.find(sell.id) is None
    assert engine.order_book.find(buy.id) is buy
    assert buy.status == OrderStatus.PENDING
    assert buy.remaining == 5


def test_price_time_priority_same_price():
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    now = datetime.now(UTC)
    sell_first = _limit(
        client_id="seller_1",
        price=10.0,
        size=1,
        action=OrderAction.SELL,
        created_at=now - timedelta(seconds=10),
    )
    sell_second = _limit(
        client_id="seller_2",
        price=10.0,
        size=1,
        action=OrderAction.SELL,
        created_at=now,
    )

    engine.submit(sell_first)
    engine.submit(sell_second)

    buy = _limit(client_id="buyer", price=12.0, size=1, action=OrderAction.BUY)
    engine.submit(buy)

    assert broker.calls
    assert broker.calls[0]["maker_client_id"] == "seller_1"
    assert engine.order_book.find(sell_first.id) is None
    assert engine.order_book.find(sell_second.id) is sell_second


def test_rejection_with_insufficient_position_removes_maker():
    broker = FakeBroker(raise_exc=InsufficentPositionError())
    engine = MatchingEngine(broker)

    sell = _limit(client_id="seller", price=10.0, size=2, action=OrderAction.SELL)
    engine.submit(sell)

    buy = _limit(client_id="buyer", price=10.0, size=2, action=OrderAction.BUY)
    engine.submit(buy)

    assert engine.order_book.find(sell.id) is None
    assert engine.order_book.find(buy.id) is buy


def test_market_order_never_enters_book():
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    buy = _market(client_id="buyer", size=5, action=OrderAction.BUY)
    with pytest.raises(ConflictError):
        engine.submit(buy)

    assert engine.order_book.get_orders("ABCD") == []


def test_market_order_walks_book_by_best_price():
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    engine.submit(_limit(client_id="s1", price=10, size=1, action=OrderAction.SELL))
    engine.submit(_limit(client_id="s2", price=11, size=1, action=OrderAction.SELL))
    engine.submit(_limit(client_id="s3", price=12, size=1, action=OrderAction.SELL))

    buy = _market(client_id="buyer", size=3, action=OrderAction.BUY)
    engine.submit(buy)

    prices = [c["price"] for c in broker.calls]
    assert prices == [10, 11, 12]
