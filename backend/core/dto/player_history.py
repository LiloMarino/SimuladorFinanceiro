from dataclasses import dataclass

from backend.core.dto.base import BaseDTO
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO


@dataclass(frozen=True, kw_only=True)
class PlayerHistoryDTO(BaseDTO):
    player_nickname: str
    starting_cash: float
    history: list[PatrimonialHistoryDTO]
