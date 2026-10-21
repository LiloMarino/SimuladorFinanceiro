from __future__ import annotations

from datetime import datetime

from backend.core.dto.base import BaseDTO
from backend.core.enum import OrderAction, OrderStatus, OrderType


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
