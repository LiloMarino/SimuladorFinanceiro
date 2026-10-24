import uuid
from abc import ABC
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal

from backend.core.dto.order import OrderDTO
from backend.core.enum import OrderAction, OrderStatus, OrderType
from backend.core.runtime.user_manager import UserManager

# Dono das ordens da liquidez do mercado simulado, que não é um jogador
MARKET_CLIENT_ID: uuid.UUID = uuid.uuid5(uuid.NAMESPACE_DNS, "__MARKET__")


@dataclass(kw_only=True)
class Order(ABC):
    """Representa uma ordem de compra ou venda executada ou pendente."""

    client_id: uuid.UUID
    ticker: str
    size: Decimal
    action: OrderAction
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    remaining: Decimal = field(init=False)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    status: OrderStatus = OrderStatus.PENDING
    # Ordem enviada por uma estratégia: o aviso dela é o do registro da estratégia
    automatic: bool = False
    # Soma de quantidade x preço das execuções, para o preço médio
    notional: float = 0.0

    def __post_init__(self):
        self.remaining = self.size

    def to_dto(self) -> OrderDTO:
        synthetic = self.client_id == MARKET_CLIENT_ID
        color = None
        if synthetic:
            nickname = "Mercado"
        else:
            user = UserManager.get_user(self.client_id)
            nickname = "Unknown" if user is None else user.nickname
            color = None if user is None else UserManager.get_color(user.id)
        return OrderDTO(
            id=self.id,
            player_nickname=nickname,
            player_color=color,
            action=self.action,
            order_type=OrderType.LIMIT
            if isinstance(self, LimitOrder)
            else OrderType.MARKET,
            limit_price=getattr(self, "price", None),
            size=self.size,
            remaining=self.remaining,
            status=self.status,
            created_at=self.created_at,
            synthetic=synthetic,
        )


@dataclass(kw_only=True)
class MarketOrder(Order):
    # Compra por valor: o dinheiro que ainda pode ser gasto; cada execução desconta o que custou
    budget: Decimal | None = None


@dataclass(kw_only=True)
class LimitOrder(Order):
    price: float
