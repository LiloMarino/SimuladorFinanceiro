from decimal import Decimal

from backend.core.dto.base import BaseDTO
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO


class PlayerHistoryDTO(BaseDTO):
    player_nickname: str
    color: str
    simulation_id: int
    simulation_name: str
    # Índice da equipe (1 a 10); nulo fora do modo em equipes
    team: int | None = None
    starting_cash: Decimal
    history: list[PatrimonialHistoryDTO]
