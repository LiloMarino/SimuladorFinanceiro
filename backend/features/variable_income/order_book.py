import heapq
from collections import defaultdict
from datetime import datetime

from backend.features.variable_income.entities.order import (
    LimitOrder,
    Order,
    OrderAction,
)


class OrderBook:
    """
    OrderBook otimizado para ordens LIMIT.
    - Mantém heaps por ticker para pegar melhor preço rapidamente
    - Mantém dict id->order para cancelamento e lookup rápido
    """

    def __init__(self):
        self._buy_heap: dict[str, list[tuple[float, datetime, LimitOrder]]] = (
            defaultdict(list)
        )  # max-heap (preço mais alto primeiro)
        self._sell_heap: dict[str, list[tuple[float, datetime, LimitOrder]]] = (
            defaultdict(list)
        )  # min-heap (preço mais baixo primeiro)
        self._orders_by_id: dict[str, LimitOrder] = {}

    def add(self, order: LimitOrder):
        """Adiciona ordem ao book
        Custo: O(log n) para heap + O(1) para dict
        """
        if order.action == OrderAction.BUY:
            heapq.heappush(
                self._buy_heap[order.ticker], (-order.price, order.timestamp, order)
            )
        else:
            heapq.heappush(
                self._sell_heap[order.ticker], (order.price, order.timestamp, order)
            )

        self._orders_by_id[order.id] = order  # O(1)

    def find(self, order_id: str) -> LimitOrder | None:
        """Lookup instantâneo pela id da ordem.
        Custo: O(1)
        """
        return self._orders_by_id.get(order_id)

    def remove(self, order: LimitOrder):
        """
        Remove ordem do book.
        Usamos lazy delete: apenas removemos do dict, o heap será limpo no pop.
        Custo: O(1)
        """
        self._orders_by_id.pop(order.id, None)

    def best_buy(self, ticker: str) -> LimitOrder | None:
        """
        Retorna melhor BUY disponível.
        Lazy remove ordens canceladas.
        Custo: O(1) para peek, O(log n) se precisar limpar lazy deletes
        """
        while self._buy_heap[ticker]:
            _, _, order = self._buy_heap[ticker][0]
            if order.id in self._orders_by_id:
                return order
            heapq.heappop(self._buy_heap[ticker])  # limpa ordem inválida
        return None

    def best_sell(self, ticker: str) -> LimitOrder | None:
        """
        Retorna melhor SELL disponível.
        Lazy remove ordens canceladas.
        Custo: O(1) para peek, O(log n) se precisar limpar lazy deletes
        """
        while self._sell_heap[ticker]:
            _, _, order = self._sell_heap[ticker][0]
            if order.id in self._orders_by_id:
                return order
            heapq.heappop(self._sell_heap[ticker])
        return None

    def get_orders(self, ticker: str) -> list[Order]:
        """Retorna todas as ordens válidas (BUY + SELL) para um ticker."""
        orders: list[Order] = []

        # BUY
        for _, _, order in self._buy_heap.get(ticker, []):
            if order.id in self._orders_by_id:
                orders.append(order)

        # SELL
        for _, _, order in self._sell_heap.get(ticker, []):
            if order.id in self._orders_by_id:
                orders.append(order)

        return orders
