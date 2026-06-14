from datetime import date, datetime

from backend.core.dto.base import BaseDTO


class SimulationDTO(BaseDTO):
    name: str
    start_date: date
    end_date: date
    starting_cash: float
    monthly_contribution: float
    # Preenchido apenas quando a simulação já existe no banco
    # (settings pendentes/pré-criação não têm id).
    simulation_id: int | None = None


class SimulationSummaryDTO(BaseDTO):
    """Resumo de uma simulação persistida (para listagem/histórico)."""

    id: int
    name: str
    start_date: date
    end_date: date
    starting_cash: float
    monthly_contribution: float
    created_at: datetime
    last_simulated_at: datetime
