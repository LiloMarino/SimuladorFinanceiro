from dataclasses import dataclass


@dataclass
class Position:
    """Representa uma posição aberta em um ativo."""

    ticker: str
    size: int = 0
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
            raise ValueError("Venda excede posição disponível.")
        self.total_cost -= self.avg_price * size
        self.size -= size
        self.avg_price = self.total_cost / self.size
