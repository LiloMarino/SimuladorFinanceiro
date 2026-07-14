from datetime import date, datetime

from backend.core.dto.base import BaseDTO


class SimulationSettingsDTO(BaseDTO):
    name: str
    start_date: date
    end_date: date
    starting_cash: float
    monthly_contribution: float


class SimulationDTO(SimulationSettingsDTO):
    id: int


class SimulationSummaryDTO(SimulationSettingsDTO):
    id: int
    created_at: datetime
    last_simulated_at: datetime


class SimulationStatusResponse(BaseDTO):
    active: bool
    simulation: SimulationDTO | None = None
