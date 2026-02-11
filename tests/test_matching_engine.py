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
    def __init__(
        self,
        *,
        raise_for_clients: dict[str, Exception] | None = None,
        raise_on: str = "maker",
    ):
        self.raise_for_clients = raise_for_clients or {}
        self.raise_on = raise_on
        self.calls: list[dict[str, object]] = []

    def execute_trade_atomic(self, **kwargs):
        self.calls.append(kwargs)

        candidate_ids: list[str | None] = []
        if self.raise_on in ("maker", "either"):
            candidate_ids.append(kwargs.get("maker_client_id"))
        if self.raise_on in ("taker", "either"):
            candidate_ids.append(kwargs.get("taker_client_id"))

        for client_id in candidate_ids:
            if client_id in self.raise_for_clients:
                raise self.raise_for_clients[client_id]


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
    return LimitOrder(
        client_id=client_id,
        ticker="ABCD",
        price=price,
        size=size,
        action=action,
        created_at=created_at or datetime.now(UTC),
    )


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


def assert_trade(
    call: dict,
    *,
    taker_client_id: str,
    maker_client_id: str,
    size: int,
    price: float,
    taker_action: OrderAction,
    maker_action: OrderAction,
) -> None:
    assert call.get("taker_client_id") == taker_client_id
    assert call.get("maker_client_id") == maker_client_id
    assert call.get("ticker") == "ABCD"
    assert call.get("size") == size
    assert call.get("price") == price
    assert call.get("taker_action") == taker_action
    assert call.get("maker_action") == maker_action


def test_limit_limit_full_fill():
    """Duas ordens LIMIT compatíveis devem se executar completamente."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    engine.submit(_limit(client_id="s", price=10, size=5, action=OrderAction.SELL))
    engine.submit(_limit(client_id="b", price=12, size=5, action=OrderAction.BUY))

    assert len(broker.calls) == 1
    assert engine.order_book.get_orders("ABCD") == []
    assert_trade(
        broker.calls[0],
        taker_client_id="b",
        maker_client_id="s",
        size=5,
        price=10,
        taker_action=OrderAction.BUY,
        maker_action=OrderAction.SELL,
    )


def test_market_limit_full_fill():
    """Uma ordem MARKET deve executar totalmente contra uma LIMIT compatível."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    sell = _limit(client_id="s", price=10, size=5, action=OrderAction.SELL)
    engine.submit(sell)

    engine.submit(_market(client_id="b", size=5, action=OrderAction.BUY))

    assert len(broker.calls) == 1
    assert engine.order_book.get_orders("ABCD") == []
    assert_trade(
        broker.calls[0],
        taker_client_id="b",
        maker_client_id="s",
        size=5,
        price=10,
        taker_action=OrderAction.BUY,
        maker_action=OrderAction.SELL,
    )
    assert sell.status == OrderStatus.EXECUTED
    assert sell.remaining == 0


def test_market_without_liquidity_raises():
    """Uma ordem MARKET sem liquidez deve falhar."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    with pytest.raises(ConflictError):
        engine.submit(_market(client_id="b", size=5, action=OrderAction.BUY))

    assert engine.order_book.get_orders("ABCD") == []


def test_limit_without_liquidity_enters_book():
    """Uma ordem LIMIT sem contraparte deve entrar no book."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    buy = _limit(client_id="b", price=10, size=5, action=OrderAction.BUY)
    engine.submit(buy)

    assert engine.order_book.find(buy.id) is buy
    assert buy.status == OrderStatus.PENDING


def test_market_limit_leaves_limit_partial():
    """Uma ordem MARKET pode deixar a LIMIT parcialmente executada."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    sell = _limit(client_id="s", price=10, size=10, action=OrderAction.SELL)
    engine.submit(sell)

    engine.submit(_market(client_id="b", size=4, action=OrderAction.BUY))

    assert sell.remaining == 6
    assert sell.status == OrderStatus.PARTIAL
    assert engine.order_book.find(sell.id) is sell
    assert len(broker.calls) == 1
    assert_trade(
        broker.calls[0],
        taker_client_id="b",
        maker_client_id="s",
        size=4,
        price=10,
        taker_action=OrderAction.BUY,
        maker_action=OrderAction.SELL,
    )


def test_market_price_priority_across_levels():
    """Ordem MARKET deve consumir do melhor preço para o pior."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    engine.submit(_limit(client_id="s1", price=10, size=3, action=OrderAction.SELL))
    engine.submit(_limit(client_id="s2", price=11, size=2, action=OrderAction.SELL))
    engine.submit(_limit(client_id="s3", price=12, size=1, action=OrderAction.SELL))

    engine.submit(_market(client_id="b", size=6, action=OrderAction.BUY))

    assert [c["size"] for c in broker.calls] == [3, 2, 1]
    assert [c["price"] for c in broker.calls] == [10, 11, 12]
    assert engine.order_book.get_orders("ABCD") == []


def test_time_priority_same_price():
    """Ordens com mesmo preço devem respeitar FIFO."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    t0 = datetime.now(UTC)
    limit1 = _limit(
        client_id="s1", price=10, size=3, action=OrderAction.SELL, created_at=t0
    )
    limit2 = _limit(
        client_id="s2",
        price=10,
        size=5,
        action=OrderAction.SELL,
        created_at=t0 + timedelta(seconds=1),
    )
    engine.submit(limit1)
    engine.submit(limit2)
    engine.submit(_market(client_id="b", size=4, action=OrderAction.BUY))

    assert len(broker.calls) == 2
    assert_trade(
        broker.calls[0],
        taker_client_id="b",
        maker_client_id="s1",
        size=3,
        price=10,
        taker_action=OrderAction.BUY,
        maker_action=OrderAction.SELL,
    )
    assert_trade(
        broker.calls[1],
        taker_client_id="b",
        maker_client_id="s2",
        size=1,
        price=10,
        taker_action=OrderAction.BUY,
        maker_action=OrderAction.SELL,
    )
    assert engine.order_book.find(limit1.id) is None
    assert engine.order_book.find(limit2.id) is limit2
    assert limit1.remaining == 0
    assert limit1.status == OrderStatus.EXECUTED
    assert limit2.remaining == 4
    assert limit2.status == OrderStatus.PARTIAL


def test_market_against_many_limits_limits_left():
    """Market contra vários LIMIT deve deixar LIMITs sobrando sem parcial."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    s1 = _limit(client_id="s1", price=10, size=2, action=OrderAction.SELL)
    s2 = _limit(client_id="s2", price=11, size=2, action=OrderAction.SELL)
    s3 = _limit(client_id="s3", price=12, size=2, action=OrderAction.SELL)

    engine.submit(s1)
    engine.submit(s2)
    engine.submit(s3)

    engine.submit(_market(client_id="b", size=4, action=OrderAction.BUY))

    assert engine.order_book.find(s1.id) is None
    assert engine.order_book.find(s2.id) is None
    assert engine.order_book.find(s3.id) is s3
    assert s3.remaining == 2
    assert s3.status == OrderStatus.PENDING


def test_market_against_many_limits_last_limit_partial():
    """Market contra vários LIMIT deve deixar o último LIMIT parcial."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    s1 = _limit(client_id="s1", price=10, size=2, action=OrderAction.SELL)
    s2 = _limit(client_id="s2", price=11, size=2, action=OrderAction.SELL)
    s3 = _limit(client_id="s3", price=12, size=2, action=OrderAction.SELL)

    engine.submit(s1)
    engine.submit(s2)
    engine.submit(s3)

    engine.submit(_market(client_id="b", size=5, action=OrderAction.BUY))

    assert engine.order_book.find(s1.id) is None
    assert engine.order_book.find(s2.id) is None
    assert engine.order_book.find(s3.id) is s3
    assert s3.remaining == 1
    assert s3.status == OrderStatus.PARTIAL


def test_market_against_many_limits_insufficient_liquidity():
    """Market contra vários LIMIT deve falhar se não houver liquidez suficiente e não deve afetar o book."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    s1 = _limit(client_id="s1", price=10, size=2, action=OrderAction.SELL)
    s2 = _limit(client_id="s2", price=11, size=2, action=OrderAction.SELL)
    s3 = _limit(client_id="s3", price=12, size=2, action=OrderAction.SELL)
    engine.submit(s1)
    engine.submit(s2)
    engine.submit(s3)

    with pytest.raises(ConflictError):
        engine.submit(_market(client_id="b", size=7, action=OrderAction.BUY))

    assert len(broker.calls) == 0
    for s in (s1, s2, s3):
        assert engine.order_book.find(s.id) is s
        assert s.remaining == 2
        assert s.status == OrderStatus.PENDING


def test_limit_against_many_limits_limits_left():
    """LIMIT contra vários LIMIT deve executar e deixar LIMITs sobrando."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    s1 = _limit(client_id="s1", price=10, size=1, action=OrderAction.SELL)
    s2 = _limit(client_id="s2", price=11, size=1, action=OrderAction.SELL)
    s3 = _limit(client_id="s3", price=12, size=1, action=OrderAction.SELL)
    s4 = _limit(client_id="s4", price=13, size=1, action=OrderAction.SELL)

    engine.submit(s1)
    engine.submit(s2)
    engine.submit(s3)
    engine.submit(s4)

    taker = _limit(client_id="b", price=12, size=3, action=OrderAction.BUY)
    engine.submit(taker)

    # Taker
    assert taker.remaining == 0
    assert engine.order_book.find(taker.id) is None
    assert taker.status == OrderStatus.EXECUTED

    # Makers
    for s in (s1, s2, s3):
        assert engine.order_book.find(s.id) is None
        assert s.remaining == 0
        assert s.status == OrderStatus.EXECUTED
    assert engine.order_book.find(s4.id) is s4
    assert s4.remaining == 1
    assert s4.status == OrderStatus.PENDING

    # Trades
    for call in broker.calls:
        assert call["price"] in (10, 11, 12)
        assert call["size"] == 1


def test_limit_against_many_limits_limit_partial_due_to_price():
    """LIMIT contra vários LIMIT deve ficar parcial se o preço limitar."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    s1 = _limit(client_id="s1", price=10, size=2, action=OrderAction.SELL)
    s2 = _limit(client_id="s2", price=11, size=2, action=OrderAction.SELL)
    s3 = _limit(client_id="s3", price=12, size=2, action=OrderAction.SELL)

    engine.submit(s1)
    engine.submit(s2)
    engine.submit(s3)

    taker = _limit(client_id="b", price=11, size=5, action=OrderAction.BUY)
    engine.submit(taker)

    assert taker.remaining == 1
    assert engine.order_book.find(taker.id) is taker
    assert taker.status == OrderStatus.PARTIAL

    for s in (s1, s2):
        assert engine.order_book.find(s.id) is None
        assert s.remaining == 0
        assert s.status == OrderStatus.EXECUTED

    assert len(broker.calls) == 2
    assert_trade(
        broker.calls[0],
        taker_client_id="b",
        maker_client_id="s1",
        size=2,
        price=10,
        taker_action=OrderAction.BUY,
        maker_action=OrderAction.SELL,
    )
    assert_trade(
        broker.calls[1],
        taker_client_id="b",
        maker_client_id="s2",
        size=2,
        price=11,
        taker_action=OrderAction.BUY,
        maker_action=OrderAction.SELL,
    )
    assert engine.order_book.find(s3.id) is s3
    assert s3.remaining == 2
    assert s3.status == OrderStatus.PENDING


def test_limit_against_many_limits_insufficient_liquidity():
    """LIMIT contra vários LIMIT deve ficar no book se faltar liquidez."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    s1 = _limit(client_id="s1", price=10, size=2, action=OrderAction.SELL)
    s2 = _limit(client_id="s2", price=11, size=3, action=OrderAction.SELL)

    engine.submit(s1)
    engine.submit(s2)

    taker = _limit(client_id="b", price=11, size=6, action=OrderAction.BUY)
    engine.submit(taker)

    assert taker.remaining == 1
    assert engine.order_book.find(taker.id) is taker
    assert taker.status == OrderStatus.PARTIAL

    for s in (s1, s2):
        assert engine.order_book.find(s.id) is None
        assert s.remaining == 0
        assert s.status == OrderStatus.EXECUTED

    assert len(broker.calls) == 2
    assert_trade(
        broker.calls[0],
        taker_client_id="b",
        maker_client_id="s1",
        size=2,
        price=10,
        taker_action=OrderAction.BUY,
        maker_action=OrderAction.SELL,
    )
    assert_trade(
        broker.calls[1],
        taker_client_id="b",
        maker_client_id="s2",
        size=3,
        price=11,
        taker_action=OrderAction.BUY,
        maker_action=OrderAction.SELL,
    )
