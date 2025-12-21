from dataclasses import dataclass

from backend.core.dto.base import BaseDTO
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.position import PositionDTO


@dataclass(frozen=True, slots=True, kw_only=True)
class PortfolioDTO(BaseDTO):
    cash: float
    variable_income: list[PositionDTO]
    # fixed_income: list[FixedIncomePositionDTO]
    patrimonial_history: list[PatrimonialHistoryDTO]
