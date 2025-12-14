from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from backend.core.dto.events.base_event import BaseEventDTO


class FixedIncomeEventType(str, Enum):
    BUY = "BUY"
    REDEEM = "REDEEM"


@dataclass(frozen=True, slots=True, kw_only=True)
class FixedIncomeEventDTO(BaseEventDTO):
    asset_id: int
    event_type: FixedIncomeEventType
    amount: Decimal
