from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from backend.core.dto.events.base_event import BaseEventDTO


class EquityEventType(Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True, slots=True, kw_only=True)
class EquityEventDTO(BaseEventDTO):
    ticker: str
    event_type: EquityEventType
    quantity: int
    price: Decimal
