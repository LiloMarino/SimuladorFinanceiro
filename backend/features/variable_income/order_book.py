from collections import defaultdict

from backend.features.variable_income.entities.order import LimitOrder, OrderAction


class OrderBook:
    def __init__(self):
        self._buy: dict[str, list[LimitOrder]] = defaultdict(list)
        self._sell: dict[str, list[LimitOrder]] = defaultdict(list)

    def add(self, order: LimitOrder):
        book = self._buy if order.action == OrderAction.BUY else self._sell
        book[order.ticker].append(order)

    def remove(self, order: LimitOrder):
        book = self._buy if order.action == OrderAction.BUY else self._sell
        book[order.ticker].remove(order)

    def buy_orders(self, ticker: str) -> list[LimitOrder]:
        return sorted(
            self._buy[ticker],
            key=lambda o: (o.price, o.timestamp),
            reverse=True,
        )

    def sell_orders(self, ticker: str) -> list[LimitOrder]:
        return sorted(
            self._sell[ticker],
            key=lambda o: (o.price, o.timestamp),
        )

    def best_buy(self, ticker: str) -> LimitOrder | None:
        orders = self.buy_orders(ticker)
        return orders[0] if orders else None

    def best_sell(self, ticker: str) -> LimitOrder | None:
        orders = self.sell_orders(ticker)
        return orders[0] if orders else None

    def find(self, order_id: str) -> LimitOrder | None:
        for book in (self._buy, self._sell):
            for orders in book.values():
                for order in orders:
                    if order.id == order_id:
                        return order
        return None

    def remove_by_id(self, order_id: str) -> LimitOrder | None:
        for book in (self._buy, self._sell):
            for orders in book.values():
                for order in list(orders):
                    if order.id == order_id:
                        orders.remove(order)
                        return order
        return None
