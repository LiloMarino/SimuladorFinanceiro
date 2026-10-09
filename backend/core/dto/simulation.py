from datetime import date, datetime
from decimal import Decimal

from backend.core.dto.base import BaseDTO


class SimulationSettingsDTO(BaseDTO):
    name: str
    start_date: date
    end_date: date
    starting_cash: Decimal
    monthly_contribution: Decimal
    price_impact_enabled: bool
    price_impact_k: float
    price_impact_decay_days: int


class SimulationDTO(SimulationSettingsDTO):
    id: int


class SimulationSummaryDTO(SimulationSettingsDTO):
    id: int
    created_at: datetime
    last_simulated_at: datetime


class SimulationStatusResponse(BaseDTO):
    active: bool
    simulation: SimulationDTO | None = None
