from datetime import date

from backend.core.dto.stock import StockDTO


class CandleDTO(StockDTO):
    open: float
    high: float
    low: float
    close: float
    volume: int
    price_date: date
    change: float
    change_pct: str
