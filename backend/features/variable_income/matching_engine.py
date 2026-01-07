from backend.core.dto.order import OrderDTO
from backend.core.exceptions.http_exceptions import (
    ForbiddenError,
    UnprocessableEntityError,
)
from backend.features.realtime import notify
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

    # =========================
    # API pública
    # =========================

    def submit(self, order: Order) -> None:
        """
        Recebe uma nova ordem:
        - Tenta casar contra players
        - MARKET: executa resto no mercado
        - LIMIT: saldo vai pro book
        """
        if order.status != OrderStatus.PENDING:
            raise UnprocessableEntityError("Ordem inválida")

        # Tenta casar contra outros players
        self._match_players(order)

        # Se ainda sobrou MarketOrder, executa contra mercado
        if isinstance(order, MarketOrder) and order.remaining > 0:
            self._execute_market(order)
            return

        # Se ainda sobrou LimitOrder, adiciona ao book
        if isinstance(order, LimitOrder) and order.remaining > 0:
            self.order_book.add(order)
            notify(
                event=f"order_added:{order.ticker}",
                payload={
                    "order": OrderDTO.from_model(order).to_json(),
                },
            )

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
        order = self.order_book.best_buy(ticker)
        while order and candle.low <= order.price:
            self._execute_limit(order, order.price)
            order = self.order_book.best_buy(ticker)

        # SELL LIMIT → high >= price
        order = self.order_book.best_sell(ticker)
        while order and candle.high >= order.price:
            self._execute_limit(order, order.price)
            order = self.order_book.best_sell(ticker)

    def cancel(self, *, order_id: str, client_id: str) -> bool:
        """
        Cancela uma ordem pendente ou parcialmente executada.
        """
        order = self.order_book.find(order_id)
        if not order:
            return False

        if order.client_id != client_id:
            raise ForbiddenError("Ordem não pertence ao cliente")

        if order.status not in (OrderStatus.PENDING, OrderStatus.PARTIAL):
            raise ForbiddenError("Ordem não pode ser cancelada")

        order.status = OrderStatus.CANCELED
        order.remaining = 0
        notify(
            event=f"order_updated:{order.ticker}",
            payload={
                "order": OrderDTO.from_model(order).to_json(),
            },
        )
        self.order_book.remove(order)
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
        try:
            self._execute_trade(order, price)
            if order.remaining == 0:
                self.order_book.remove(order)
        except ValueError:
            # TODO: #63 Tratar melhor os erros de _execute_trade
            order.status = OrderStatus.CANCELED
            self.order_book.remove(order)
            notify(
                event=f"order_updated:{order.ticker}",
                payload={
                    "order": OrderDTO.from_model(order).to_json(),
                },
            )

    def _execute_trade(self, order: Order, price: float) -> None:
        """
        Executa efetivamente a ordem via Broker.
        """
        qty = order.remaining

        self.broker.execute_order(
            client_id=order.client_id,
            ticker=order.ticker,
            size=qty,
            price=price,
            action=order.action,
        )

        order.remaining -= qty
        order.status = (
            OrderStatus.EXECUTED if order.remaining == 0 else OrderStatus.PARTIAL
        )

        self._notify_execution(order, price, qty)

    # =========================
    # Player x Player
    # =========================

    def _match_players(self, order: Order) -> None:
        if order.action == OrderAction.BUY:
            self._match_player_buy(order)
        else:
            self._match_player_sell(order)

    def _match_player_buy(self, buy: Order):
        """
        Match de BUY (Market ou Limit) contra ordens SELL do book.
        """
        while buy.remaining > 0:
            sell = self.order_book.best_sell(buy.ticker)
            if not sell:
                break

            # Para LimitOrder, checa se preço é compatível
            if isinstance(buy, LimitOrder) and sell.price > buy.price:
                break

            self._execute_player_trade(buy, sell, sell.price)

    def _match_player_sell(self, sell: Order):
        """
        Match de SELL (Market ou Limit) contra ordens BUY do book.
        """
        while sell.remaining > 0:
            buy = self.order_book.best_buy(sell.ticker)
            if not buy:
                break

            # Para LimitOrder, checa se preço é compatível
            if isinstance(sell, LimitOrder) and buy.price < sell.price:
                break

            self._execute_player_trade(buy, sell, buy.price)

    def _execute_player_trade(self, buy: Order, sell: Order, price: float):
        qty = min(buy.remaining, sell.remaining)

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

        buy.remaining -= qty
        sell.remaining -= qty

        buy.status = OrderStatus.EXECUTED if buy.remaining == 0 else OrderStatus.PARTIAL
        sell.status = (
            OrderStatus.EXECUTED if sell.remaining == 0 else OrderStatus.PARTIAL
        )

        self._notify_execution(buy, price, qty)
        self._notify_execution(sell, price, qty)

        if isinstance(buy, LimitOrder) and buy.remaining == 0:
            self.order_book.remove(buy)
        if isinstance(sell, LimitOrder) and sell.remaining == 0:
            self.order_book.remove(sell)

    # =========================
    # Notificações
    # =========================

    def _notify_execution(self, order: Order, price: float, quantity: int):
        if order.remaining == 0:
            notify(
                event="order_executed",
                payload={
                    "order_id": order.id,
                    "ticker": order.ticker,
                    "action": order.action.value,
                    "price": price,
                    "quantity": quantity,
                },
                to=order.client_id,
            )
        else:
            notify(
                event="order_partial_executed",
                payload={
                    "order_id": order.id,
                    "ticker": order.ticker,
                    "action": order.action.value,
                    "price": price,
                    "quantity": quantity,
                    "remaining": order.remaining,
                },
                to=order.client_id,
            )

        if isinstance(order, LimitOrder):
            notify(
                event=f"order_updated:{order.ticker}",
                payload={
                    "order": OrderDTO.from_model(order).to_json(),
                },
            )
