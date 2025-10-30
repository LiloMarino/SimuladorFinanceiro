from __future__ import annotations

import threading
from typing import TYPE_CHECKING

import backtrader as bt

from backend import logger_utils

if TYPE_CHECKING:
    from backend.simulation.simulation import Simulation

logger = logger_utils.setup_logger(__name__)


class ManualStrategy(bt.Strategy):
    _orders_lock = threading.Lock()
    _orders: list[tuple[str, str, int]] = []

    @classmethod
    def queue_order(cls, action: str, ticker: str, quantity: int):
        """Enfileira uma nova ordem estática (chamada via API)."""
        with cls._orders_lock:
            cls._orders.append((action, ticker, quantity))
        logger.info(f"[ManualStrategy] Ordem recebida: {action} {quantity}x {ticker}")

    @classmethod
    def pop_orders(cls) -> list[tuple[str, str, int]]:
        """Retorna e limpa todas as ordens pendentes."""
        with cls._orders_lock:
            orders = cls._orders[:]
            cls._orders.clear()
        return orders

    def __init__(self):
        logger.info("ManualStrategy iniciada.")

    def next(self):
        """Executa ordens externas pendentes (vindas via API)."""
        for action, ticker, size in self.pop_orders():
            data = self.getdatabyname(ticker)
            if not data:
                logger.warning(f"Tentou operar ticker desconhecido: {ticker}")
                continue

            if action == "buy":
                logger.info(f"Executando BUY de {size}x {ticker}")
                self.buy(data=data, size=size)
            elif action == "sell":
                logger.info(f"Executando SELL de {size}x {ticker}")
                self.sell(data=data, size=size)
