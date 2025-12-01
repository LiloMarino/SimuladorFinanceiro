from dataclasses import dataclass

from backend.core.models.models import StockPriceHistory


@dataclass(frozen=True, slots=True)
class StockDetailsDTO:
    ticker: str
    name: str
    price: float
    low: float
    high: float
    volume: int
    change: float
    change_pct: str
    history: list[StockPriceHistory]
