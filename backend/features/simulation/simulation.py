from datetime import datetime, timedelta

from backend.core import repository
from backend.core.dto.stock_details import StockDetailsDTO
from backend.core.logger import setup_logger
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
        stocks = repository.stock.get_stocks_by_date(self._current_date)
        self._engine.update_market_data(stocks)

        # Executa a estratégia
        self._engine.next(self._current_date)

        logger.info(f"Dia atual: {self.get_current_date_formatted()}")

        # Emite notificações
        for stock in stocks:
            ticker = stock.ticker
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
        return repository.stock.get_stocks_by_date(self._current_date)

    def get_stock_details(self, ticker: str) -> StockDetailsDTO | None:
        return repository.stock.get_stock_details(ticker, self._current_date)

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
            "ipca": repository.economic.get_ipca_rate(self._current_date),
            "selic": repository.economic.get_selic_rate(self._current_date),
            "cdi": repository.economic.get_cdi_rate(self._current_date),
        }
