import heapq
from collections import defaultdict
from collections.abc import Callable
from datetime import datetime
from uuid import UUID

from backend.core.enum import OrderAction
from backend.features.variable_income.entities.order import LimitOrder, Order


class OrderBook:
    """
    Livro de ofertas otimizado para ordens LIMIT.

    Responsável por:
    - Manter heaps por ticker para obter melhor preço em O(log n)
    - Indexar ordens por ID para lookup e cancelamento em O(1)
    - Implementar lazy deletion de ordens canceladas nos heaps
    - Fornecer best buy/sell e listar ordens pendentes por ticker
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
                self._buy_heap[order.ticker], (-order.price, order.created_at, order)
            )
        else:
            heapq.heappush(
                self._sell_heap[order.ticker], (order.price, order.created_at, order)
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

    def best_buy(
        self, ticker: str, skip: Callable[[LimitOrder], bool] | None = None
    ) -> LimitOrder | None:
        """
        Retorna melhor BUY disponível, na prioridade preço-tempo, sem as que `skip` recusa.
        Lazy remove ordens canceladas.
        Custo: O(1) para peek, O(log n) se precisar limpar lazy deletes; a lista só é
        ordenada quando a melhor é recusada por `skip`
        """
        return self._best(self._buy_heap[ticker], skip)

    def best_sell(
        self, ticker: str, skip: Callable[[LimitOrder], bool] | None = None
    ) -> LimitOrder | None:
        """
        Retorna melhor SELL disponível, na prioridade preço-tempo, sem as que `skip` recusa.
        Lazy remove ordens canceladas.
        Custo: O(1) para peek, O(log n) se precisar limpar lazy deletes; a lista só é
        ordenada quando a melhor é recusada por `skip`
        """
        return self._best(self._sell_heap[ticker], skip)

    def _best(
        self,
        heap: list[tuple[float, datetime, LimitOrder]],
        skip: Callable[[LimitOrder], bool] | None,
    ) -> LimitOrder | None:
        while heap:
            _, _, order = heap[0]
            if order.id in self._orders_by_id:
                break
            heapq.heappop(heap)  # limpa ordem inválida
        else:
            return None

        if skip is None or not skip(order):
            return order

        # A recusada continua no book; a próxima na prioridade vem da cópia ordenada
        for _, _, candidate in sorted(heap, key=lambda entry: entry[:2]):
            if candidate.id in self._orders_by_id and not skip(candidate):
                return candidate
        return None

    def all_open(self) -> list[LimitOrder]:
        """Todas as ordens válidas do book, de qualquer ticker."""
        return list(self._orders_by_id.values())

    def orders_of(self, client_id: UUID) -> list[LimitOrder]:
        """Ordens válidas de um cliente, de qualquer ticker."""
        return [o for o in self._orders_by_id.values() if o.client_id == client_id]

    def get_orders(self, ticker: str) -> list[Order]:
        """Ordens válidas do ticker na ordem de prioridade do casamento.

        Compras do maior para o menor preço, depois vendas do menor para o maior;
        no mesmo preço, quem chegou primeiro vem antes.
        """
        buys = sorted(
            (
                entry
                for entry in self._buy_heap.get(ticker, [])
                if entry[2].id in self._orders_by_id
            ),
            key=lambda entry: entry[:2],
        )
        sells = sorted(
            (
                entry
                for entry in self._sell_heap.get(ticker, [])
                if entry[2].id in self._orders_by_id
            ),
            key=lambda entry: entry[:2],
        )
        orders: list[Order] = [order for _, _, order in buys]
        orders.extend(order for _, _, order in sells)
        return orders
