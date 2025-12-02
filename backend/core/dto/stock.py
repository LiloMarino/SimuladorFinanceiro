from dataclasses import dataclass
from datetime import date

from backend.core.dto.base import BaseDTO


@dataclass(frozen=True, slots=True, kw_only=True)
class StockDTO(BaseDTO):
    ticker: str
    name: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    price_date: date
    change: float
    change_pct: str
