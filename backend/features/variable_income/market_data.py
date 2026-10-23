from collections import deque

from backend.features.variable_income.entities.candle import Candle


class MarketData:
    """
    Buffer de candles históricos de mercado por ticker.

    Responsável por:
    - Armazenar histórico limitado de candles (OHLCV) por ticker
    - Fornecer acesso aos candles mais recentes para análise
    - Retornar o último candle de um ticker para referência de preço
    """

    def __init__(self, maxlen: int = 30):
        self._buffers: dict[str, deque[Candle]] = {}
        self._maxlen = maxlen

    def add_candle(self, candle: Candle, *, replace_current: bool = False):
        if candle.ticker not in self._buffers:
            self._buffers[candle.ticker] = deque(maxlen=self._maxlen)
        buffer = self._buffers[candle.ticker]
        if replace_current and buffer and buffer[-1].price_date == candle.price_date:
            buffer.pop()
        self._buffers[candle.ticker].append(candle)

    def get_recent(self, ticker: str) -> list[Candle]:
        return list(self._buffers.get(ticker, []))

    def get_last(self, ticker: str) -> Candle | None:
        buffer = self._buffers.get(ticker)
        if not buffer:
            return None
        return buffer[-1]
