from decimal import Decimal

from backend.core.dto.base import BaseDTO
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO


class PlayerHistoryDTO(BaseDTO):
    player_nickname: str
    simulation_id: int
    simulation_name: str
    starting_cash: Decimal
    history: list[PatrimonialHistoryDTO]


class PlayerPerformanceDTO(PlayerHistoryDTO):
    position: int
    total_networth: Decimal
    return_value: Decimal
    return_percent: Decimal


class PerformanceReportDTO(BaseDTO):
    # Ordenado pelo ranking: o primeiro tem o melhor retorno e o último, o pior
    players: list[PlayerPerformanceDTO]
    average_return: Decimal | None
