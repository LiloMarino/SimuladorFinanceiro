from __future__ import annotations

from decimal import Decimal

from backend.core.dto.base import BaseDTO
from backend.core.utils import ratio
from backend.features.variable_income.entities.position import Position


class PositionDTO(BaseDTO):
    ticker: str
    size: int
    reserved: int
    total_cost: Decimal
    avg_price: Decimal
    current_price: Decimal
    current_value: Decimal
    return_value: Decimal
    return_pct: Decimal

    @staticmethod
    def from_model(position: Position, current_price: Decimal) -> PositionDTO:
        current_value = current_price * position.size
        return_value = current_value - position.total_cost
        return PositionDTO(
            ticker=position.ticker,
            size=position.size,
            reserved=position.reserved,
            total_cost=position.total_cost,
            avg_price=position.avg_price,
            current_price=current_price,
            current_value=current_value,
            return_value=return_value,
            return_pct=ratio(return_value, position.total_cost),
        )


class PortfolioPositionDTO(PositionDTO):
    portfolio_pct: Decimal
