"""O código da B3 fica na base sem o `.SA`, que só entra ao falar com o yfinance."""

from __future__ import annotations

from typing import Any, ClassVar

import pandas as pd
import pytest

from backend.features.import_data import importer_service
from backend.routes import importer


@pytest.mark.parametrize(
    ("typed", "stored"),
    [("PETR4", "PETR4"), (" petr4.sa ", "PETR4"), ("BTC-USD", "BTC-USD")],
)
def test_bare_ticker_drops_the_suffix(typed: str, stored: str) -> None:
    assert importer_service.bare_ticker(typed) == stored


@pytest.mark.parametrize(
    ("ticker", "symbol"),
    [
        ("PETR4", "PETR4.SA"),
        ("KNRI11", "KNRI11.SA"),
        ("BTC-USD", "BTC-USD"),
        ("AAPL", "AAPL"),
        ("^BVSP", "^BVSP"),
    ],
)
def test_yfinance_symbol_adds_the_suffix_only_to_b3_codes(
    ticker: str, symbol: str
) -> None:
    assert importer_service.yfinance_symbol(ticker) == symbol


def _prices() -> pd.DataFrame:
    return pd.DataFrame(
        {"Open": [1.0], "High": [1.0], "Low": [1.0], "Close": [1.0], "Volume": [1.0]},
        index=pd.to_datetime(["2024-01-02"]),
    )


def test_download_asks_yfinance_for_the_symbol(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    asked: list[Any] = []

    def download(symbol: Any, **_kwargs: object) -> pd.DataFrame:
        asked.append(symbol)
        return _prices()

    monkeypatch.setattr(importer_service.yf, "download", download)
    importer_service.from_yfinance("PETR4")
    importer_service.from_yfinance("BTC-USD", "2024-01-01", "2024-02-01")
    assert asked == ["PETR4.SA", "BTC-USD"]


def test_batch_asks_for_symbols_and_answers_by_stored_code(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    asked: list[Any] = []
    columns = pd.MultiIndex.from_product(
        [["PETR4.SA", "BTC-USD"], ["Open", "High", "Low", "Close", "Volume"]]
    )
    frame = pd.DataFrame(
        [[1.0] * 10], columns=columns, index=pd.to_datetime(["2024-01-02"])
    )

    def download(symbols: Any, **_kwargs: object) -> pd.DataFrame:
        asked.append(symbols)
        return frame

    monkeypatch.setattr(importer_service.yf, "download", download)
    result = importer_service.from_yfinance_batch(["PETR4", "BTC-USD"])
    assert asked == [["PETR4.SA", "BTC-USD"]]
    assert list(result) == ["PETR4", "BTC-USD"]


def test_profile_is_requested_by_symbol(monkeypatch: pytest.MonkeyPatch) -> None:
    asked: list[str] = []

    class Ticker:
        info: ClassVar[dict[str, Any]] = {"longName": "Petrobras"}

        def __init__(self, symbol: str) -> None:
            asked.append(symbol)

    monkeypatch.setattr(importer_service.yf, "Ticker", Ticker)
    profile = importer_service._download_profile("PETR4")
    assert (asked, profile.ticker) == (["PETR4.SA"], "PETR4")


def test_requests_carry_the_code_without_the_suffix() -> None:
    """`PETR4.SA` digitado chega ao serviço como `PETR4`, no lote também."""
    single = importer.ImportYFinanceRequest(ticker="PETR4.SA")
    batch = importer.ImportYFinanceBatchRequest(tickers=["vale3.sa", "BTC-USD"])
    assert (single.ticker, batch.tickers) == ("PETR4", ["VALE3", "BTC-USD"])
