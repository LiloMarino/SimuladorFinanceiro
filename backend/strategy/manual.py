import threading

from backend import logger_utils
from backend.strategy.base_strategy import BaseStrategy

logger = logger_utils.setup_logger(__name__)


class ManualStrategy(BaseStrategy):
    _orders_lock = threading.Lock()
    _orders: list[tuple[str, str, int, float]] = []  # (ação, ticker, quantidade, preço)

    @classmethod
    def queue_order(cls, action: str, ticker: str, size: int, price: float):
        with cls._orders_lock:
            cls._orders.append((action, ticker, size, price))
        logger.info(f"Ordem recebida: {action.upper()} {size}x {ticker} @ {price}")

    @classmethod
    def pop_orders(cls):
        with cls._orders_lock:
            orders = cls._orders[:]
            cls._orders.clear()
        return orders

    def next(self):
        for action, ticker, size, price in self.pop_orders():
            try:
                if action == "buy":
                    self.broker.buy(ticker, price, size)
                elif action == "sell":
                    self.broker.sell(ticker, price, size)
                else:
                    logger.warning(f"Ação inválida: {action}")
            except Exception as e:
                logger.error(f"Erro executando ordem {action} {ticker}: {e}")
