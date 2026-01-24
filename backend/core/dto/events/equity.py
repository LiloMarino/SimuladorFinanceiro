from decimal import Decimal

from backend.core.dto.events.base_event import BaseEventDTO
from backend.core.enum import EquityEventType


class EquityEventDTO(BaseEventDTO):
    ticker: str
    event_type: EquityEventType
    quantity: int
    price: Decimal
