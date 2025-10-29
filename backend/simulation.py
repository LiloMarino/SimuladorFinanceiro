import threading
from datetime import datetime, timedelta

import backtrader as bt
from flask import current_app

from backend import logger_utils
from backend.data_provider import (
    get_all_tickers,
    get_feed,
    get_stock_details,
    get_stocks,
)
from backend.strategy.manual import ManualStrategy

logger = logger_utils.setup_logger(__name__)


class Simulation:
    def __init__(self, start_date: datetime, end_date: datetime):
        self.__speed = 0
        self.__current_date = start_date
        self.__end_date = end_date
        self._orders: list[tuple[str, str, int]] = []  # (action, ticker, quantity)
        self._thread: threading.Thread | None = None

        # Configura o Cerebro
        self.cerebro = bt.Cerebro()
        tickers = get_all_tickers()
        for ticker in tickers:
            feed = get_feed(ticker, start_date, end_date)
            self.cerebro.adddata(feed, name=ticker)

        self.cerebro.broker.setcash(10000)
        self.cerebro.addstrategy(ManualStrategy)

    def next_day(self):
        if self.__current_date < self.__end_date:
            self.__current_date += timedelta(days=1)
            logger.info(f"Avançando para o dia {self.get_current_date_formatted()}")
        else:
            logger.info("Fim da simulação")
            raise StopIteration("Fim da simulação")

    def get_current_date_formatted(self) -> str:
        return self.__current_date.strftime("%d/%m/%Y")

    def set_speed(self, speed: int):
        logger.info(f"Velocidade da simulação alterada para {speed}x")
        self.__speed = speed

    def get_speed(self) -> int:
        return self.__speed

    def get_stocks(self) -> list:
        return get_stocks(self.__current_date)

    def get_stock_details(self, ticker: str) -> dict | None:
        return get_stock_details(ticker, self.__current_date)

    def queue_order(self, action: str, ticker: str, quantity: int):
        logger.info(f"Ordem enfileirada: {action} {quantity}x {ticker}")
        self._orders.append((action, ticker, quantity))

    def pop_orders(self) -> list[tuple[str, str, int]]:
        orders = self._orders[:]
        self._orders.clear()
        return orders

    def start(self):
        self._thread = threading.Thread(target=self.run, daemon=True)
        self._thread.start()
        logger.info("Thread da simulação iniciada.")

    def run(self):
        self.cerebro.run()


def get_simulation() -> Simulation:
    if "simulation" not in current_app.config:
        from_date = datetime(2023, 1, 1)
        to_date = datetime(2026, 8, 18)
        current_app.config["simulation"] = Simulation(from_date, to_date)
    return current_app.config["simulation"]
