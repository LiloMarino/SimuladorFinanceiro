from dataclasses import dataclass, field
from decimal import Decimal

from backend.core.dto.position import PositionDTO
from backend.core.exceptions import InsufficentPositionError
from backend.core.utils import ratio


@dataclass
class Position:
    """Representa uma posição aberta em um ativo."""

    ticker: str
    size: Decimal = field(default_factory=Decimal)
    reserved: Decimal = field(default_factory=Decimal)
    total_cost: Decimal = field(default_factory=Decimal)
    avg_price: Decimal = field(default_factory=Decimal)

    def update_buy(self, price: Decimal, size: Decimal):
        """Atualiza posição após uma compra."""
        self.total_cost += price * size
        self.size += size
        self.avg_price = self.total_cost / self.size

    def update_sell(self, size: Decimal):
        """Atualiza posição após uma venda."""
        if self.size - size < 0:
            raise InsufficentPositionError()
        self.total_cost -= self.avg_price * size
        self.size -= size
        self.avg_price = (self.total_cost / self.size) if self.size > 0 else Decimal(0)

    def reserve(self, size: Decimal):
        """Reserva parte da posição para ordens em aberto."""
        if self.size - self.reserved < size:
            raise InsufficentPositionError()
        self.reserved += size

    def release(self, size: Decimal):
        """Libera parte da posição reservada."""
        self.reserved = max(Decimal(0), self.reserved - size)

    def to_dto(self, current_price: Decimal) -> PositionDTO:
        current_value = current_price * self.size
        return_value = current_value - self.total_cost
        return PositionDTO(
            ticker=self.ticker,
            size=self.size,
            reserved=self.reserved,
            total_cost=self.total_cost,
            avg_price=self.avg_price,
            current_price=current_price,
            current_value=current_value,
            return_value=return_value,
            return_pct=ratio(return_value, self.total_cost),
        )
