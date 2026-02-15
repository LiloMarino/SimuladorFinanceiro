from dataclasses import dataclass

from backend.core.exceptions import InsufficentPositionError


@dataclass
class Position:
    """Representa uma posição aberta em um ativo."""

    ticker: str
    size: int = 0
    reserved: int = 0
    total_cost: float = 0
    avg_price: float = 0

    def update_buy(self, price: float, size: int):
        """Atualiza posição após uma compra."""
        self.total_cost += price * size
        self.size += size
        self.avg_price = self.total_cost / self.size

    def update_sell(self, size: int):
        """Atualiza posição após uma venda."""
        if self.size - size < 0:
            raise InsufficentPositionError()
        self.total_cost -= self.avg_price * size
        self.size -= size
        self.avg_price = (self.total_cost / self.size) if self.size > 0 else 0

    def reserve(self, size: int):
        """Reserva parte da posição para ordens em aberto."""
        if self.size - self.reserved < size:
            raise InsufficentPositionError()
        self.reserved += size

    def release(self, size: int):
        """Libera parte da posição reservada."""
        self.reserved = max(0, self.reserved - size)
