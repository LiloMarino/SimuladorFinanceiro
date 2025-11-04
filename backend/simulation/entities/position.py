from dataclasses import dataclass


@dataclass
class Position:
    """Representa uma posição aberta em um ativo."""

    ticker: str
    size: int = 0
    avg_price: float = 0.0

    def update_buy(self, price: float, size: int):
        """Atualiza posição após uma compra."""
        if self.size + size == 0:
            self.avg_price = price
        else:
            total_cost = self.avg_price * self.size + price * size
            self.size += size
            self.avg_price = total_cost / self.size

    def update_sell(self, size: int):
        """Atualiza posição após uma venda."""
        self.size -= size
        if self.size < 0:
            raise ValueError("Venda excede posição disponível.")
