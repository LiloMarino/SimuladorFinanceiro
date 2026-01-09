from backend.core.dto.order import OrderDTO
from backend.core.exceptions.http_exceptions import (
    ConflictError,
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
from backend.features.variable_income.market_liquidity import MarketLiquidity
from backend.features.variable_income.order_book import OrderBook


class MatchingEngine:
    """
    Engine de matching baseada exclusivamente em OrderBook.

    Regras:
    - TODA ordem tenta consumir o book
    - MARKET → consome tudo ou falha
    - LIMIT → consome até o limite, resto entra no book
    - Candle NÃO executa ordens, apenas injeta liquidez
    """

    def __init__(self, broker: Broker):
        self.broker = broker
        self.market_data = MarketData()
        self.order_book = OrderBook()
        self.market_liquidity = MarketLiquidity(order_book=self.order_book)

    # =========================
    # API pública
    # =========================

    def submit(self, order: Order) -> None:
        if order.status != OrderStatus.PENDING:
            raise UnprocessableEntityError("Ordem inválida")

        # Toda ordem tenta consumir o book
        self._consume_book(order)

        # MARKET que sobrou → erro
        if isinstance(order, MarketOrder) and order.remaining > 0:
            raise ConflictError("Sem liquidez no mercado")

        # LIMIT que sobrou → entra no book
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
        Candle injeta liquidez sintética no book.
        """
        candle = self.market_data.get_last(ticker)
        if not candle:
            return

        self.market_liquidity.refresh(candle)
        notify(
            event=f"order_book_snapshot:{candle.ticker}",
            payload={
                "orders": [
                    OrderDTO.from_model(o).to_json()
                    for o in self.order_book.get_orders(candle.ticker)
                ]
            },
        )

    def cancel(self, *, order_id: str, client_id: str) -> bool:
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
    # Core matching
    # =========================

    def _consume_book(self, order: Order) -> None:
        """
        Consome o book respeitando:
        - preço (se LIMIT)
        - melhor preço disponível
        - price-time priority
        """
        while order.remaining > 0:
            counter = (
                self.order_book.best_sell(order.ticker)
                if order.action == OrderAction.BUY
                else self.order_book.best_buy(order.ticker)
            )

            if not counter:
                break

            # LIMIT → checa compatibilidade de preço
            if isinstance(order, LimitOrder):
                if order.action == OrderAction.BUY and counter.price > order.price:
                    break
                if order.action == OrderAction.SELL and counter.price < order.price:
                    break

            self._execute_trade(
                order, counter, counter.price
            )  # TODO: #63 Tratar melhor os erros de _execute_trade

    def _execute_trade(self, taker: Order, maker: LimitOrder, price: float):
        """
        Executa trade entre taker (ordem ativa) e maker (ordem do book).
        """
        qty = min(taker.remaining, maker.remaining)

        self.broker.execute_order(
            client_id=taker.client_id,
            ticker=taker.ticker,
            size=qty,
            price=price,
            action=taker.action,
        )
        if maker.client_id != MarketLiquidity.MARKET_CLIENT_ID:
            self.broker.execute_order(
                client_id=maker.client_id,
                ticker=maker.ticker,
                size=qty,
                price=price,
                action=maker.action,
            )

        taker.remaining -= qty
        maker.remaining -= qty

        taker.status = (
            OrderStatus.EXECUTED if taker.remaining == 0 else OrderStatus.PARTIAL
        )
        maker.status = (
            OrderStatus.EXECUTED if maker.remaining == 0 else OrderStatus.PARTIAL
        )

        self._notify_execution(taker, price, qty)
        self._notify_execution(maker, price, qty)

        if maker.remaining == 0:
            self.order_book.remove(maker)

    # =========================
    # Notificações
    # =========================

    def _notify_execution(self, order: Order, price: float, quantity: int):
        event = "order_executed" if order.remaining == 0 else "order_partial_executed"

        payload = {
            "order_id": order.id,
            "ticker": order.ticker,
            "action": order.action.value,
            "price": price,
            "quantity": quantity,
        }

        if order.remaining > 0:
            payload["remaining"] = order.remaining

        if order.client_id != MarketLiquidity.MARKET_CLIENT_ID:
            notify(event=event, payload=payload, to=order.client_id)

        if isinstance(order, LimitOrder):
            notify(
                event=f"order_updated:{order.ticker}",
                payload={
                    "order": OrderDTO.from_model(order).to_json(),
                },
            )
