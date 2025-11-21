from collections import deque

from backend.features.simulation.entities.candle import Candle


class DataBuffer:
    def __init__(self, maxlen: int = 30):
        self._buffers: dict[str, deque[Candle]] = {}
        self._maxlen = maxlen

    def add_candle(self, candle: Candle):
        if candle.ticker not in self._buffers:
            self._buffers[candle.ticker] = deque(maxlen=self._maxlen)
        self._buffers[candle.ticker].append(candle)

    def get_recent(self, ticker: str) -> list[Candle]:
        return list(self._buffers.get(ticker, []))
