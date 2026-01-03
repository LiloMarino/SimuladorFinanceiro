from backend.features.variable_income.broker import Broker
from backend.features.variable_income.entities.order import (
    LimitOrder,
    MarketOrder,
    Order,
    OrderAction,
    OrderStatus,
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
        Recebe uma nova ordem:
        - Tenta casar contra ordens do book
        - MARKET: executa saldo no mercado
        - LIMIT: saldo vai pro book
        """
        if order.status != OrderStatus.PENDING:
            raise ValueError("Ordem inválida")

        # 1. Tenta casar contra players
        self._match_players(order)

        # 2. MARKET executa direto no mercado
        if isinstance(order, MarketOrder):
            self._execute_market(order)
            return

        # 3. LIMIT vai pro book
        if isinstance(order, LimitOrder):
            self.order_book.add(order)
            return

        raise TypeError("Tipo de ordem desconhecido")

    def on_tick(self, ticker: str) -> None:
        """
        Chamado a cada novo candle.
        Executa LIMITs quando o candle atinge o preço
        """
        candles = self.market_data.get_recent(ticker)
        if not candles:
            return

        candle = candles[-1]

        # BUY LIMIT → low <= price
        for order in list(self.order_book.buy_orders(ticker)):
            if candle.low <= order.price:
                self._execute_limit(order, order.price)

        # SELL LIMIT → high >= price
        for order in list(self.order_book.sell_orders(ticker)):
            if candle.high >= order.price:
                self._execute_limit(order, order.price)

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

        self.order_book.remove(order)
        order.status = OrderStatus.CANCELED
        order.remaining = 0
        return True

    # =========================
    # Execução
    # =========================

    def _execute_market(self, order: MarketOrder) -> None:
        """
        Executa ordem a mercado usando o último preço disponível.
        """
        candles = self.market_data.get_recent(order.ticker)
        if not candles:
            raise ValueError(f"Sem dados de mercado para {order.ticker}")

        self._execute_trade(order, candles[-1].price)

    def _execute_limit(self, order: LimitOrder, price: float) -> None:
        """
        Executa ordem limitada usando o preço do candle.
        """
        self._execute_trade(order, price)
        if order.remaining == 0:
            self.order_book.remove(order)

    def _execute_trade(self, order: Order, price: float) -> None:
        """
        Executa efetivamente a ordem via Broker.
        """
        qty = order.remaining if isinstance(order, LimitOrder) else order.size

        self.broker.execute_order(
            client_id=order.client_id,
            ticker=order.ticker,
            size=qty,
            price=price,
            action=order.action,
        )

        if isinstance(order, LimitOrder):
            order.remaining = 0

        order.status = OrderStatus.EXECUTED

    # =========================
    # Player x Player
    # =========================

    def _match_players(self, order: Order) -> None:
        if order.action == OrderAction.BUY:
            self._match_player_buy(order)
        else:
            self._match_player_sell(order)

    def _match_player_buy(self, buy: Order):
        for sell in list(self.order_book.sell_orders(buy.ticker)):
            if isinstance(buy, LimitOrder) and (
                buy.remaining == 0 or sell.price > buy.price
            ):
                break

            self._execute_player_trade(buy, sell, sell.price)

    def _match_player_sell(self, sell: Order):
        for buy in list(self.order_book.buy_orders(sell.ticker)):
            if isinstance(sell, LimitOrder) and (
                sell.remaining == 0 or buy.price < sell.price
            ):
                break

            self._execute_player_trade(buy, sell, buy.price)

    def _execute_player_trade(self, buy: Order, sell: Order, price: float):
        buy_qty = buy.remaining if isinstance(buy, LimitOrder) else buy.size
        sell_qty = sell.remaining if isinstance(sell, LimitOrder) else sell.size

        qty = min(buy_qty, sell_qty)

        self.broker.execute_order(
            client_id=buy.client_id,
            ticker=buy.ticker,
            size=qty,
            price=price,
            action=buy.action,
        )
        self.broker.execute_order(
            client_id=sell.client_id,
            ticker=sell.ticker,
            size=qty,
            price=price,
            action=sell.action,
        )

        if isinstance(buy, LimitOrder):
            buy.remaining -= qty
            buy.status = (
                OrderStatus.EXECUTED if buy.remaining == 0 else OrderStatus.PARTIAL
            )
            if buy.remaining == 0:
                self.order_book.remove(buy)

        if isinstance(sell, LimitOrder):
            sell.remaining -= qty
            sell.status = (
                OrderStatus.EXECUTED if sell.remaining == 0 else OrderStatus.PARTIAL
            )
            if sell.remaining == 0:
                self.order_book.remove(sell)
