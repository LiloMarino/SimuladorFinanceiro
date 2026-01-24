from __future__ import annotations

from datetime import date

from backend.core.dto.base import BaseDTO
from backend.core.models.models import StockPriceHistory


class StockPriceHistoryDTO(BaseDTO):
    price_date: date
    open: float
    high: float
    low: float
    close: float
    volume: int

    @staticmethod
    def from_model(m: StockPriceHistory) -> StockPriceHistoryDTO:
        return StockPriceHistoryDTO(
            price_date=m.price_date,
            open=m.open,
            high=m.high,
            low=m.low,
            close=m.close,
            volume=m.volume,
        )
