from __future__ import annotations

import datetime
from dataclasses import dataclass

from backend.core.dto.base import BaseDTO
from backend.core.models.models import StockPriceHistory


@dataclass(frozen=True, slots=True, kw_only=True)
class StockPriceHistoryDTO(BaseDTO):
    stock_id: int
    price_date: datetime.date
    open: float
    high: float
    low: float
    close: float
    volume: int

    @staticmethod
    def from_model(m: StockPriceHistory) -> StockPriceHistoryDTO:
        return StockPriceHistoryDTO(
            stock_id=m.stock_id,
            price_date=m.price_date,
            open=m.open,
            high=m.high,
            low=m.low,
            close=m.close,
            volume=m.volume,
        )
