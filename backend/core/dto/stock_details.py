from backend.core.dto.candle import CandleDTO
from backend.core.dto.stock_price_history import StockPriceHistoryDTO


class StockDetailsDTO(CandleDTO):
    history: list[StockPriceHistoryDTO]
