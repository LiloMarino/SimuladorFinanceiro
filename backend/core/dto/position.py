from __future__ import annotations

from decimal import Decimal

from backend.core.dto.base import BaseDTO


class PositionDTO(BaseDTO):
    ticker: str
    size: Decimal
    reserved: Decimal
    total_cost: Decimal
    avg_price: Decimal
    current_price: Decimal
    current_value: Decimal
    return_value: Decimal
    return_pct: Decimal


class PortfolioPositionDTO(PositionDTO):
    name: str
    portfolio_pct: Decimal
