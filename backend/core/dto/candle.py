from datetime import date

from backend.core.dto.stock import StockDTO


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


class MarketQuoteDTO(CandleDTO):
    # Fechamentos dos últimos 30 pregões até hoje, do mais antigo ao mais recente
    sparkline: list[float]
    sector: str | None
    segment: str | None
