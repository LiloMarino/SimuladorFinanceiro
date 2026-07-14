"""
DTOs dos payloads emitidos via `notify(...)` (WebSocket/SSE).

Servem para dois propósitos:
1. Tipar os call sites de `notify(...)` em vez de dicts soltos.
2. Compor `RealtimeEventCatalog`, exposto via rota dev-only para que
   `openapi-typescript` gere `types/events.ts` a partir destes schemas.
"""

from typing import Literal

from backend.core.dto.base import BaseDTO
from backend.core.dto.candle import CandleDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.dto.fixed_income_position import FixedIncomePositionDTO
from backend.core.dto.order import OrderDTO
from backend.core.dto.position import PositionDTO
from backend.core.dto.simulation import SimulationSettingsDTO, SimulationStatusResponse
from backend.core.dto.snapshot import SnapshotDTO
from backend.features.variable_income.entities.order import OrderAction


class CashUpdateEventDTO(BaseDTO):
    cash: float


class SpeedUpdateEventDTO(BaseDTO):
    speed: int


class SimulationTickUpdateEventDTO(BaseDTO):
    current_date: str


class PlayerPresenceEventDTO(BaseDTO):
    nickname: str


class SimulationEndedEventDTO(BaseDTO):
    reason: Literal["completed", "stopped_by_host"]


class OrderExecutedEventDTO(BaseDTO):
    order_id: str
    ticker: str
    action: OrderAction
    price: float
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


class FixedIncomePositionUpdateEventDTO(BaseDTO):
    positions: list[FixedIncomePositionDTO]


class SnapshotUpdateEventDTO(BaseDTO):
    snapshot: SnapshotDTO


class StatisticsSnapshotEntryDTO(BaseDTO):
    player_nickname: str
    snapshot: SnapshotDTO


class StatisticsSnapshotUpdateEventDTO(BaseDTO):
    snapshots: list[StatisticsSnapshotEntryDTO]


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
    fixed_income_position_update: FixedIncomePositionUpdateEventDTO
    statistics_snapshot_update: StatisticsSnapshotUpdateEventDTO
    order_executed: OrderExecutedEventDTO
    order_partial_executed: OrderPartialExecutedEventDTO
    player_join: PlayerPresenceEventDTO
    player_exit: PlayerPresenceEventDTO
    simulation_settings_update: SimulationSettingsDTO
    stock_update: StockUpdateEventDTO
    position_update: PositionUpdateEventDTO
    order_added: OrderEventDTO
    order_updated: OrderEventDTO
    order_book_snapshot: OrderBookSnapshotEventDTO
