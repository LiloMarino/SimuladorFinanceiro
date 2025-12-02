from dataclasses import dataclass

from backend.core.dto.stock import StockDTO
from backend.core.dto.stock_price_history import StockPriceHistoryDTO


@dataclass(frozen=True, slots=True, kw_only=True)
class StockDetailsDTO(StockDTO):
    history: list[StockPriceHistoryDTO]
