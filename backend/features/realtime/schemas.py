"""
DTOs dos payloads emitidos via `notify(...)` (WebSocket).

Servem para dois propósitos:
1. Tipar os call sites de `notify(...)` em vez de dicts soltos.
2. Compor `RealtimeEventCatalog`, exposto via rota dev-only para que
   `openapi-typescript` gere `types/events.ts` a partir destes schemas.
"""

from datetime import date
from decimal import Decimal
from typing import Literal

from backend.core.dto.achievements import AchievementUnlockedEventDTO
from backend.core.dto.base import BaseDTO
from backend.core.dto.candle import CandleDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.dto.goal import GoalProgressDTO
from backend.core.dto.life import LifeEventDTO
from backend.core.dto.order import OrderDTO
from backend.core.dto.patrimonial_history import PortfolioHistoryPointDTO
from backend.core.dto.portfolio import PortfolioDTO
from backend.core.dto.position import PositionDTO
from backend.core.dto.simulation import SimulationSettingsDTO, SimulationStatusResponse
from backend.core.dto.snapshot import SnapshotDTO
from backend.features.variable_income.entities.order import OrderAction


class CashUpdateEventDTO(BaseDTO):
    cash: Decimal


class SpeedUpdateEventDTO(BaseDTO):
    speed: int


class SimulationTickUpdateEventDTO(BaseDTO):
    current_date: date


class PlayerPresenceEventDTO(BaseDTO):
    """Entrada, saída e troca de cor ou equipe de um jogador: a cor é a chave da paleta."""

    nickname: str
    color: str
    # Índice da equipe (1 a 10); nulo fora do modo em equipes ou enquanto não escolheu
    team: int | None = None


class SimulationSelectedEventDTO(BaseDTO):
    simulation_id: int | None


class SimulationDeletedEventDTO(BaseDTO):
    simulation_id: int


class SimulationEndedEventDTO(BaseDTO):
    reason: Literal["completed", "stopped_by_host"]
    simulation_id: int


class OrderExecutedEventDTO(BaseDTO):
    order_id: str
    ticker: str
    action: OrderAction
    price: Decimal
    quantity: int


class OrderPartialExecutedEventDTO(OrderExecutedEventDTO):
    remaining: int


class StocksUpdateEventDTO(BaseDTO):
    stocks: list[CandleDTO]


class StockUpdateEventDTO(BaseDTO):
    stock: CandleDTO


class PositionUpdateEventDTO(BaseDTO):
    position: PositionDTO


class OrderEventDTO(BaseDTO):
    order: OrderDTO


class OrderBookSnapshotEventDTO(BaseDTO):
    orders: list[OrderDTO]


class FixedAssetsUpdateEventDTO(BaseDTO):
    assets: list[FixedIncomeAssetDTO]


class PortfolioUpdateEventDTO(BaseDTO):
    portfolio: PortfolioDTO


class SnapshotUpdateEventDTO(BaseDTO):
    snapshot: PortfolioHistoryPointDTO


class StatisticsSnapshotEntryDTO(BaseDTO):
    player_nickname: str
    snapshot: SnapshotDTO


class StatisticsSnapshotUpdateEventDTO(BaseDTO):
    snapshots: list[StatisticsSnapshotEntryDTO]


class FutureRecordingProgressEventDTO(BaseDTO):
    """A série que começou a ser gravada e quantas já foram, de quantas."""

    series: str
    done: int
    total: int


class RealtimeEventCatalog(BaseDTO):
    """
    Um campo por nome de evento realtime, tipado para o DTO do payload
    correspondente. Nunca é instanciado de verdade — só existe para que seu
    schema apareça em `/openapi.json` via a rota dev-only em `routes/realtime.py`.
    """

    simulation_started: SimulationStatusResponse
    simulation_ended: SimulationEndedEventDTO
    simulation_update: SimulationTickUpdateEventDTO
    speed_update: SpeedUpdateEventDTO
    cash_update: CashUpdateEventDTO
    stocks_update: StocksUpdateEventDTO
    fixed_assets_update: FixedAssetsUpdateEventDTO
    snapshot_update: SnapshotUpdateEventDTO
    portfolio_update: PortfolioUpdateEventDTO
    statistics_snapshot_update: StatisticsSnapshotUpdateEventDTO
    goal_progress_update: GoalProgressDTO
    life_event: LifeEventDTO
    order_executed: OrderExecutedEventDTO
    order_partial_executed: OrderPartialExecutedEventDTO
    player_join: PlayerPresenceEventDTO
    player_exit: PlayerPresenceEventDTO
    player_color: PlayerPresenceEventDTO
    player_team: PlayerPresenceEventDTO
    simulation_selected: SimulationSelectedEventDTO
    simulation_deleted: SimulationDeletedEventDTO
    simulation_settings_update: SimulationSettingsDTO
    stock_update: StockUpdateEventDTO
    position_update: PositionUpdateEventDTO
    order_added: OrderEventDTO
    order_updated: OrderEventDTO
    order_book_snapshot: OrderBookSnapshotEventDTO
    future_recording_progress: FutureRecordingProgressEventDTO
    achievement_unlocked: AchievementUnlockedEventDTO
