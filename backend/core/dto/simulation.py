from dataclasses import dataclass
from datetime import date

from backend.core.dto.base import BaseDTO


@dataclass(frozen=True, slots=True, kw_only=True)
class SimulationDTO(BaseDTO):
    start_date: date
    end_date: date
    starting_cash: float
    monthly_contribution: float
