from decimal import Decimal

from backend.core.dto.base import BaseDTO
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO


class PlayerHistoryDTO(BaseDTO):
    player_nickname: str
    simulation_id: int
    simulation_name: str
    starting_cash: Decimal
    history: list[PatrimonialHistoryDTO]


class RiskMetricsDTO(BaseDTO):
    # Drawdown e volatilidade em fração (0.2 = 20%), Sharpe em número puro;
    # None quando a série ainda é curta demais para medir
    max_drawdown: Decimal | None
    annual_volatility: Decimal | None
    sharpe_ratio: Decimal | None


class PlayerPerformanceDTO(PlayerHistoryDTO):
    position: int
    total_networth: Decimal
    return_value: Decimal
    return_percent: Decimal
    risk: RiskMetricsDTO


class PerformanceReportDTO(BaseDTO):
    # Ordenado pelo ranking: o primeiro tem o melhor retorno e o último, o pior
    players: list[PlayerPerformanceDTO]
    average_return: Decimal | None
