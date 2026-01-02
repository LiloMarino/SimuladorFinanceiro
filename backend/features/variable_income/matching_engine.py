from backend.features.variable_income.broker import Broker
from backend.features.variable_income.entities.order import (
    Order,
    OrderStatus,
    OrderType,
)
from backend.features.variable_income.market_data import MarketData
from backend.features.variable_income.order_book import OrderBook


class MatchingEngine:
    def __init__(self, broker: Broker):
        self.broker = broker
        self.market_data = MarketData()
        self.order_book = OrderBook()

    def submit(self, order: Order) -> None:
        """
        Recebe uma nova ordem (market ou limit).
        - MARKET: executa imediatamente contra o mercado
        - LIMIT: adiciona ao order book
        """
        if order.order_type == OrderType.MARKET:
            self._execute_market_order(order)
        else:
            self.order_book.add(order)
            order.status = OrderStatus.PENDING

    def on_tick(self, ticker: str) -> None:
        """
        Chamado a cada novo candle.
        Executa ordens LIMIT que baterem no mercado.
        """
        candles = self.market_data.get_recent(ticker)
        if not candles:
            return

        candle = candles[-1]

        # BUY LIMIT: executa se low <= price
        for order in list(self.order_book.buy_orders(ticker)):
            if order.price is None:
                continue

            if candle.low <= order.price:
                self._execute_limit_order(order, order.price)
                self.order_book.remove(order)

        # SELL LIMIT: executa se high >= price
        for order in list(self.order_book.sell_orders(ticker)):
            if order.price is None:
                continue

            if candle.high >= order.price:
                self._execute_limit_order(order, order.price)
                self.order_book.remove(order)

    def _execute_market_order(self, order: Order) -> None:
        """
        Executa ordem a mercado usando o último preço disponível.
        """
        candles = self.market_data.get_recent(order.ticker)
        if not candles:
            raise ValueError(f"Sem dados de mercado para {order.ticker}")

        price = candles[-1].price
        self._execute_trade(order, price)

    def _execute_limit_order(self, order: Order, price: float) -> None:
        """
        Executa uma ordem LIMIT que foi atingida pelo mercado.
        """
        self._execute_trade(order, price)

    def _execute_trade(self, order: Order, price: float) -> None:
        """
        Executa efetivamente a ordem via Broker.
        """
        self.broker.execute_order(
            client_id=order.client_id,
            ticker=order.ticker,
            size=order.remaining,
            price=price,
            action=order.action,
        )
        order.remaining = 0
        order.status = OrderStatus.EXECUTED
