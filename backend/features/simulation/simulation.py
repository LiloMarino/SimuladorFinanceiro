import logging
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from backend.core import repository
from backend.core.dto.candle import CandleDTO
from backend.core.dto.economic_indicators import EconomicIndicatorsDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.dto.fixed_income_projection import FixedIncomeProjectionDTO
from backend.core.dto.order import OrderDTO
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.player_history import PerformanceReportDTO
from backend.core.dto.position import PositionDTO
from backend.core.dto.simulation import SimulationDTO
from backend.core.dto.stock_details import StockDetailsDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import IndicatorSeries
from backend.core.indicators import annual_index_rate
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.user_manager import UserManager
from backend.core.utils import next_business_day
from backend.features.fixed_income.accrual import project
from backend.features.realtime import notify
from backend.features.realtime.schemas import (
    PortfolioUpdateEventDTO,
    SimulationTickUpdateEventDTO,
    SnapshotUpdateEventDTO,
    StatisticsSnapshotEntryDTO,
    StatisticsSnapshotUpdateEventDTO,
    StocksUpdateEventDTO,
    StockUpdateEventDTO,
)
from backend.features.simulation.simulation_engine import SimulationEngine
from backend.features.statistics.ranking import build_performance_report
from backend.features.strategy.manual import ManualStrategy
from backend.features.variable_income.price_impact import PriceImpact

logger = logging.getLogger(__name__)


class Simulation:
    """
    Orquestrador principal da simulação financeira.

    Responsável por:
    - Avançar simulação dia-a-dia (next_tick), pulando finais de semana
    - Aplicar contribuições mensais e registrar eventos mensais
    - Debitar o IR da renda variável no vencimento do DARF
    - Criar snapshots diários do portfólio de todos os players
    - Fornecer interface de alto nível para operações (criar/cancelar ordens, consultar portfólio)
    - Gerenciar velocidade da simulação e notificar atualizações realtime
    - Limpar caches de usuários ao fazer logout
    """

    def __init__(self, settings: SimulationDTO, resume_from: date | None = None):
        """
        `resume_from` é o último dia já processado de uma simulação retomada; o
        primeiro tick é o dia útil seguinte. Sem ele, o primeiro tick é o `start_date`.
        """
        self._speed = 0
        self.settings = settings
        self._current_date = resume_from or self.settings.start_date - timedelta(days=1)
        self._engine = SimulationEngine(
            self._current_date,
            settings.starting_cash,
            settings.id,
        )
        self._engine.set_strategy(ManualStrategy)
        self._price_impact = PriceImpact(
            settings.id,
            settings.price_impact_enabled,
            settings.price_impact_k,
            settings.price_impact_decay_days,
        )

        # O mês do último dia processado já recebeu o aporte
        self._last_contribution_month: tuple[int, int] | None = (
            (resume_from.year, resume_from.month) if resume_from else None
        )

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

    def add_cash(self, client_id: UUID, cash: Decimal) -> None:
        self._engine.add_cash(client_id, cash)

    def buy_fixed_income(
        self, client_id: UUID, asset: FixedIncomeAssetDTO, value: Decimal
    ) -> None:
        self._engine.fixed_broker.buy(client_id, asset, value)

    def project_fixed_income(
        self, asset: FixedIncomeAssetDTO, amount: Decimal
    ) -> FixedIncomeProjectionDTO:
        return project(asset, amount, self._current_date)

    def get_patrimonial_history(self, client_id: UUID) -> list[PatrimonialHistoryDTO]:
        return repository.portfolio.get_patrimonial_history(
            UserManager.get_user_id(client_id)
        )

    def next_tick(self):
        # Verifica se a simulação terminou
        if self._current_date > self.settings.end_date:
            logger.info("Fim da simulação")
            raise StopIteration()

        # Avança para o próximo dia útil
        self._current_date = next_business_day(self._current_date)
        if self._current_date > self.settings.end_date:
            logger.info("Fim da simulação")
            raise StopIteration()

        # O impacto é lido dos eventos no banco: o flush leva antes as ordens que
        # chegaram por HTTP depois do último tick, ainda datadas do dia anterior
        EventManager.flush()
        self._price_impact.refresh(self._current_date)

        # Obtém os dados do dia atual e atualiza o buffer
        stocks = self.get_stocks()
        self._engine.update_market_data(stocks)

        # Executa a estratégia
        self._engine.next(self._current_date)

        users = repository.user.get_all_users()
        month_changed = self._has_month_changed()

        # O aporte do mês e o DARF que vence hoje entram nos eventos antes do flush,
        # para o snapshot do dia já contá-los
        if month_changed:
            self._apply_monthly_contributions(users)
        self._collect_income_tax(users)
        EventManager.flush()

        self._create_daily_snapshots(users, month_changed)

        # Emite notificações
        logger.info(f"Dia atual: {self.get_current_date_formatted()}")
        for stock in stocks:
            ticker = stock.ticker
            notify(
                f"stock_update:{ticker}",
                StockUpdateEventDTO(stock=stock).to_json(),
            )
        notify(
            "simulation_update",
            SimulationTickUpdateEventDTO(
                current_date=self.get_current_date_formatted()
            ).to_json(),
        )
        notify("stocks_update", StocksUpdateEventDTO(stocks=stocks).to_json())
        for player in UserManager.list_active_players():
            notify(
                "portfolio_update",
                PortfolioUpdateEventDTO(
                    portfolio=self.get_portfolio(player.client_id)
                ).to_json(),
                to=player.client_id,
            )

    def get_current_date(self) -> date:
        return self._current_date

    def get_current_date_formatted(self) -> str:
        return self._current_date.strftime("%d/%m/%Y")

    def set_speed(self, speed: int):
        logger.info(f"Velocidade da simulação alterada para {speed}x")
        self._speed = speed

    def get_speed(self) -> int:
        return self._speed

    def get_stocks(self) -> list[CandleDTO]:
        return [
            self._price_impact.apply(stock)
            for stock in repository.stock.get_stocks_by_date(self._current_date)
        ]

    def get_stock_details(self, ticker: str) -> StockDetailsDTO | None:
        details = repository.stock.get_stock_details(ticker, self._current_date)
        if details is None:
            return None
        return self._price_impact.apply(details).model_copy(
            update={
                "history": self._price_impact.apply_history(ticker, details.history)
            }
        )

    def get_portfolio_ticker(self, client_id: UUID, ticker: str) -> PositionDTO:
        positions = self._engine.get_positions(client_id)
        position = positions.get(ticker)
        return (
            PositionDTO.from_model(position, self._engine.get_current_price(position))
            if position
            else PositionDTO(
                ticker=ticker,
                size=0,
                reserved=0,
                total_cost=Decimal(0),
                avg_price=Decimal(0),
                current_price=Decimal(0),
                current_value=Decimal(0),
                return_value=Decimal(0),
                return_pct=Decimal(0),
            )
        )

    def get_economic_indicators(self) -> EconomicIndicatorsDTO:
        return EconomicIndicatorsDTO(
            ipca=annual_index_rate(IndicatorSeries.IPCA, self._current_date),
            selic=annual_index_rate(IndicatorSeries.SELIC, self._current_date),
            cdi=annual_index_rate(IndicatorSeries.CDI, self._current_date),
        )

    def get_statistics(self) -> PerformanceReportDTO:
        return build_performance_report(
            repository.statistics.get_players_history([self.settings.id])
        )

    def get_orders(self, ticker: str) -> list[OrderDTO]:
        orders = self._engine.matching_engine.order_book.get_orders(ticker)
        return [OrderDTO.from_model(o) for o in orders]

    def clear_user_cache(self, client_id: UUID) -> None:
        # Remove saldo em cache
        self._engine._cash.pop(client_id, None)
        # Remove posições de renda variável em cache
        self._engine.broker._positions.pop(client_id, None)
        # Remove ativos de renda fixa em cache
        self._engine.fixed_broker._assets.pop(client_id, None)

    def _has_month_changed(self) -> bool:
        current_month = (self._current_date.year, self._current_date.month)

        if self._last_contribution_month != current_month:
            self._last_contribution_month = current_month
            return True

        return False

    def _apply_monthly_contributions(self, users: list[UserDTO]):
        if self.settings.monthly_contribution <= 0:
            return

        for user in users:
            self._engine.add_contribution(
                user.client_id, self.settings.monthly_contribution
            )

    def _collect_income_tax(self, users: list[UserDTO]):
        """
        O DARF do mês anterior vence no último dia útil do mês. O evento TAX fica
        datado do vencimento e a retomada começa no dia seguinte ao último evento,
        então cada DARF sai do caixa uma vez só.
        """
        if next_business_day(self._current_date).month == self._current_date.month:
            return

        for user in users:
            months = self._engine.assess_income_tax(user.id)
            darf = next(
                (m.darf_amount for m in months if m.due_date == self._current_date),
                None,
            )
            if darf:
                self._engine.pay_income_tax(user.client_id, darf)

    def _create_daily_snapshots(self, users: list[UserDTO], month_changed: bool):
        """
        `statistics_snapshot_update` faz a tela de Estatísticas buscar o histórico
        inteiro de novo, então sai só na virada do mês; `snapshot_update` é um merge
        por data no cache da Carteira e sai todo dia.
        """
        snapshots_payload = []

        for user in users:
            portfolio = self.get_portfolio(user.client_id)
            snapshot = repository.snapshot.create_snapshot(
                user_id=user.id,
                snapshot_date=self._current_date,
                total_equity=portfolio.variable_income_value,
                total_fixed=portfolio.fixed_income_value,
            )

            # Portfolio (individual)
            notify(
                event="snapshot_update",
                payload=SnapshotUpdateEventDTO(snapshot=snapshot).to_json(),
                to=user.client_id,
            )

            # Statistics (global)
            snapshots_payload.append(
                StatisticsSnapshotEntryDTO(
                    player_nickname=user.nickname,
                    snapshot=snapshot,
                )
            )

        if not month_changed:
            return

        notify(
            event="statistics_snapshot_update",
            payload=StatisticsSnapshotUpdateEventDTO(
                snapshots=snapshots_payload
            ).to_json(),
        )
