from __future__ import annotations

from datetime import date
from decimal import Decimal

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
    size: Decimal
    remaining: Decimal
    limit_price: float | None
    # O dia da partida em que a ordem foi criada
    placed_on: date
    # Liquidez do mercado simulado, não de um jogador
    synthetic: bool
