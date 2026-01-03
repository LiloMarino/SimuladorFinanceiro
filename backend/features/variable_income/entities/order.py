import uuid
from abc import ABC
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class OrderAction(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    EXECUTED = "executed"
    PARTIAL = "partial"
    PENDING = "pending"
    CANCELED = "canceled"


@dataclass(kw_only=True)
class Order(ABC):
    """Representa uma ordem de compra ou venda executada ou pendente."""

    client_id: str
    ticker: str
    size: int
    action: OrderAction
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    remaining: int = field(init=False)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    status: OrderStatus = OrderStatus.PENDING

    def __post_init__(self):
        self.remaining = self.size


@dataclass(kw_only=True)
class MarketOrder(Order):
    pass


@dataclass(kw_only=True)
class LimitOrder(Order):
    price: float
