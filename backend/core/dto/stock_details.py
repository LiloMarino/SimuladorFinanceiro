from dataclasses import dataclass

from backend.core.dto.candle import CandleDTO
from backend.core.dto.stock_price_history import StockPriceHistoryDTO


@dataclass(frozen=True, kw_only=True)
class StockDetailsDTO(CandleDTO):
    history: list[StockPriceHistoryDTO]
