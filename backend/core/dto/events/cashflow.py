from dataclasses import dataclass
from decimal import Decimal

from backend.core.dto.events.base_event import BaseEventDTO
from backend.core.enum import CashflowEventType


@dataclass(frozen=True, slots=True, kw_only=True)
class CashflowEventDTO(BaseEventDTO):
    event_type: CashflowEventType
    amount: Decimal
