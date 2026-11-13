from datetime import UTC, date, datetime

from pydantic import Field

from backend.core.dto.base import BaseDTO


class BaseEventDTO(BaseDTO):
    """Base para qualquer evento da partida."""

    simulation_id: int
    event_date: date
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PortfolioEventDTO(BaseEventDTO):
    """Evento financeiro: pertence à carteira, não ao jogador que a controla."""

    portfolio_id: int
