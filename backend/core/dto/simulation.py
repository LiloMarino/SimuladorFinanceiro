from datetime import date, datetime
from decimal import Decimal

from backend.core.dto.base import BaseDTO
from backend.core.enum import SimulationStatus, VictoryCriterion


class SimulationSettingsDTO(BaseDTO):
    name: str
    start_date: date
    end_date: date
    starting_cash: Decimal
    monthly_contribution: Decimal
    price_impact_enabled: bool
    price_impact_k: float
    price_impact_decay_days: int
    victory_criterion: VictoryCriterion


class SimulationDTO(SimulationSettingsDTO):
    id: int


class SimulationSummaryDTO(SimulationSettingsDTO):
    id: int
    created_at: datetime
    last_simulated_at: datetime


class SavedSimulationDTO(SimulationSummaryDTO):
    resume_from: date | None
    status: SimulationStatus
    players_count: int
    winner_nickname: str | None


class PriceImpactPointDTO(BaseDTO):
    day: int
    impact: float


class PriceImpactPreviewDTO(BaseDTO):
    volume_share: float
    first_day_impact: float
    curve: list[PriceImpactPointDTO]


class SimulationStatusResponse(BaseDTO):
    active: bool
    simulation: SimulationDTO | None = None
