from datetime import datetime, timedelta

from backend import logger_utils
from backend.data_provider import get_stock_details, get_stocks
from backend.simulation.simulation_engine import SimulationEngine
from backend.strategy.manual import ManualStrategy

logger = logger_utils.setup_logger(__name__)


class Simulation:
    def __init__(self, start_date: datetime, end_date: datetime):
        self._speed = 0
        self._current_date = start_date
        self._end_date = end_date
        self._engine = SimulationEngine()
        self._engine.set_strategy(ManualStrategy)

    def next_tick(self) -> list[dict]:
        if self._current_date >= self._end_date:
            logger.info("Fim da simulação")
            raise StopIteration()

        # Obtém os dados do dia atual e atualiza o buffer
        stocks = get_stocks(self._current_date)
        self._engine.update_market_data(stocks)

        # Executa a estratégia
        self._engine.next()

        logger.info(f"Avançando para {self.get_current_date_formatted()}")
        self._current_date += timedelta(days=1)

        return stocks

    def get_current_date_formatted(self) -> str:
        return self._current_date.strftime("%d/%m/%Y")

    def set_speed(self, speed: int):
        logger.info(f"Velocidade da simulação alterada para {speed}x")
        self._speed = speed

    def get_speed(self) -> int:
        return self._speed

    def get_stocks(self) -> list:
        return get_stocks(self._current_date)

    def get_stock_details(self, ticker: str) -> dict | None:
        return get_stock_details(ticker, self._current_date)

    def get_portfolio(self) -> list[dict]:
        positions = self._engine.get_positions()
        portfolio = []
        for ticker, pos in positions.items():
            portfolio.append(
                {
                    "ticker": pos.ticker,
                    "size": pos.size,
                    "avg_price": pos.avg_price,
                }
            )
        return portfolio

    def get_cash(self) -> float:
        return self._engine.get_cash()
