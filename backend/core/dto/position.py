from dataclasses import dataclass

from backend.core.dto.base import BaseDTO


@dataclass(frozen=True, slots=True, kw_only=True)
class PositionDTO(BaseDTO):
    ticker: str
    size: int
    total_cost: float
