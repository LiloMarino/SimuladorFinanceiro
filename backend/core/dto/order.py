from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from backend.core.dto.base import BaseDTO
from backend.core.runtime.user_manager import UserManager
from backend.features.variable_income.entities.order import (
    LimitOrder,
    Order,
    OrderAction,
    OrderStatus,
    OrderType,
)


@dataclass(frozen=True, kw_only=True)
class OrderDTO(BaseDTO):
    id: str
    player_nickname: str
    action: OrderAction
    order_type: OrderType
    status: OrderStatus
    size: int
    remaining: int
    limit_price: float | None
    created_at: datetime

    @staticmethod
    def from_model(order: Order) -> OrderDTO:
        if order.client_id == "__MARKET__":
            nickname = "Mercado"
        else:
            user = UserManager.get_user(order.client_id)
            nickname = "Unknown" if user is None else user.nickname
        return OrderDTO(
            id=order.id,
            player_nickname=nickname,
            action=order.action,
            order_type=OrderType.LIMIT
            if isinstance(order, LimitOrder)
            else OrderType.MARKET,
            limit_price=getattr(order, "price", None),
            size=order.size,
            remaining=order.remaining,
            status=order.status,
            created_at=order.created_at,
        )
