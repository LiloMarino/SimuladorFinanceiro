from datetime import UTC, date, datetime

from pydantic import Field

from backend.core.dto.base import BaseDTO
from backend.core.enum import GovernmentEventType


class GovernmentEventDTO(BaseDTO):
    """Um fato político da partida; o `payload` de cada tipo é lido por `government.state.apply`."""

    simulation_id: int
    event_type: GovernmentEventType
    payload: dict[str, object]
    event_date: date
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
