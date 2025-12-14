from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"


class OrderAction(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    EXECUTED = "executed"
    PENDING = "pending"
    CANCELED = "canceled"


@dataclass
class Order:
    """Representa uma ordem de compra ou venda executada ou pendente."""

    client_id: str
    ticker: str
    size: int
    action: OrderAction
    order_type: OrderType
    price: float | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    status: OrderStatus = OrderStatus.PENDING
