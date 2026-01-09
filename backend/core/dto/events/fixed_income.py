from dataclasses import dataclass
from decimal import Decimal

from backend.core.dto.events.base_event import BaseEventDTO
from backend.core.enum import FixedIncomeEventType


@dataclass(frozen=True, kw_only=True)
class FixedIncomeEventDTO(BaseEventDTO):
    asset_id: int
    event_type: FixedIncomeEventType
    amount: Decimal
