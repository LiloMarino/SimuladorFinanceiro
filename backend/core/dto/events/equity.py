from decimal import Decimal

from backend.core.dto.events.base_event import PortfolioEventDTO
from backend.core.enum import EquityEventType


class EquityEventDTO(PortfolioEventDTO):
    ticker: str
    event_type: EquityEventType
    quantity: Decimal
    price: Decimal
