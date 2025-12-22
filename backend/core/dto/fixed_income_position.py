from dataclasses import dataclass

from backend.core.dto.base import BaseDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO


@dataclass(frozen=True, slots=True, kw_only=True)
class FixedIncomePositionDTO(BaseDTO):
    asset: FixedIncomeAssetDTO
    total_applied: float
    current_value: float
