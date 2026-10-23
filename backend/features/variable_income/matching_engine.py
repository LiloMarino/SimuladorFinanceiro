import logging
from collections.abc import Callable
from uuid import UUID

from backend.core.enum import OrderAction, OrderStatus
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    ForbiddenError,
    UnprocessableEntityError,
)
from backend.features.realtime import notify
from backend.features.realtime.schemas import (
    OrderBookSnapshotEventDTO,
    OrderEventDTO,
    OrderExecutedEventDTO,
    OrderPartialExecutedEventDTO,
)
from backend.features.variable_income.broker import Broker, to_money
from backend.features.variable_income.entities.order import (
    MARKET_CLIENT_ID,
    LimitOrder,
    MarketOrder,
    Order,
)
from backend.features.variable_income.market_data import MarketData
from backend.features.variable_income.market_liquidity import MarketLiquidity
from backend.features.variable_income.order_book import OrderBook

logger = logging.getLogger(__name__)


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
        # Chamado quando uma ordem que descansava no book sai dele (executada por inteiro ou cancelada)
        self.on_order_closed: Callable[[Order], None] | None = None

    # =========================
    # API pública
    # =========================

    def submit(self, order: Order) -> None:
        if order.status != OrderStatus.PENDING:
            raise UnprocessableEntityError("Ordem inválida")

        if isinstance(order, MarketOrder):
            executed = self._consume_book(order)
            if order.remaining > 0 and executed == 0:
                raise ConflictError("Sem liquidez no mercado")

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
                    payload=OrderEventDTO(order=order.to_dto()).to_json(),
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
            payload=OrderBookSnapshotEventDTO(
                orders=[o.to_dto() for o in self.order_book.get_orders(candle.ticker)]
            ).to_json(),
        )

    def cancel(self, *, order_id: str, client_id: UUID) -> bool:
        order = self.order_book.find(order_id)
        if not order:
            return False

        if order.client_id != client_id:
            raise ForbiddenError("Ordem não pertence ao cliente")

        if order.status not in (OrderStatus.PENDING, OrderStatus.PARTIAL):
            raise ForbiddenError("Ordem não pode ser cancelada")

        self.broker.release_limit_order(order)

        order.status = OrderStatus.CANCELED
        order.remaining = 0
        notify(
            event=f"order_updated:{order.ticker}",
            payload=OrderEventDTO(order=order.to_dto()).to_json(),
        )
        self.order_book.remove(order)
        self._closed(order)
        return True

    def cancel_all(self, client_id: UUID | None = None) -> int:
        """Cancela as ordens abertas de um jogador, ou de todos quando `client_id` é None.

        A liquidez sintética do mercado fica de fora: ela não reserva caixa nem posição.
        """
        orders = (
            self.order_book.all_open()
            if client_id is None
            else self.order_book.orders_of(client_id)
        )
        canceled = 0
        for order in orders:
            if order.client_id == MARKET_CLIENT_ID:
                continue
            if self.cancel(order_id=order.id, client_id=order.client_id):
                canceled += 1
        return canceled

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
        logger.debug(
            "Ordem casada: %s %sx %s a R$ %s (taker %s, maker %s)",
            taker.action.value,
            qty,
            taker.ticker,
            price,
            taker.id,
            maker.id,
        )

        self.broker.execute_trade(
            taker_order=taker,
            maker_order=maker,
            size=qty,
            price=price,
        )

        # Trade bem-sucedido atualiza estados e notifica
        taker.remaining -= qty
        maker.remaining -= qty
        taker.notional += qty * price
        maker.notional += qty * price

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
            self._closed(maker)

    def _closed(self, order: Order) -> None:
        if self.on_order_closed is not None and order.automatic:
            self.on_order_closed(order)

    # =========================
    # Notificações
    # =========================

    def _notify_execution(self, order: Order, price: float, quantity: int):
        # O aviso da ordem de estratégia é o `strategy_orders`, que sai ao fim do dia
        if order.automatic:
            self._notify_book_update(order)
            return

        event = "order_executed" if order.remaining == 0 else "order_partial_executed"

        if order.remaining > 0:
            payload = OrderPartialExecutedEventDTO(
                order_id=order.id,
                ticker=order.ticker,
                action=order.action,
                price=to_money(price),
                quantity=quantity,
                remaining=order.remaining,
            ).to_json()
        else:
            payload = OrderExecutedEventDTO(
                order_id=order.id,
                ticker=order.ticker,
                action=order.action,
                price=to_money(price),
                quantity=quantity,
            ).to_json()

        if order.client_id != MARKET_CLIENT_ID:
            notify(event=event, payload=payload, to=order.client_id)

        self._notify_book_update(order)

    def _notify_book_update(self, order: Order):
        if isinstance(order, LimitOrder):
            notify(
                event=f"order_updated:{order.ticker}",
                payload=OrderEventDTO(order=order.to_dto()).to_json(),
            )
