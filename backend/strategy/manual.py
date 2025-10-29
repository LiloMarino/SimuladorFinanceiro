import time

import backtrader as bt
from flask import current_app

from backend import logger_utils
from backend.realtime import get_broker, notify
from backend.realtime.ws_broker import SocketBroker
from backend.simulation import get_simulation

logger = logger_utils.setup_logger(__name__)


class ManualStrategy(bt.Strategy):
    def __init__(self):
        with current_app.app_context():
            self.simulation = get_simulation()
            logger.info("ManualStrategy iniciada.")

    def next(self):
        try:
            self.simulation.next_day()
            current_date = self.simulation.get_current_date_formatted()
            stocks = self.simulation.get_stocks()

            for stock in stocks:
                ticker = stock["ticker"]
                notify(f"stock_update:{ticker}", {"stock": stock})

            logger.info("Notificando clientes...")
            notify("simulation_update", {"currentDate": current_date})
            notify("stocks_update", {"stocks": stocks})

        except StopIteration:
            logger.info("Fim da simulação.")

        while speed == 0:
            speed = self.simulation.get_speed()

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

            # Delay não bloqueante
            self._non_blocking_sleep(speed)

    def _non_blocking_sleep(self, speed: float):
        delay = 1 / max(speed, 1)
        broker = get_broker()
        try:
            if isinstance(broker, SocketBroker):
                broker.socketio.sleep(delay)
            else:
                time.sleep(delay)
        except Exception as e:
            logger.debug(f"Erro no sleep: {e}")
            time.sleep(delay)
