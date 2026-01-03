import threading
from typing import ClassVar

from backend.core.logger import setup_logger
from backend.features.strategy.base_strategy import BaseStrategy
from backend.features.variable_income.entities.order import (
    MarketOrder,
    OrderAction,
)

logger = setup_logger(__name__)


class ManualStrategy(BaseStrategy):
    _orders_lock = threading.Lock()
    _orders: ClassVar[list[MarketOrder]] = []

    @classmethod
    def queue_order(cls, client_id: str, action: OrderAction, ticker: str, size: int):
        with cls._orders_lock:
            cls._orders.append(
                MarketOrder(
                    client_id=client_id,
                    action=action,
                    ticker=ticker,
                    size=size,
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
            self.matching_engine.submit(order)
