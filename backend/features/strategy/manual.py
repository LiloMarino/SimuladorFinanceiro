import threading
from typing import ClassVar

from backend.core.logger import setup_logger
from backend.features.strategy.base_strategy import BaseStrategy
from backend.features.variable_income.entities.order import (
    Order,
    OrderAction,
    OrderType,
)

logger = setup_logger(__name__)


class ManualStrategy(BaseStrategy):
    _orders_lock = threading.Lock()
    _orders: ClassVar[list[Order]] = []

    @classmethod
    def queue_order(cls, client_id: str, action: OrderAction, ticker: str, size: int):
        with cls._orders_lock:
            cls._orders.append(
                Order(
                    client_id=client_id,
                    action=action,
                    ticker=ticker,
                    size=size,
                    order_type=OrderType.MARKET,
                )
            )
        logger.info(f"Ordem recebida: {action.name} {size}x {ticker} (a mercado)")

    @classmethod
    def pop_orders(cls):
        with cls._orders_lock:
            orders = cls._orders[:]
            cls._orders.clear()
        return orders

    def next(self):
        for order in self.pop_orders():
            try:
                match order.action:
                    case OrderAction.BUY:
                        self.broker.buy(order.client_id, order.ticker, order.size)
                    case OrderAction.SELL:
                        self.broker.sell(order.client_id, order.ticker, order.size)
            except Exception:
                logger.exception(f"Erro executando ordem: {order}")
