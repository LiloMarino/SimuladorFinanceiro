from collections import defaultdict

from backend.features.variable_income.entities.order import Order, OrderAction


class OrderBook:
    def __init__(self):
        self._buy: dict[str, list[Order]] = defaultdict(list)
        self._sell: dict[str, list[Order]] = defaultdict(list)

    def add(self, order: Order):
        book = self._buy if order.action == OrderAction.BUY else self._sell
        book[order.ticker].append(order)

    def remove(self, order: Order):
        book = self._buy if order.action == OrderAction.BUY else self._sell
        book[order.ticker].remove(order)

    def buy_orders(self, ticker: str) -> list[Order]:
        return sorted(
            self._buy[ticker],
            key=lambda o: (o.price, o.timestamp),
            reverse=True,
        )

    def sell_orders(self, ticker: str) -> list[Order]:
        return sorted(
            self._sell[ticker],
            key=lambda o: (o.price, o.timestamp),
        )

    def best_buy(self, ticker: str) -> Order | None:
        orders = self.buy_orders(ticker)
        return orders[0] if orders else None

    def best_sell(self, ticker: str) -> Order | None:
        orders = self.sell_orders(ticker)
        return orders[0] if orders else None
