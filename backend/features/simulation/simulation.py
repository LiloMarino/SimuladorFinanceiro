from datetime import datetime, timedelta

from backend.core.logger import setup_logger
from backend.core.utils.data_provider import (
    get_cdi_rate,
    get_ipca_rate,
    get_selic_rate,
    get_stock_details,
    get_stocks,
)
from backend.features.realtime import notify
from backend.features.simulation.entities.fixed_income_asset import FixedIncomeAsset
from backend.features.simulation.entities.portfolio import Portfolio
from backend.features.simulation.entities.position import Position
from backend.features.simulation.simulation_engine import SimulationEngine
from backend.features.strategy.manual import ManualStrategy

logger = setup_logger(__name__)


class Simulation:
    def __init__(self, start_date: datetime, end_date: datetime):
        self._speed = 0
        self._current_date = start_date
        self._end_date = end_date
        self._engine = SimulationEngine()
        self._engine.set_strategy(ManualStrategy)

    def next_tick(self):
        # Verifica se a simulação terminou
        if self._current_date > self._end_date:
            logger.info("Fim da simulação")
            raise StopIteration()

        # Avança para o próximo dia útil
        self._current_date += timedelta(days=1)
        while self._current_date.weekday() >= 5:
            self._current_date += timedelta(days=1)
        if self._current_date > self._end_date:
            logger.info("Fim da simulação")
            raise StopIteration()

        # Obtém os dados do dia atual e atualiza o buffer
        stocks = get_stocks(self._current_date)
        self._engine.update_market_data(stocks)

        # Executa a estratégia
        self._engine.next(self._current_date)

        logger.info(f"Dia atual: {self.get_current_date_formatted()}")

        # Emite notificações
        for stock in stocks:
            ticker = stock["ticker"]
            notify(f"stock_update:{ticker}", {"stock": stock})

        notify("simulation_update", {"currentDate": self.get_current_date_formatted()})
        notify("stocks_update", {"stocks": stocks})

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

    def get_portfolio(self) -> Portfolio:
        return self._engine.get_portfolio()

    def get_portfolio_ticker(self, ticker: str) -> Position:
        positions = self._engine.get_positions()
        return positions.get(ticker, Position(ticker))

    def get_fixed_asset(self, uuid: str) -> dict | None:
        asset = self._engine.get_fixed_income_market().get_asset(uuid)
        if asset:
            return asset.to_dict()
        return None

    def get_fixed_assets(self) -> list[FixedIncomeAsset]:
        return self._engine.get_fixed_income_market().get_available_assets()

    def get_cash(self) -> float:
        return self._engine.get_cash()

    def get_economic_indicators(self):
        return {
            "ipca": get_ipca_rate(),
            "selic": get_selic_rate(),
            "cdi": get_cdi_rate(),
        }
