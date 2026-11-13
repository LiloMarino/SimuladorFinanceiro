from decimal import Decimal

from backend.core.dto.events.base_event import PortfolioEventDTO
from backend.core.enum import FixedIncomeEventType


class FixedIncomeEventDTO(PortfolioEventDTO):
    asset_id: int
    event_type: FixedIncomeEventType
    amount: Decimal
    # IR e IOF retidos no resgate (bruto - líquido); zero na aplicação
    tax_withheld: Decimal = Decimal(0)
    # Dólar do dia em reais; só a conta em dólar guarda (compra em R$, resgate em US$)
    fx_rate: Decimal | None = None
