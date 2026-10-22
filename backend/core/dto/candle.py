from __future__ import annotations

from datetime import date

from backend.core.dto.stock import StockDTO
from backend.core.dto.stock_price_history import StockPriceHistoryDTO
from backend.core.enum import AssetClass
from backend.core.models.models import Stock, StockPriceHistory


class CandleDTO(StockDTO):
    open: float
    high: float
    low: float
    close: float
    volume: int
    price_date: date
    # Variação do dia (fechamento - abertura); `change_pct` em fração: 0.0141 = +1,41%
    change: float
    change_pct: float

    @staticmethod
    def from_prices(
        stock: Stock, prices: StockPriceHistory | StockPriceHistoryDTO
    ) -> CandleDTO:
        change = prices.close - prices.open
        return CandleDTO(
            id=stock.id,
            ticker=stock.ticker,
            name=stock.name,
            asset_class=AssetClass(stock.asset_class),
            open=prices.open,
            high=prices.high,
            low=prices.low,
            close=prices.close,
            volume=prices.volume,
            price_date=prices.price_date,
            change=round(change, 2),
            change_pct=change / prices.open if prices.open else 0,
        )


class MarketQuoteDTO(CandleDTO):
    # Fechamentos dos últimos 30 pregões até hoje, do mais antigo ao mais recente
    sparkline: list[float]
    sector: str | None
    segment: str | None
