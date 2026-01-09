from dataclasses import dataclass
from datetime import date

from backend.core.dto.base import BaseDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO


@dataclass(frozen=True, kw_only=True)
class FixedIncomePositionDTO(BaseDTO):
    asset: FixedIncomeAssetDTO
    total_applied: float
    current_value: float
    first_applied_date: date
