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


def test_limit_limit_full_fill():
    """Duas ordens LIMIT compativeis devem se executar completamente."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    engine.submit(_limit(client_id="s", price=10, size=5, action=OrderAction.SELL))
    engine.submit(_limit(client_id="b", price=12, size=5, action=OrderAction.BUY))

    assert len(broker.calls) == 1
    assert engine.order_book.get_orders("ABCD") == []


def test_market_limit_full_fill():
    """Uma ordem MARKET deve executar totalmente contra uma LIMIT compativel."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    sell = _limit(client_id="s", price=10, size=5, action=OrderAction.SELL)
    engine.submit(sell)

    engine.submit(_market(client_id="b", size=5, action=OrderAction.BUY))

    assert len(broker.calls) == 1
    assert engine.order_book.get_orders("ABCD") == []


def test_market_without_liquidity_raises():
    """Uma ordem MARKET sem liquidez deve falhar."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    with pytest.raises(ConflictError):
        engine.submit(_market(client_id="b", size=5, action=OrderAction.BUY))


def test_market_without_cash_removes_maker_and_fails():
    """Uma ordem MARKET que falha no broker deve remover o maker e falhar."""
    broker = FakeBroker(raise_for_clients={"s": InsufficentCashError()})
    engine = MatchingEngine(broker)

    maker = _limit(client_id="s", price=10, size=5, action=OrderAction.SELL)
    engine.submit(maker)

    with pytest.raises(ConflictError):
        engine.submit(_market(client_id="b", size=5, action=OrderAction.BUY))

    assert engine.order_book.find(maker.id) is None
    assert len(broker.calls) == 1


def test_limit_without_cash_enters_book_after_removing_maker():
    """Uma LIMIT que falha no broker deve remover o maker e entrar no book."""
    broker = FakeBroker(raise_for_clients={"s": InsufficentCashError()})
    engine = MatchingEngine(broker)

    maker = _limit(client_id="s", price=10, size=5, action=OrderAction.SELL)
    engine.submit(maker)

    taker = _limit(client_id="b", price=12, size=5, action=OrderAction.BUY)
    engine.submit(taker)

    assert engine.order_book.find(maker.id) is None
    assert engine.order_book.find(taker.id) is taker
    assert len(broker.calls) == 1


def test_limit_without_liquidity_enters_book():
    """Uma ordem LIMIT sem contraparte deve entrar no book."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    buy = _limit(client_id="b", price=10, size=5, action=OrderAction.BUY)
    engine.submit(buy)

    assert engine.order_book.find(buy.id) is buy


def test_market_limit_leaves_limit_partial():
    """Uma ordem MARKET pode deixar a LIMIT parcialmente executada."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    sell = _limit(client_id="s", price=10, size=10, action=OrderAction.SELL)
    engine.submit(sell)

    engine.submit(_market(client_id="b", size=4, action=OrderAction.BUY))

    assert sell.remaining == 6
    assert engine.order_book.find(sell.id) is sell


def test_market_price_priority_across_levels():
    """Ordem MARKET deve consumir do melhor preco para o pior."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    engine.submit(_limit(client_id="s1", price=10, size=1, action=OrderAction.SELL))
    engine.submit(_limit(client_id="s2", price=11, size=1, action=OrderAction.SELL))
    engine.submit(_limit(client_id="s3", price=12, size=1, action=OrderAction.SELL))

    engine.submit(_market(client_id="b", size=3, action=OrderAction.BUY))

    prices = [c["price"] for c in broker.calls]
    assert prices == [10, 11, 12]


def test_time_priority_same_price():
    """Ordens com mesmo preco devem respeitar FIFO."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    t0 = datetime.now(UTC)
    engine.submit(
        _limit(client_id="s1", price=10, size=1, action=OrderAction.SELL, created_at=t0)
    )
    engine.submit(
        _limit(
            client_id="s2",
            price=10,
            size=1,
            action=OrderAction.SELL,
            created_at=t0 + timedelta(seconds=1),
        )
    )

    engine.submit(_market(client_id="b", size=1, action=OrderAction.BUY))

    assert broker.calls[0]["maker_client_id"] == "s1"


def test_market_against_many_limits_limits_left():
    """Market contra varios LIMIT deve deixar LIMITs sobrando sem parcial."""
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


def test_market_against_many_limits_last_limit_partial():
    """Market contra varios LIMIT deve deixar o ultimo LIMIT parcial."""
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


def test_market_against_many_limits_insufficient_liquidity():
    """Market contra varios LIMIT deve falhar se faltar liquidez."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    engine.submit(_limit(client_id="s1", price=10, size=2, action=OrderAction.SELL))
    engine.submit(_limit(client_id="s2", price=11, size=2, action=OrderAction.SELL))
    engine.submit(_limit(client_id="s3", price=12, size=2, action=OrderAction.SELL))

    with pytest.raises(ConflictError):
        engine.submit(_market(client_id="b", size=7, action=OrderAction.BUY))

    assert engine.order_book.get_orders("ABCD") == []


def test_market_skips_maker_with_insufficient_position():
    """Market deve ignorar maker com posicao insuficiente e seguir."""
    broker = FakeBroker(raise_for_clients={"s1": InsufficentPositionError()})
    engine = MatchingEngine(broker)

    s1 = _limit(client_id="s1", price=10, size=1, action=OrderAction.SELL)
    s2 = _limit(client_id="s2", price=11, size=1, action=OrderAction.SELL)
    engine.submit(s1)
    engine.submit(s2)

    engine.submit(_market(client_id="b", size=1, action=OrderAction.BUY))

    assert len(broker.calls) == 2
    assert broker.calls[0]["maker_client_id"] == "s1"
    assert broker.calls[1]["maker_client_id"] == "s2"
    assert engine.order_book.find(s1.id) is None
    assert engine.order_book.find(s2.id) is None


def test_limit_against_many_limits_limits_left():
    """LIMIT contra varios LIMIT deve executar e deixar LIMITs sobrando."""
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

    assert taker.remaining == 0
    assert engine.order_book.find(taker.id) is None
    assert engine.order_book.find(s4.id) is s4


def test_limit_against_many_limits_limit_partial_due_to_price():
    """LIMIT contra varios LIMIT deve ficar parcial se o preco limitar."""
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
    assert engine.order_book.find(s3.id) is s3


def test_limit_against_many_limits_insufficient_liquidity():
    """LIMIT contra varios LIMIT deve ficar no book se faltar liquidez."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    s1 = _limit(client_id="s1", price=10, size=2, action=OrderAction.SELL)
    s2 = _limit(client_id="s2", price=11, size=2, action=OrderAction.SELL)

    engine.submit(s1)
    engine.submit(s2)

    taker = _limit(client_id="b", price=11, size=5, action=OrderAction.BUY)
    engine.submit(taker)

    assert taker.remaining == 1
    assert engine.order_book.find(taker.id) is taker
    assert engine.order_book.find(s1.id) is None
    assert engine.order_book.find(s2.id) is None


def test_market_sell_skips_buyer_with_insufficient_cash():
    """Market SELL deve ignorar BUY sem saldo e seguir."""
    broker = FakeBroker(raise_for_clients={"b1": InsufficentCashError()})
    engine = MatchingEngine(broker)

    b1 = _limit(client_id="b1", price=12, size=1, action=OrderAction.BUY)
    b2 = _limit(client_id="b2", price=11, size=1, action=OrderAction.BUY)
    engine.submit(b1)
    engine.submit(b2)

    engine.submit(_market(client_id="s", size=1, action=OrderAction.SELL))

    assert len(broker.calls) == 2
    assert broker.calls[0]["maker_client_id"] == "b1"
    assert broker.calls[1]["maker_client_id"] == "b2"
    assert engine.order_book.find(b1.id) is None
    assert engine.order_book.find(b2.id) is None


def test_invalid_limit_does_not_block_other_valid_limits():
    """LIMIT invalida deve ser removida sem bloquear execucao das outras."""
    broker = FakeBroker(raise_for_clients={"s2": InsufficentCashError()})
    engine = MatchingEngine(broker)

    valid1 = _limit(client_id="s1", price=10, size=1, action=OrderAction.SELL)
    invalid = _limit(client_id="s2", price=11, size=1, action=OrderAction.SELL)
    valid2 = _limit(client_id="s3", price=12, size=1, action=OrderAction.SELL)

    engine.submit(valid1)
    engine.submit(invalid)
    engine.submit(valid2)

    engine.submit(_market(client_id="b", size=2, action=OrderAction.BUY))

    assert engine.order_book.find(invalid.id) is None
    assert engine.order_book.find(valid1.id) is None
    assert engine.order_book.find(valid2.id) is None
