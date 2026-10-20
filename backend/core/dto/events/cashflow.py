from decimal import Decimal

from backend.core.dto.events.base_event import BaseEventDTO
from backend.core.enum import CashflowEventType


class CashflowEventDTO(BaseEventDTO):
    event_type: CashflowEventType
    amount: Decimal
    # Qual imprevisto foi; nulo nos outros eventos
    life_event_key: str | None = None
