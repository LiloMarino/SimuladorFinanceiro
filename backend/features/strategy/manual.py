import threading

from backend.features.strategy.base_strategy import BaseStrategy
from backend.shared.utils.logger import setup_logger

logger = setup_logger(__name__)


class ManualStrategy(BaseStrategy):
    _orders_lock = threading.Lock()
    _orders: list[tuple[str, str, int]] = []  # (ação, ticker, quantidade)

    @classmethod
    def queue_order(cls, action: str, ticker: str, size: int):
        with cls._orders_lock:
            cls._orders.append((action, ticker, size))
        logger.info(f"Ordem recebida: {action.upper()} {size}x {ticker} (a mercado)")

    @classmethod
    def pop_orders(cls):
        with cls._orders_lock:
            orders = cls._orders[:]
            cls._orders.clear()
        return orders

    def next(self):
        for action, ticker, size in self.pop_orders():
            try:
                if action == "buy":
                    self.broker.buy(ticker, size)
                elif action == "sell":
                    self.broker.sell(ticker, size)
                else:
                    logger.warning(f"Ação inválida: {action}")
            except Exception as e:
                logger.error(f"Erro executando ordem {action} {ticker}: {e}")
