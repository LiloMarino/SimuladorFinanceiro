from datetime import timedelta
from decimal import Decimal

from backend.core import repository
from backend.core.dto.candle import CandleDTO
from backend.core.dto.order import OrderDTO
from backend.core.dto.player_history import PlayerHistoryDTO
from backend.core.dto.position import PositionDTO
from backend.core.dto.simulation import SimulationDTO
from backend.core.dto.stock_details import StockDetailsDTO
from backend.core.dto.user import UserDTO
from backend.core.logger import setup_logger
from backend.core.runtime.event_manager import EventManager
from backend.features.realtime import notify
from backend.features.simulation.simulation_engine import SimulationEngine
from backend.features.strategy.manual import ManualStrategy

logger = setup_logger(__name__)


class Simulation:
    def __init__(self, simulation_data: SimulationDTO):
        self._speed = 0
        self.simulation_data = simulation_data
        self._current_date = self.simulation_data.start_date - timedelta(days=1)
        self._engine = SimulationEngine(self._current_date)
        self._engine.set_strategy(ManualStrategy)

        # Controle de snapshot
        self._last_snapshot_month: tuple[int, int] | None = None

        # Configura os alias
        self.get_cash = self._engine.get_cash
        self.get_fixed_assets = self._engine.fixed_income_market.get_available_assets
        self.get_fixed_asset = self._engine.fixed_income_market.get_asset
        self.get_fixed_positions = self._engine.fixed_broker.get_fixed_positions
        self.get_portfolio = self._engine.get_portfolio
        self.create_order = self._engine.matching_engine.submit
        self.cancel_order = self._engine.matching_engine.cancel

        # Roda o primeiro tick para a inicialização
        self.next_tick()

    def next_tick(self):
        # Verifica se a simulação terminou
        if self._current_date > self.simulation_data.end_date:
            logger.info("Fim da simulação")
            raise StopIteration()

        # Avança para o próximo dia útil
        self._current_date += timedelta(days=1)
        while self._current_date.weekday() >= 5:
            self._current_date += timedelta(days=1)
        if self._current_date > self.simulation_data.end_date:
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
            snapshots_payload = []
            users = repository.user.get_all_users()
            for user in users:
                # Obtém as posições de renda fixa antes do snapshot
                client_id = str(user.client_id)

                fixed_positions = self.get_fixed_positions(client_id)

                for position in fixed_positions.values():
                    asset_id = repository.fixed_income.get_or_create_asset(
                        position.asset
                    )
                    repository.fixed_income.upsert_position(
                        user_id=user.id,
                        asset_id=asset_id,
                        total_applied=Decimal(position.total_applied),
                        current_value=Decimal(position.current_value),
                        accrual_date=self._current_date,
                    )

                # Cria o snapshot
                snapshot = repository.snapshot.create_snapshot(
                    user_id=user.id,
                    snapshot_date=self._current_date,
                )

                # Portfolio (individual)
                notify(
                    event="snapshot_update",
                    payload={"snapshot": snapshot.to_json()},
                    to=client_id,
                )

                # Statistics (global)
                snapshots_payload.append(
                    {
                        "player_nickname": user.nickname,
                        "snapshot": snapshot.to_json(),
                    }
                )

            notify(
                event="statistics_snapshot_update",
                payload={"snapshots": snapshots_payload},
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

    def get_stocks(self) -> list[CandleDTO]:
        return repository.stock.get_stocks_by_date(self._current_date)

    def get_stock_details(self, ticker: str) -> StockDetailsDTO | None:
        return repository.stock.get_stock_details(ticker, self._current_date)

    def get_portfolio_ticker(self, client_id: str, ticker: str) -> PositionDTO:
        positions = self._engine.get_positions(client_id)
        position = positions.get(ticker)
        return (
            PositionDTO.from_model(position)
            if position
            else PositionDTO(
                ticker=ticker,
                size=0,
                total_cost=0,
                avg_price=0,
            )
        )

    def get_economic_indicators(self):
        return {
            "ipca": repository.economic.get_ipca_rate(self._current_date),
            "selic": repository.economic.get_selic_rate(self._current_date),
            "cdi": repository.economic.get_cdi_rate(self._current_date),
        }

    def get_statistics(self) -> list[PlayerHistoryDTO]:
        return repository.statistics.get_players_history()

    def get_orders(self, ticker: str) -> list[OrderDTO]:
        orders = self._engine.matching_engine.order_book.get_orders(ticker)
        return [OrderDTO.from_model(o) for o in orders]

    def _has_month_changed(self) -> bool:
        current_month = (self._current_date.year, self._current_date.month)

        if self._last_snapshot_month != current_month:
            self._last_snapshot_month = current_month
            return True

        return False
