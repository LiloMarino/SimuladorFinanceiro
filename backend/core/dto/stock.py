from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StockDTO:
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
