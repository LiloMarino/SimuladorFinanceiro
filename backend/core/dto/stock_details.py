from dataclasses import dataclass

from backend.core.dto.base import BaseDTO
from backend.core.dto.stock_price_history import StockPriceHistoryDTO


@dataclass(frozen=True, slots=True, kw_only=True)
class StockDetailsDTO(BaseDTO):
    ticker: str
    name: str
    price: float
    low: float
    high: float
    volume: int
    change: float
    change_pct: str
    history: list[StockPriceHistoryDTO]
