from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from backend.core import repository
from backend.features.strategy.price_history import PriceHistory


class FixedFactor:
    """Impacto que multiplica todos os dias pelo mesmo fator."""

    def __init__(self, factor: float):
        self.factor = factor
        self.requested: list[list[date]] = []

    def factors_on(self, ticker: str, days: list[date]) -> dict[date, float]:
        self.requested.append(list(days))
        return {day: self.factor for day in days}


@pytest.fixture
def frame(monkeypatch: pytest.MonkeyPatch) -> pd.DataFrame:
    index = pd.bdate_range("2020-01-01", periods=10)
    prices = pd.DataFrame(
        {
            "open": [10.0 + i for i in range(10)],
            "high": [11.0 + i for i in range(10)],
            "low": [9.0 + i for i in range(10)],
            "close": [10.5 + i for i in range(10)],
            "volume": list(range(100, 110)),
        },
        index=index,
    )
    loads: list[list[str]] = []

    def _get_price_frame(tickers, end_date, simulation_id):
        loads.append(list(tickers))
        return {t: prices for t in tickers}

    monkeypatch.setattr(repository.stock, "get_price_frame", _get_price_frame)
    prices.attrs["loads"] = loads
    return prices


def _history(factor: float = 1.0) -> PriceHistory:
    return PriceHistory(1, date(2020, 12, 31), FixedFactor(factor))  # pyright: ignore[reportArgumentType]


def test_window_ends_on_the_requested_day(frame: pd.DataFrame):
    window = _history().window("ABCD", date(2020, 1, 8), 3)

    assert list(window.index) == list(frame.index[3:6])
    assert window["close"].tolist() == [13.5, 14.5, 15.5]
    assert window["volume"].tolist() == [103, 104, 105]


def test_window_scales_prices_by_the_factor_and_keeps_volume(frame: pd.DataFrame):
    window = _history(1.02).window("ABCD", date(2020, 1, 3), 5)

    assert window["open"].tolist() == [10.2, 11.22, 12.24]
    assert window["close"].tolist() == [10.71, 11.73, 12.75]
    assert window["volume"].tolist() == [100, 101, 102]


def test_window_on_a_non_trading_day_ends_on_the_previous_session(frame: pd.DataFrame):
    saturday = date(2020, 1, 4)

    window = _history().window("ABCD", saturday, 2)

    assert list(window.index) == list(frame.index[1:3])


def test_window_before_the_history_is_empty(frame: pd.DataFrame):
    window = _history().window("ABCD", date(2019, 12, 1), 5)

    assert window.empty
    assert list(window.columns) == ["open", "high", "low", "close", "volume"]


def test_each_ticker_is_read_from_the_database_once(frame: pd.DataFrame):
    history = _history()

    for day in (date(2020, 1, 3), date(2020, 1, 6), date(2020, 1, 7)):
        history.window("ABCD", day, 2)

    assert frame.attrs["loads"] == [["ABCD"]]
