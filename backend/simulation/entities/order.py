from dataclasses import dataclass
from datetime import datetime
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

    ticker: str
    size: int
    price: float
    timestamp: datetime
    action: OrderAction
    order_type: OrderType
    status: OrderStatus = OrderStatus.PENDING
