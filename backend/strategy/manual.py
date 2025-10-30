from __future__ import annotations

import time
from typing import TYPE_CHECKING

import backtrader as bt

from backend import logger_utils
from backend.realtime import get_broker, notify
from backend.realtime.ws_broker import SocketBroker

if TYPE_CHECKING:
    from backend.simulation.simulation import Simulation

logger = logger_utils.setup_logger(__name__)


class ManualStrategy(bt.Strategy):
    def __init__(self, simulation: Simulation):
        self.simulation = simulation
        logger.info("ManualStrategy iniciada.")

    def next(self):
        # Executa ordens externas pendentes
        for action, ticker, size in self.simulation.pop_orders():
            data = self.getdatabyname(ticker)
            if data:
                if action == "buy":
                    logger.info(f"Executando BUY de {size}x {ticker}")
                    self.buy(data=data, size=size)
                elif action == "sell":
                    logger.info(f"Executando SELL de {size}x {ticker}")
                    self.sell(data=data, size=size)
            else:
                logger.warning(f"Tentou operar ticker desconhecido: {ticker}")
