from __future__ import annotations

import threading
from datetime import date
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.events.base_event import BaseEventDTO
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.enum import EquityEventType
from backend.core.exceptions import InsufficentCashError, InsufficentPositionError
from backend.core.runtime.user_manager import UserManager
from backend.features.variable_income.broker import Broker, load_positions, to_money
from backend.features.variable_income.entities.order import (
    LimitOrder,
    MarketOrder,
    OrderAction,
)
from backend.features.variable_income.market_liquidity import MarketLiquidity
from backend.features.variable_income.matching_engine import MatchingEngine
from tests.fakes import FakeSimulationEngine, client

BUYER = client("buyer")
SELLER = client("seller")
MARKET = MarketLiquidity.MARKET_CLIENT_ID

type History = dict[str, list[tuple[EquityEventType, str, int]]]


@pytest.fixture
def history(monkeypatch: pytest.MonkeyPatch, captured_events: list[BaseEventDTO]):
    """Define o histórico de compras/vendas que `load_positions` lê de cada cliente."""

    def _set(by_client: History) -> None:
        user_ids = {client(name): i for i, name in enumerate(by_client, start=1)}
        events = {
            user_ids[client(name)]: [
                EquityEventDTO(
                    simulation_id=1,
                    user_id=user_ids[client(name)],
                    event_date=date(2020, 1, 2),
                    ticker="ABCD",
                    event_type=event_type,
                    price=Decimal(price),
                    quantity=quantity,
                )
                for event_type, price, quantity in trades
            ]
            for name, trades in by_client.items()
        }
        monkeypatch.setattr(
            UserManager, "get_user_id", lambda client_id: user_ids.get(client_id, 0)
        )
        monkeypatch.setattr(
            repository.portfolio,
            "get_equity_events",
            lambda user_id: events.get(user_id, []),
        )

    _set({})
    return _set


def _broker(**cash: str) -> tuple[Broker, FakeSimulationEngine]:
    engine = FakeSimulationEngine(
        cash={client(name): Decimal(value) for name, value in cash.items()}
    )
    return Broker(engine, threading.RLock()), engine


def _limit(client_id, action: OrderAction, price: float, size: int) -> LimitOrder:
    return LimitOrder(
        client_id=client_id, ticker="ABCD", price=price, size=size, action=action
    )


def _market(client_id, action: OrderAction, size: int) -> MarketOrder:
    return MarketOrder(client_id=client_id, ticker="ABCD", size=size, action=action)


def test_to_money_keeps_decimal_text():
    """Preço float vira Decimal pelo texto, sem a expansão binária."""
    assert to_money(0.1) == Decimal("0.1")
    assert to_money(10.25) == Decimal("10.25")


def test_load_positions_replays_and_drops_closed(history):
    """Reconstrução repete compras e vendas e descarta posição zerada."""
    history(
        {
            "buyer": [
                (EquityEventType.BUY, "10", 10),
                (EquityEventType.BUY, "13", 5),
                (EquityEventType.SELL, "0", 6),
            ]
        }
    )

    position = load_positions(BUYER)["ABCD"]

    assert position.size == 9
    assert position.avg_price == Decimal("11")
    history({"buyer": [(EquityEventType.BUY, "10", 3), (EquityEventType.SELL, "0", 3)]})
    assert load_positions(BUYER) == {}


def test_reserve_buy_debits_limit_cost(history):
    """LIMIT BUY reserva o custo pelo preço limite já na entrada."""
    broker, engine = _broker(buyer="1000")

    broker.reserve_limit_order(_limit(BUYER, OrderAction.BUY, 12, 10))

    assert engine.cash[BUYER] == Decimal("880")


def test_reserve_buy_without_cash_is_rejected(history):
    """LIMIT BUY acima do saldo falha e não mexe no caixa."""
    broker, engine = _broker(buyer="100")

    with pytest.raises(InsufficentCashError):
        broker.reserve_limit_order(_limit(BUYER, OrderAction.BUY, 12, 10))

    assert engine.cash[BUYER] == Decimal("100")


def test_reserve_sell_without_position_is_rejected(history):
    """LIMIT SELL sem posição no ativo falha."""
    broker, _ = _broker()

    with pytest.raises(InsufficentPositionError):
        broker.reserve_limit_order(_limit(SELLER, OrderAction.SELL, 10, 1))


def test_reserve_sell_blocks_position_quantity(history):
    """LIMIT SELL bloqueia a quantidade, que deixa de estar disponível."""
    history({"seller": [(EquityEventType.BUY, "8", 10)]})
    broker, _ = _broker()

    broker.reserve_limit_order(_limit(SELLER, OrderAction.SELL, 10, 4))

    assert broker.get_available_position(SELLER, "ABCD") == 6
    with pytest.raises(InsufficentPositionError):
        broker.reserve_limit_order(_limit(SELLER, OrderAction.SELL, 10, 7))


def test_release_buy_refunds_only_remaining(history):
    """Liberar LIMIT BUY devolve o custo só da parte não executada."""
    broker, engine = _broker(buyer="1000")
    order = _limit(BUYER, OrderAction.BUY, 12, 10)
    broker.reserve_limit_order(order)
    order.remaining = 4

    broker.release_limit_order(order)

    assert engine.cash[BUYER] == Decimal("928")


def test_limit_buy_filled_below_limit_refunds_difference(history, captured_events):
    """LIMIT BUY executada abaixo do limite estorna a diferença reservada."""
    broker, engine = _broker(buyer="1000")
    order = _limit(BUYER, OrderAction.BUY, 12, 10)
    broker.reserve_limit_order(order)

    broker.execute_trade(
        taker_order=order,
        maker_order=_limit(MARKET, OrderAction.SELL, 10, 10),
        size=10,
        price=10,
    )

    position = broker.get_positions(BUYER)["ABCD"]
    assert engine.cash[BUYER] == Decimal("900")
    assert (position.size, position.avg_price) == (10, Decimal("10"))
    assert len(captured_events) == 1
    assert isinstance(captured_events[0], EquityEventDTO)
    assert captured_events[0].event_type == EquityEventType.BUY
    assert captured_events[0].price == Decimal("10")


def test_market_buy_debits_trade_cost(history):
    """MARKET BUY debita o custo da execução no preço do maker."""
    broker, engine = _broker(buyer="1000")

    broker.execute_trade(
        taker_order=_market(BUYER, OrderAction.BUY, 5),
        maker_order=_limit(MARKET, OrderAction.SELL, 10.5, 5),
        size=5,
        price=10.5,
    )

    assert engine.cash[BUYER] == Decimal("947.5")


def test_market_buy_without_cash_is_rejected(history, captured_events):
    """MARKET BUY sem saldo falha antes de mover caixa, posição ou evento."""
    broker, engine = _broker(buyer="40")

    with pytest.raises(InsufficentCashError):
        broker.execute_trade(
            taker_order=_market(BUYER, OrderAction.BUY, 5),
            maker_order=_limit(MARKET, OrderAction.SELL, 10, 5),
            size=5,
            price=10,
        )

    assert engine.cash[BUYER] == Decimal("40")
    assert broker.get_positions(BUYER) == {}
    assert captured_events == []


def test_market_sell_beyond_free_quantity_is_rejected(history):
    """MARKET SELL não usa a quantidade reservada por LIMIT SELL."""
    history({"seller": [(EquityEventType.BUY, "8", 10)]})
    broker, _ = _broker()
    broker.reserve_limit_order(_limit(SELLER, OrderAction.SELL, 20, 8))

    with pytest.raises(InsufficentPositionError):
        broker.execute_trade(
            taker_order=_market(SELLER, OrderAction.SELL, 5),
            maker_order=_limit(MARKET, OrderAction.BUY, 10, 5),
            size=5,
            price=10,
        )


def test_limit_sell_credits_cash_and_closes_position(history, captured_events):
    """LIMIT SELL total credita o valor, consome a reserva e fecha a posição."""
    history({"seller": [(EquityEventType.BUY, "8", 10)]})
    broker, engine = _broker()
    order = _limit(SELLER, OrderAction.SELL, 11, 10)
    broker.reserve_limit_order(order)

    broker.execute_trade(
        taker_order=order,
        maker_order=_limit(MARKET, OrderAction.BUY, 11, 10),
        size=10,
        price=11,
    )

    assert engine.cash[SELLER] == Decimal("110")
    assert broker.get_positions(SELLER) == {}
    assert [e.event_type for e in captured_events if isinstance(e, EquityEventDTO)] == [
        EquityEventType.SELL
    ]


def test_market_liquidity_side_has_no_cash_or_events(history, captured_events):
    """Do lado da liquidez sintética não há caixa, posição nem evento."""
    broker, engine = _broker(buyer="1000")

    broker.execute_trade(
        taker_order=_market(BUYER, OrderAction.BUY, 2),
        maker_order=_limit(MARKET, OrderAction.SELL, 10, 2),
        size=2,
        price=10,
    )

    assert MARKET not in engine.cash
    assert len(captured_events) == 1


def test_non_positive_size_is_rejected(history):
    """Trade com quantidade zero ou negativa falha."""
    broker, _ = _broker(buyer="1000")

    with pytest.raises(ValueError):
        broker.execute_trade(
            taker_order=_market(BUYER, OrderAction.BUY, 1),
            maker_order=_limit(MARKET, OrderAction.SELL, 10, 1),
            size=0,
            price=10,
        )


def test_matching_with_real_broker_conserves_cash_and_shares(history, captured_events):
    """Negócio entre dois jogadores conserva caixa e ações e emite BUY e SELL."""
    history({"seller": [(EquityEventType.BUY, "8", 10)]})
    broker, engine = _broker(buyer="1000")
    matching = MatchingEngine(broker)

    sell = _limit(SELLER, OrderAction.SELL, 10, 10)
    matching.submit(sell)
    matching.submit(_limit(BUYER, OrderAction.BUY, 12, 6))

    buyer_position = broker.get_positions(BUYER)["ABCD"]
    seller_position = broker.get_positions(SELLER)["ABCD"]
    # Comprador reservou 72 a R$ 12 e recebeu de volta 12 por executar a R$ 10
    assert engine.cash[BUYER] == Decimal("940")
    assert engine.cash[SELLER] == Decimal("60")
    assert engine.cash[BUYER] + engine.cash[SELLER] == Decimal("1000")
    assert (buyer_position.size, buyer_position.avg_price) == (6, Decimal("10"))
    assert (seller_position.size, seller_position.reserved) == (4, 4)
    # Taker executa antes do maker
    assert [e.event_type for e in captured_events if isinstance(e, EquityEventDTO)] == [
        EquityEventType.BUY,
        EquityEventType.SELL,
    ]


def test_cancel_pending_limit_returns_reservation(history):
    """Cancelar LIMIT pendente devolve o caixa reservado e tira a ordem do book."""
    broker, engine = _broker(buyer="1000")
    matching = MatchingEngine(broker)
    order = _limit(BUYER, OrderAction.BUY, 12, 10)
    matching.submit(order)

    assert matching.cancel(order_id=order.id, client_id=BUYER)

    assert engine.cash[BUYER] == Decimal("1000")
    assert matching.order_book.find(order.id) is None
