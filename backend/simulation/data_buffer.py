from collections import deque


class DataBuffer:
    def __init__(self, maxlen: int = 30):
        self._buffers: dict[str, deque] = {}
        self._maxlen = maxlen

    def add_candle(self, ticker: str, candle: dict):
        if ticker not in self._buffers:
            self._buffers[ticker] = deque(maxlen=self._maxlen)
        self._buffers[ticker].append(candle)

    def get_recent(self, ticker: str) -> list[dict]:
        return list(self._buffers.get(ticker, []))
