from dataclasses import dataclass
from datetime import date, datetime

from backend.core.dto.base import BaseDTO


@dataclass(frozen=True, slots=True, kw_only=True)
class BaseEventDTO(BaseDTO):
    """
    Base para qualquer evento financeiro.
    """

    user_id: int
    event_date: date
    created_at: datetime
