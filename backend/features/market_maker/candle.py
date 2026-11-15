from datetime import date
from decimal import Decimal

from backend.core.dto.candle import CandleDTO
from backend.core.dto.stock import StockDTO
from backend.features.market_maker.account import DayTrades


def close_candle(
    stock: StockDTO,
    day: date,
    trades: DayTrades,
    previous_close: float | None,
    reference: Decimal,
) -> CandleDTO:
    """A vela do pregão: primeiro negócio, máxima, mínima, último negócio e volume.

    Sem negócio, a vela repete o último fechamento (ou o valor de referência, na estreia) e
    o volume é zero.
    """
    if trades.open is None:
        close = previous_close if previous_close is not None else float(reference)
        open_ = high = low = close
    else:
        open_, high, low, close = (
            float(trades.open),
            float(trades.high),
            float(trades.low),
            float(trades.close),
        )
    change = close - open_
    return CandleDTO(
        id=stock.id,
        ticker=stock.ticker,
        name=stock.name,
        asset_class=stock.asset_class,
        origin=stock.origin,
        open=open_,
        high=high,
        low=low,
        close=close,
        volume=int(trades.quantity),
        price_date=day,
        change=round(change, 2),
        change_pct=change / open_ if open_ else 0,
    )
