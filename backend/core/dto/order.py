from __future__ import annotations

from datetime import date
from decimal import Decimal

from backend.core.dto.base import BaseDTO
from backend.core.enum import OrderAction, OrderOwner, OrderStatus, OrderType


class OrderDTO(BaseDTO):
    id: str
    # Quem pôs a ordem: o apelido do jogador, o nome da gestora ou o do dono sintético
    player_nickname: str
    # Chave da paleta do jogador; None para quem não tem cor (bot sem cor, gestora e donos sintéticos)
    player_color: str | None
    owner: OrderOwner
    action: OrderAction
    order_type: OrderType
    status: OrderStatus
    size: Decimal
    remaining: Decimal
    limit_price: float | None
    # O dia da partida em que a ordem foi criada
    placed_on: date
