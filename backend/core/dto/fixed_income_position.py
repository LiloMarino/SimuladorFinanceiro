from datetime import date
from decimal import Decimal

from backend.core.dto.base import BaseDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO


class FixedIncomePositionDTO(BaseDTO):
    asset: FixedIncomeAssetDTO
    total_applied: Decimal
    current_value: Decimal
    first_applied_date: date
    return_value: Decimal
    return_pct: Decimal
    portfolio_pct: Decimal
