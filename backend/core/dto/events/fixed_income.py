from decimal import Decimal

from backend.core.dto.events.base_event import BaseEventDTO
from backend.core.enum import FixedIncomeEventType


class FixedIncomeEventDTO(BaseEventDTO):
    asset_id: int
    event_type: FixedIncomeEventType
    amount: Decimal
    # IR e IOF retidos no resgate (bruto - líquido); zero na aplicação
    tax_withheld: Decimal = Decimal(0)
