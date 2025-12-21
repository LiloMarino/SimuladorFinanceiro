from datetime import datetime, timedelta

from backend.core import repository
from backend.core.dto.position import PositionDTO
from backend.core.dto.stock import StockDTO
from backend.core.dto.stock_details import StockDetailsDTO
from backend.core.dto.user import UserDTO
from backend.core.logger import setup_logger
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.user_manager import UserManager
from backend.features.realtime import notify
from backend.features.simulation.simulation_engine import SimulationEngine
from backend.features.strategy.manual import ManualStrategy

logger = setup_logger(__name__)


class Simulation:
    def __init__(self, start_date: datetime, end_date: datetime):
        self._speed = 0
        self._current_date = start_date - timedelta(days=1)
        self._end_date = end_date
        self._engine = SimulationEngine(self._current_date)
        self._engine.set_strategy(ManualStrategy)

        # Controle de snapshot
        self._last_snapshot_month: tuple[int, int] | None = None

        # Configura os alias
        self.get_cash = self._engine.get_cash
        self.get_fixed_assets = self._engine.fixed_income_market.get_available_assets
        self.get_portfolio = self._engine.get_portfolio

        # Roda o primeiro tick para a inicialização
        self.next_tick()

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

        # Persiste os eventos
        EventManager.flush()

        # Cria snapshot mensal
        if self._has_month_changed():
            users = repository.user.get_all_users()
            for user in users:
                snapshot = repository.snapshot.create_snapshot(
                    user_id=user.id,
                    current_date=self._current_date,
                )

                notify(
                    event="snapshot_update",
                    payload={"snapshot": snapshot.to_json()},
                    to=str(user.client_id),
                )

        # Emite notificações
        logger.info(f"Dia atual: {self.get_current_date_formatted()}")
        for stock in stocks:
            ticker = stock.ticker
            notify(f"stock_update:{ticker}", {"stock": stock.to_json()})
        notify("simulation_update", {"currentDate": self.get_current_date_formatted()})
        notify("stocks_update", {"stocks": [s.to_json() for s in stocks]})

    def get_current_date_formatted(self) -> str:
        return self._current_date.strftime("%d/%m/%Y")

    def create_user(self, client_id: str, nickname: str) -> UserDTO:
        return repository.user.create_user(client_id, nickname, self._current_date)

    def set_speed(self, speed: int):
        logger.info(f"Velocidade da simulação alterada para {speed}x")
        self._speed = speed

    def get_speed(self) -> int:
        return self._speed

    def get_stocks(self) -> list[StockDTO]:
        return repository.stock.get_stocks_by_date(self._current_date)

    def get_stock_details(self, ticker: str) -> StockDetailsDTO | None:
        return repository.stock.get_stock_details(ticker, self._current_date)

    def get_portfolio_ticker(self, client_id: str, ticker: str) -> PositionDTO:
        positions = self._engine.get_positions(client_id)
        position = positions.get(ticker)
        return (
            PositionDTO(
                ticker=ticker,
                size=position.size,
                total_cost=position.total_cost,
                avg_price=position.avg_price,
            )
            if position
            else PositionDTO(
                ticker=ticker,
                size=0,
                total_cost=0,
                avg_price=0,
            )
        )

    def get_fixed_asset(self, uuid: str) -> dict | None:
        asset = self._engine.fixed_income_market.get_asset(uuid)
        if asset:
            return asset.to_dict()
        return None

    def get_economic_indicators(self):
        return {
            "ipca": repository.economic.get_ipca_rate(self._current_date),
            "selic": repository.economic.get_selic_rate(self._current_date),
            "cdi": repository.economic.get_cdi_rate(self._current_date),
        }

    def _has_month_changed(self) -> bool:
        current_month = (self._current_date.year, self._current_date.month)

        if self._last_snapshot_month != current_month:
            self._last_snapshot_month = current_month
            return True

        return False
