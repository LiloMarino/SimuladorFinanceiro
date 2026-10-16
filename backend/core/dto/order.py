from __future__ import annotations

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
from backend.features.variable_income.market_liquidity import MarketLiquidity


class OrderDTO(BaseDTO):
    id: str
    player_nickname: str
    # Chave da paleta; None para a liquidez do mercado simulado
    player_color: str | None
    action: OrderAction
    order_type: OrderType
    status: OrderStatus
    size: int
    remaining: int
    limit_price: float | None
    created_at: datetime
    # Liquidez do mercado simulado, não de um jogador
    synthetic: bool

    @staticmethod
    def from_model(order: Order) -> OrderDTO:
        synthetic = order.client_id == MarketLiquidity.MARKET_CLIENT_ID
        color = None
        if synthetic:
            nickname = "Mercado"
        else:
            user = UserManager.get_user(order.client_id)
            nickname = "Unknown" if user is None else user.nickname
            color = None if user is None else UserManager.get_color(user.id)
        return OrderDTO(
            id=order.id,
            player_nickname=nickname,
            player_color=color,
            action=order.action,
            order_type=OrderType.LIMIT
            if isinstance(order, LimitOrder)
            else OrderType.MARKET,
            limit_price=getattr(order, "price", None),
            size=order.size,
            remaining=order.remaining,
            status=order.status,
            created_at=order.created_at,
            synthetic=synthetic,
        )
