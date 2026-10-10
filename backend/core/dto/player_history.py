from decimal import Decimal

from backend.core.dto.base import BaseDTO
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO


class PlayerHistoryDTO(BaseDTO):
    player_nickname: str
    simulation_id: int
    simulation_name: str
    starting_cash: Decimal
    history: list[PatrimonialHistoryDTO]
