from backend.core.dto.base import BaseDTO
from backend.core.dto.fixed_income_position import FixedIncomePositionDTO
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.position import PositionDTO


class PortfolioDTO(BaseDTO):
    starting_cash: float
    cash: float
    variable_income: list[PositionDTO]
    fixed_income: list[FixedIncomePositionDTO]
    patrimonial_history: list[PatrimonialHistoryDTO]
