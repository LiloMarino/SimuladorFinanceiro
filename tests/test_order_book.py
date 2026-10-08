from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from backend.features.variable_income.entities.order import LimitOrder, OrderAction
from backend.features.variable_income.order_book import OrderBook

T0 = datetime(2020, 1, 6, tzinfo=UTC)


def _limit(
    price: float,
    action: OrderAction,
    *,
    ticker: str = "ABCD",
    seconds: int = 0,
) -> LimitOrder:
    return LimitOrder(
        client_id=uuid.uuid4(),
        ticker=ticker,
        price=price,
        size=1,
        action=action,
        created_at=T0 + timedelta(seconds=seconds),
    )


def test_best_buy_is_highest_price():
    """Melhor compra é a de maior preço."""
    book = OrderBook()
    best = _limit(11, OrderAction.BUY)
    book.add(_limit(10, OrderAction.BUY))
    book.add(best)
    book.add(_limit(9, OrderAction.BUY))

    assert book.best_buy("ABCD") is best


def test_best_sell_is_lowest_price():
    """Melhor venda é a de menor preço."""
    book = OrderBook()
    best = _limit(9, OrderAction.SELL)
    book.add(_limit(10, OrderAction.SELL))
    book.add(best)

    assert book.best_sell("ABCD") is best


def test_same_price_older_order_wins():
    """No mesmo preço, a ordem mais antiga tem prioridade."""
    book = OrderBook()
    newer = _limit(10, OrderAction.SELL, seconds=5)
    older = _limit(10, OrderAction.SELL, seconds=1)
    book.add(newer)
    book.add(older)

    assert book.best_sell("ABCD") is older


def test_removed_order_is_skipped_as_best():
    """Ordem removida some do topo, da busca e da listagem."""
    book = OrderBook()
    top = _limit(9, OrderAction.SELL)
    next_best = _limit(10, OrderAction.SELL)
    book.add(top)
    book.add(next_best)

    book.remove(top)

    assert book.best_sell("ABCD") is next_best
    assert book.find(top.id) is None
    assert book.get_orders("ABCD") == [next_best]


def test_empty_side_has_no_best():
    """Lado sem ordens não tem melhor oferta."""
    book = OrderBook()
    book.add(_limit(10, OrderAction.SELL))

    assert book.best_buy("ABCD") is None
    assert book.best_sell("WXYZ") is None


def test_get_orders_lists_both_sides_of_one_ticker():
    """Listagem traz compras e vendas do ticker pedido, e só dele."""
    book = OrderBook()
    buy = _limit(9, OrderAction.BUY)
    sell = _limit(11, OrderAction.SELL)
    book.add(buy)
    book.add(sell)
    book.add(_limit(5, OrderAction.BUY, ticker="WXYZ"))

    assert book.get_orders("ABCD") == [buy, sell]
    assert book.find(buy.id) is buy
