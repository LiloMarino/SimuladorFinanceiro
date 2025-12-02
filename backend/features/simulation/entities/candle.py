from dataclasses import dataclass
from datetime import date


@dataclass
class Candle:
    """Representa um candle de mercado."""

    ticker: str
    price_date: date
    open: float
    high: float
    low: float
    close: float
    volume: int

    @property
    def price(self) -> float:
        """Retorna o preço de fechamento (usado como referência de mercado)."""
        return self.close
