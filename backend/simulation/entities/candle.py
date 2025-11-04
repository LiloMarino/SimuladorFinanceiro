from dataclasses import dataclass
from datetime import datetime


@dataclass
class Candle:
    """Representa um candle de mercado."""

    ticker: str
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

    @property
    def price(self) -> float:
        """Retorna o preço de fechamento (usado como referência de mercado)."""
        return self.close
