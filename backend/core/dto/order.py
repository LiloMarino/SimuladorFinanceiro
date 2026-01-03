from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from backend.core.dto.base import BaseDTO
from backend.features.variable_income.entities.order import (
    LimitOrder,
    Order,
    OrderAction,
    OrderType,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class OrderDTO(BaseDTO):
    id: str
    client_id: str
    ticker: str
    action: OrderAction
    order_type: OrderType
    price: float | None
    size: int
    remaining: int
    status: str
    timestamp: datetime

    @staticmethod
    def from_model(order: Order) -> OrderDTO:
        return OrderDTO(
            id=order.id,
            client_id=order.client_id,
            ticker=order.ticker,
            action=order.action,
            order_type=OrderType.LIMIT
            if isinstance(order, LimitOrder)
            else OrderType.MARKET,
            price=getattr(order, "price", None),
            size=order.size,
            remaining=order.remaining,
            status=order.status.value,
            timestamp=order.timestamp,
        )
