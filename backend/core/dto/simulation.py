from datetime import date

from backend.core.dto.base import BaseDTO


class SimulationDTO(BaseDTO):
    start_date: date
    end_date: date
    starting_cash: float
    monthly_contribution: float
