from __future__ import annotations

from dataclasses import dataclass

from backend.core.dto.base import BaseDTO
from backend.features.variable_income.entities.position import Position


@dataclass(frozen=True, kw_only=True)
class PositionDTO(BaseDTO):
    ticker: str
    size: int
    total_cost: float
    avg_price: float

    @staticmethod
    def from_model(position: Position) -> PositionDTO:
        return PositionDTO(
            ticker=position.ticker,
            size=position.size,
            total_cost=position.total_cost,
            avg_price=position.avg_price,
        )
