from backend.features.variable_income.broker import Broker
from backend.features.variable_income.entities.order import (
    Order,
    OrderAction,
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
        if order.status != OrderStatus.PENDING:
            raise ValueError("Ordem inválida")

        # Tenta executar a ordem entre os players
        self._match_players_orders(order)

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

    def cancel(self, *, order_id: str, client_id: str) -> bool:
        """
        Cancela uma ordem pendente ou parcialmente executada.
        Retorna True se cancelada, False se não encontrada.
        """
        order = self.order_book.find(order_id)

        if not order:
            return False

        if order.client_id != client_id:
            raise PermissionError("Ordem não pertence ao cliente")

        if order.status not in (OrderStatus.PENDING, OrderStatus.PARTIAL):
            raise ValueError("Ordem não pode ser cancelada")

        self.order_book.remove_by_id(order_id)

        order.status = OrderStatus.CANCELED
        order.remaining = 0

        return True

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

    def _execute_player_trade(
        self,
        *,
        buy: Order,
        sell: Order,
        price: float,
    ):
        """
        Executa uma ordem de compra e uma ordem de venda entre dois players.
        """
        qty = min(buy.remaining, sell.remaining)

        # executa BUY
        self.broker.execute_order(
            client_id=buy.client_id,
            ticker=buy.ticker,
            size=qty,
            price=price,
            action=buy.action,
        )

        # executa SELL
        self.broker.execute_order(
            client_id=sell.client_id,
            ticker=sell.ticker,
            size=qty,
            price=price,
            action=sell.action,
        )

        buy.remaining -= qty
        sell.remaining -= qty

        buy.status = OrderStatus.EXECUTED if buy.remaining == 0 else OrderStatus.PARTIAL
        sell.status = (
            OrderStatus.EXECUTED if sell.remaining == 0 else OrderStatus.PARTIAL
        )

        if buy.remaining == 0:
            self.order_book.remove(buy)

        if sell.remaining == 0:
            self.order_book.remove(sell)

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

    def _match_players_orders(self, order: Order):
        if order.action == OrderAction.BUY:
            self._match_player_buy(order)
        else:
            self._match_player_sell(order)

    def _match_player_buy(self, buy: Order):
        sells = self.order_book.sell_orders(buy.ticker)

        for sell in list(sells):
            if buy.remaining == 0:
                break

            if buy.order_type == OrderType.LIMIT and sell.price > buy.price:
                break

            trade_price = sell.price
            self._execute_player_trade(buy=buy, sell=sell, price=trade_price)

    def _match_player_sell(self, sell: Order):
        buys = self.order_book.buy_orders(sell.ticker)

        for buy in list(buys):
            if sell.remaining == 0:
                break

            if sell.order_type == OrderType.LIMIT and buy.price < sell.price:
                break

            trade_price = buy.price
            self._execute_player_trade(buy=buy, sell=sell, price=trade_price)
