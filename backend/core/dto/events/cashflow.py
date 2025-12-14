from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from backend.core.dto.events.base_event import BaseEventDTO


class CashflowEventType(Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    DIVIDEND = "DIVIDEND"


@dataclass(frozen=True, slots=True, kw_only=True)
class CashflowEventDTO(BaseEventDTO):
    event_type: CashflowEventType
    amount: Decimal
