from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

import backend.features.variable_income.matching_engine as me
from backend.core.enum import OrderAction, OrderStatus
from backend.core.exceptions import InsufficentCashError, InsufficentPositionError
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.runtime import user_manager
from backend.features.variable_income.broker import Broker
from backend.features.variable_income.entities.order import (
    MARKET_CLIENT_ID,
    LimitOrder,
    MarketOrder,
)
from backend.features.variable_income.matching_engine import MatchingEngine


class FakeBroker(Broker):
    def __init__(self, *, fail_for: dict[str, Exception] | None = None):
        self.fail_for = fail_for or {}
        self.calls: list[dict] = []
        self.released: list[LimitOrder] = []
        # Converter chaves string para UUID
        self._fail_for_uuids = {
            uuid.uuid5(uuid.NAMESPACE_DNS, k): v for k, v in self.fail_for.items()
        }

    def reserve_limit_order(self, order: LimitOrder) -> None:
        client_id = order.client_id
        if client_id in self._fail_for_uuids:
            raise self._fail_for_uuids[client_id]

    def release_limit_order(self, order: LimitOrder) -> None:
        self.released.append(order)

    def market_buy_limit(self, order: MarketOrder, price: float) -> Decimal:
        # Sem caixa no fake: o teto da compra é o que falta da ordem
        return order.remaining

    def execute_trade(self, **kwargs):
        self.calls.append(kwargs)

        taker = kwargs.get("taker_order")
        maker = kwargs.get("maker_order")

        for order in (taker, maker):
            if order and order.client_id in self._fail_for_uuids:
                raise self._fail_for_uuids[order.client_id]


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
    uuid_client_id = uuid.uuid5(uuid.NAMESPACE_DNS, client_id)
    return LimitOrder(
        placed_on=date(2020, 1, 2),
        client_id=uuid_client_id,
        ticker="ABCD",
        price=price,
        size=Decimal(size),
        action=action,
        created_at=created_at or datetime.now(UTC),
    )


def _market(
    *,
    client_id: str,
    size: int,
    action: OrderAction,
) -> MarketOrder:
    uuid_client_id = uuid.uuid5(uuid.NAMESPACE_DNS, client_id)
    return MarketOrder(
        placed_on=date(2020, 1, 2),
        client_id=uuid_client_id,
        ticker="ABCD",
        size=Decimal(size),
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
    taker = call["taker_order"]
    maker = call["maker_order"]

    taker_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, taker_client_id)
    maker_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, maker_client_id)

    assert taker.client_id == taker_uuid
    assert maker.client_id == maker_uuid
    assert taker.ticker == "ABCD"
    assert maker.ticker == "ABCD"
    assert call["size"] == size
    assert call["price"] == price
    assert taker.action == taker_action
    assert maker.action == maker_action


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
    """Market contra vários LIMIT deve executar e falhar no último."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    s1 = _limit(client_id="s1", price=10, size=2, action=OrderAction.SELL)
    s2 = _limit(client_id="s2", price=11, size=2, action=OrderAction.SELL)
    s3 = _limit(client_id="s3", price=12, size=2, action=OrderAction.SELL)
    engine.submit(s1)
    engine.submit(s2)
    engine.submit(s3)

    engine.submit(_market(client_id="b", size=7, action=OrderAction.BUY))

    assert len(broker.calls) == 3
    for s in (s1, s2, s3):
        assert engine.order_book.find(s.id) is None
        assert s.remaining == 0
        assert s.status == OrderStatus.EXECUTED


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


def test_limit_against_same_price_limit_partial_due_to_price():
    """LIMIT contra LIMIT do mesmo preço deve ficar parcial se o tamanho limitar."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)

    s1 = _limit(client_id="s1", price=10, size=2, action=OrderAction.SELL)
    s2 = _limit(client_id="s2", price=10, size=3, action=OrderAction.SELL)

    engine.submit(s1)
    engine.submit(s2)

    taker = _limit(client_id="b", price=10, size=4, action=OrderAction.BUY)
    engine.submit(taker)

    assert engine.order_book.find(taker.id) is None
    assert taker.remaining == 0
    assert taker.status == OrderStatus.EXECUTED

    assert engine.order_book.find(s1.id) is None
    assert s1.remaining == 0
    assert s1.status == OrderStatus.EXECUTED

    assert engine.order_book.find(s2.id) is s2
    assert s2.remaining == 1
    assert s2.status == OrderStatus.PARTIAL

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
        price=10,
        taker_action=OrderAction.BUY,
        maker_action=OrderAction.SELL,
    )


def test_limit_without_cash_is_rejected():
    """LIMIT BUY sem saldo deve ser rejeitada e não entrar no book."""
    broker = FakeBroker(
        fail_for={"b": InsufficentCashError()},
    )
    engine = MatchingEngine(broker)

    sell = _limit(client_id="s", price=10, size=5, action=OrderAction.SELL)
    engine.submit(sell)

    with pytest.raises(InsufficentCashError):
        engine.submit(_limit(client_id="b", price=12, size=5, action=OrderAction.BUY))

    # Book intacto
    assert engine.order_book.find(sell.id) is sell
    assert sell.remaining == 5
    assert sell.status == OrderStatus.PENDING


def test_market_without_cash_is_rejected():
    """MARKET BUY sem saldo deve falhar e não consumir liquidez."""
    broker = FakeBroker(
        fail_for={"b": InsufficentCashError()},
    )
    engine = MatchingEngine(broker)

    sell = _limit(client_id="s", price=10, size=5, action=OrderAction.SELL)
    engine.submit(sell)

    with pytest.raises(InsufficentCashError):
        engine.submit(_market(client_id="b", size=3, action=OrderAction.BUY))

    # Book intacto
    assert engine.order_book.find(sell.id) is sell
    assert sell.remaining == 5
    assert sell.status == OrderStatus.PENDING


def test_limit_sell_without_position_is_rejected():
    """LIMIT SELL sem posição deve ser rejeitada."""
    broker = FakeBroker(
        fail_for={"s": InsufficentPositionError()},
    )
    engine = MatchingEngine(broker)

    buy = _limit(client_id="b", price=10, size=5, action=OrderAction.BUY)
    engine.submit(buy)

    with pytest.raises(InsufficentPositionError):
        engine.submit(_limit(client_id="s", price=10, size=5, action=OrderAction.SELL))

    # Book intacto
    assert engine.order_book.find(buy.id) is buy
    assert buy.remaining == 5
    assert buy.status == OrderStatus.PENDING


def test_market_sell_without_position_is_rejected():
    """MARKET SELL sem posição deve falhar e não afetar o book."""
    broker = FakeBroker(
        fail_for={"s": InsufficentPositionError()},
    )
    engine = MatchingEngine(broker)

    buy = _limit(client_id="b", price=10, size=5, action=OrderAction.BUY)
    engine.submit(buy)

    with pytest.raises(InsufficentPositionError):
        engine.submit(_market(client_id="s", size=3, action=OrderAction.SELL))

    # Book intacto
    assert engine.order_book.find(buy.id) is buy
    assert buy.remaining == 5
    assert buy.status == OrderStatus.PENDING


# =========================
# Contas do mesmo dono
# =========================

OWNERS = {"ana": 1, "ana_fund": 1, "ana_fund_2": 1, "bia": 2, "bot": 3}


def _uuid(name: str) -> uuid.UUID:
    return uuid.uuid5(uuid.NAMESPACE_DNS, name)


@pytest.fixture
def owned_engine() -> tuple[MatchingEngine, FakeBroker]:
    """Motor em que a conta pessoal da Ana e as duas gestoras dela têm o mesmo dono."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)
    engine.owner_of = lambda client_id: next(
        (owner for name, owner in OWNERS.items() if _uuid(name) == client_id), None
    )
    return engine, broker


@pytest.fixture
def notices(monkeypatch: pytest.MonkeyPatch) -> list[dict]:
    sent: list[dict] = []
    monkeypatch.setattr(me, "notify", lambda **kwargs: sent.append(kwargs))
    return sent


def test_account_skips_the_counter_of_the_same_owner_and_trades_with_the_next(
    owned_engine,
):
    """A gestora compra da próxima venda quando a melhor é da pessoal do gestor."""
    engine, broker = owned_engine
    own = _limit(client_id="ana", price=10, size=5, action=OrderAction.SELL)
    other = _limit(client_id="bia", price=11, size=5, action=OrderAction.SELL)
    engine.submit(own)
    engine.submit(other)

    engine.submit(
        _limit(client_id="ana_fund", price=12, size=5, action=OrderAction.BUY)
    )

    assert len(broker.calls) == 1
    assert_trade(
        broker.calls[0],
        taker_client_id="ana_fund",
        maker_client_id="bia",
        size=5,
        price=11,
        taker_action=OrderAction.BUY,
        maker_action=OrderAction.SELL,
    )
    assert engine.order_book.find(own.id) is own
    assert own.remaining == 5
    assert own.status == OrderStatus.PENDING


def test_remainder_that_would_cross_the_skipped_order_is_canceled_with_notice(
    owned_engine, notices
):
    """A sobra que cruzaria a ordem pulada é cancelada e o jogador recebe o motivo."""
    engine, broker = owned_engine
    own = _limit(client_id="ana", price=10, size=5, action=OrderAction.SELL)
    other = _limit(client_id="bia", price=11, size=2, action=OrderAction.SELL)
    engine.submit(own)
    engine.submit(other)

    buy = _limit(client_id="ana_fund", price=12, size=5, action=OrderAction.BUY)
    engine.submit(buy)

    assert [call["size"] for call in broker.calls] == [2]
    assert buy.status == OrderStatus.CANCELED
    assert buy.remaining == 0
    # A reserva da sobra volta ao jogador
    assert broker.released == [buy]
    assert engine.order_book.find(buy.id) is None
    assert engine.order_book.best_buy("ABCD") is None
    assert engine.order_book.best_sell("ABCD") is own
    [notice] = [n for n in notices if n["event"] == "order_canceled"]
    assert notice["to"] == buy.client_id
    assert notice["payload"]["order_id"] == buy.id
    assert Decimal(notice["payload"]["quantity"]) == 3
    assert "ordem sua ou da gestora que você gere" in notice["payload"]["reason"]


def test_remainder_below_the_skipped_price_rests_in_the_book(owned_engine):
    """A sobra que não cruza a ordem pulada entra no book normalmente."""
    engine, broker = owned_engine
    own = _limit(client_id="ana", price=10, size=5, action=OrderAction.SELL)
    engine.submit(own)

    buy = _limit(client_id="ana_fund", price=9, size=5, action=OrderAction.BUY)
    engine.submit(buy)

    assert broker.calls == []
    assert engine.order_book.find(buy.id) is buy
    assert buy.status == OrderStatus.PENDING


def test_sell_skips_the_buy_of_the_same_owner_and_cancels_the_crossing_remainder(
    owned_engine, notices
):
    """A venda também pula a compra do mesmo dono e cancela a sobra que a cruzaria."""
    engine, broker = owned_engine
    own = _limit(client_id="ana_fund", price=12, size=5, action=OrderAction.BUY)
    other = _limit(client_id="bia", price=11, size=3, action=OrderAction.BUY)
    engine.submit(own)
    engine.submit(other)

    sell = _limit(client_id="ana", price=10, size=5, action=OrderAction.SELL)
    engine.submit(sell)

    assert [(call["size"], call["price"]) for call in broker.calls] == [(3, 11)]
    assert sell.status == OrderStatus.CANCELED
    assert engine.order_book.find(own.id) is own
    assert any(n["event"] == "order_canceled" for n in notices)


def test_player_does_not_trade_with_their_own_order(owned_engine, notices):
    """A compra de um jogador não executa contra a venda dele mesmo."""
    engine, broker = owned_engine
    sell = _limit(client_id="ana", price=10, size=5, action=OrderAction.SELL)
    engine.submit(sell)

    buy = _limit(client_id="ana", price=10, size=5, action=OrderAction.BUY)
    engine.submit(buy)

    assert broker.calls == []
    assert buy.status == OrderStatus.CANCELED
    assert engine.order_book.find(sell.id) is sell
    assert engine.order_book.get_orders("ABCD") == [sell]


def test_two_funds_of_the_same_manager_do_not_trade(owned_engine):
    """Duas gestoras do mesmo gestor não negociam entre si."""
    engine, broker = owned_engine
    sale = _limit(client_id="ana_fund", price=10, size=5, action=OrderAction.SELL)
    engine.submit(sale)

    purchase = _limit(client_id="ana_fund_2", price=10, size=5, action=OrderAction.BUY)
    engine.submit(purchase)

    assert broker.calls == []
    assert purchase.status == OrderStatus.CANCELED
    assert engine.order_book.get_orders("ABCD") == [sale]


def test_market_order_skips_the_own_order_and_follows(owned_engine):
    """A ordem a mercado pula a do mesmo dono e executa na próxima."""
    engine, broker = owned_engine
    engine.submit(_limit(client_id="ana", price=10, size=5, action=OrderAction.SELL))
    engine.submit(_limit(client_id="bia", price=11, size=5, action=OrderAction.SELL))

    engine.submit(_market(client_id="ana_fund", size=5, action=OrderAction.BUY))

    assert_trade(
        broker.calls[0],
        taker_client_id="ana_fund",
        maker_client_id="bia",
        size=5,
        price=11,
        taker_action=OrderAction.BUY,
        maker_action=OrderAction.SELL,
    )


def test_market_order_with_only_the_own_order_has_no_liquidity(owned_engine):
    """Sem outra contraparte, a mercado termina como termina sem liquidez."""
    engine, broker = owned_engine
    own = _limit(client_id="ana", price=10, size=5, action=OrderAction.SELL)
    engine.submit(own)

    with pytest.raises(ConflictError, match="Sem liquidez"):
        engine.submit(_market(client_id="ana_fund", size=5, action=OrderAction.BUY))

    assert broker.calls == []
    assert engine.order_book.find(own.id) is own


def test_different_owners_trade_as_before(owned_engine):
    """Bot e jogador de donos diferentes seguem negociando."""
    engine, broker = owned_engine
    engine.submit(_limit(client_id="bot", price=10, size=5, action=OrderAction.SELL))
    engine.submit(_limit(client_id="bia", price=10, size=5, action=OrderAction.BUY))

    assert len(broker.calls) == 1


def test_synthetic_market_account_is_never_locked(owned_engine):
    """O Mercado não tem dono: nunca é pulado, nem pula."""
    engine, broker = owned_engine
    engine.submit(
        LimitOrder(
            placed_on=date(2020, 1, 2),
            client_id=MARKET_CLIENT_ID,
            ticker="ABCD",
            price=10,
            size=Decimal(5),
            action=OrderAction.SELL,
        )
    )

    engine.submit(_limit(client_id="ana", price=10, size=5, action=OrderAction.BUY))

    assert len(broker.calls) == 1


def test_skipped_order_executes_later_with_a_third_party(owned_engine):
    """A ordem pulada continua no book e executa quando chega um terceiro."""
    engine, broker = owned_engine
    own = _limit(client_id="ana", price=10, size=5, action=OrderAction.SELL)
    engine.submit(own)
    engine.submit(
        _limit(client_id="ana_fund", price=10, size=5, action=OrderAction.BUY)
    )

    engine.submit(_limit(client_id="bia", price=10, size=5, action=OrderAction.BUY))

    assert len(broker.calls) == 1
    assert_trade(
        broker.calls[0],
        taker_client_id="bia",
        maker_client_id="ana",
        size=5,
        price=10,
        taker_action=OrderAction.BUY,
        maker_action=OrderAction.SELL,
    )
    assert own.status == OrderStatus.EXECUTED


def test_without_owner_resolver_every_account_trades():
    """Sem o resolvedor de dono, o motor casa como sempre."""
    broker = FakeBroker()
    engine = MatchingEngine(broker)
    engine.submit(_limit(client_id="ana", price=10, size=5, action=OrderAction.SELL))

    engine.submit(_limit(client_id="ana", price=10, size=5, action=OrderAction.BUY))

    assert len(broker.calls) == 1
