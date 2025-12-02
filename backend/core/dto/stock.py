from dataclasses import dataclass

from backend.core.dto.base import BaseDTO


@dataclass(frozen=True, slots=True, kw_only=True)
class StockDTO(BaseDTO):
    ticker: str
    name: str
    open: float
    high: float
    low: float
    price: float
    volume: int
    date: str
    change: float
    change_pct: str
