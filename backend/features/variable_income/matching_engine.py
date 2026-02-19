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
    Engine de matching de ordens baseada exclusivamente em OrderBook.

    Responsável por:
    - Executar matching entre ordens de compra e venda do OrderBook
    - Aplicar regras de execução: MARKET consome tudo ou falha, LIMIT consome até limite
    - Coordenar com Broker para executar trades atomicamente
    - Gerenciar injeção de liquidez sintética baseada em candles
    - Processar submissão e cancelamento de ordens
    - Emitir notificações realtime de ações no OrderBook
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

        if isinstance(order, MarketOrder):
            executed = self._consume_book(order)
            if order.remaining > 0:
                if executed == 0:
                    raise ConflictError("Sem liquidez no mercado")
                raise ConflictError(
                    f"Ordem executada parcialmente: executado {executed} de {order.size}."
                )

        if isinstance(order, LimitOrder):
            # Reserva o cash/posição em LIMIT para evitar que seja gasto em outro trade antes de ser executado
            self.broker.reserve_limit_order(order)

            # LIMIT tenta consumir o book
            self._consume_book(order)

            # LIMIT que sobrou → entra no book
            if order.remaining > 0:
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

        self.market_liquidity.refresh(candle, self._process_market_order)

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

        if order.status != OrderStatus.PENDING:
            raise ForbiddenError("Ordem não pode ser cancelada")

        self.broker.release_limit_order(order)

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

    def _process_market_order(self, mo: LimitOrder) -> bool:
        """Callback usado por MarketLiquidity.refresh.

        Retorna True se a ordem foi adicionada ao book (resting), False caso
        contrário. Evita criar listas auxiliares no caller.
        """
        if mo.remaining <= 0:
            return False

        self._consume_book(mo)

        if mo.remaining > 0:
            self.order_book.add(mo)
            return True

        return False

    # =========================
    # Core matching
    # =========================

    def _consume_book(self, order: Order) -> int:
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

            self._execute_trade(order, counter, counter.price)
        return order.size - order.remaining

    def _execute_trade(self, taker: Order, maker: LimitOrder, price: float):
        """
        Executa trade atomicamente entre taker (ordem ativa) e maker (ordem do book).
        Se falhar, maker é removido do book e notificado com rejeição.
        """
        qty = min(taker.remaining, maker.remaining)

        self.broker.execute_trade(
            taker_order=taker,
            maker_order=maker,
            size=qty,
            price=price,
        )

        # Trade bem-sucedido atualiza estados e notifica
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
