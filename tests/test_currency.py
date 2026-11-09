"""O ativo cotado em dólar entra na base em real, convertido pela PTAX de cada dia."""

from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd
import pytest
from sqlalchemy import Engine

from backend.core import repository
from backend.core.enum import AssetClass, Currency, IndicatorSeries
from backend.core.exceptions.http_exceptions import UnprocessableEntityError
from backend.features.import_data import importer_service
from backend.features.import_data.bcb_sgs import fetch_sgs
from backend.features.import_data.currency import to_brl
from backend.features.import_data.indicators import INDICATOR_SOURCES

# Sexta, sábado, domingo e segunda: a PTAX só publica em dia útil
DAYS = pd.to_datetime(["2024-01-05", "2024-01-06", "2024-01-07", "2024-01-08"])
PTAX = pd.Series(
    [4.9, 5.0], index=pd.to_datetime(["2024-01-05", "2024-01-08"]), dtype=float
)


def _frame(
    days: pd.DatetimeIndex = DAYS, dividends: float = 0.0, splits: float = 0.0
) -> pd.DataFrame:
    size = len(days)
    return pd.DataFrame(
        {
            "Open": [100.0] * size,
            "High": [102.0] * size,
            "Low": [99.0] * size,
            "Close": [101.0] * size,
            "Volume": [1000.0] * size,
            "Dividends": [dividends] * size,
            "Stock Splits": [splits] * size,
        },
        index=days,
    )


def test_usd_prices_are_multiplied_by_the_ptax_of_each_day() -> None:
    converted = to_brl(_frame(), Currency.USD, PTAX)
    # Fim de semana usa a PTAX de sexta; segunda tem a sua
    assert converted["Close"].tolist() == [494.9, 494.9, 494.9, 505.0]
    assert converted["Open"].tolist() == [490.0, 490.0, 490.0, 500.0]


def test_dividend_is_converted_and_split_and_volume_are_kept() -> None:
    converted = to_brl(_frame(dividends=0.25, splits=2.0), Currency.USD, PTAX)
    assert converted["Dividends"].tolist() == [1.225, 1.225, 1.225, 1.25]
    assert converted["Stock Splits"].tolist() == [2.0] * 4
    assert converted["Volume"].tolist() == [1000.0] * 4


def test_days_before_the_first_ptax_are_dropped() -> None:
    days = pd.to_datetime(["1994-06-30", "2024-01-05"])
    converted = to_brl(_frame(days), Currency.USD, PTAX)
    assert list(converted.index) == [pd.Timestamp("2024-01-05")]


def test_brl_comes_back_untouched() -> None:
    frame = _frame()
    assert to_brl(frame, Currency.BRL, PTAX).equals(frame)


def _yfinance_quoting_in(monkeypatch: pytest.MonkeyPatch, code: str) -> None:
    class Ticker:
        def __init__(self, _symbol: str) -> None:
            self.fast_info = {"currency": code}

    monkeypatch.setattr(importer_service.yf, "Ticker", Ticker)


@pytest.mark.parametrize(
    ("code", "currency"), [("USD", Currency.USD), ("BRL", Currency.BRL)]
)
def test_currency_is_read_from_yfinance(
    monkeypatch: pytest.MonkeyPatch, code: str, currency: Currency
) -> None:
    _yfinance_quoting_in(monkeypatch, code)
    assert importer_service.fetch_currency("AAPL") == currency


def test_other_currency_is_refused_with_the_reason(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _yfinance_quoting_in(monkeypatch, "GBp")
    with pytest.raises(UnprocessableEntityError, match="GBp"):
        importer_service.fetch_currency("VOD.L")


def _stub_pipeline(
    monkeypatch: pytest.MonkeyPatch, currencies: dict[str, Currency]
) -> list[tuple[str, float, Currency | None]]:
    """A fonte devolve um pregão de US$ 101; o que chega ao upsert fica na lista."""
    saved: list[tuple[str, float, Currency | None]] = []

    def upsert(
        df: pd.DataFrame,
        ticker: str,
        overwrite: bool = False,
        currency: Currency | None = None,
    ) -> None:
        saved.append((ticker, float(df["Close"].iloc[0]), currency))

    def fetch_currency(ticker: str) -> Currency:
        if ticker not in currencies:
            raise UnprocessableEntityError(f"{ticker} é cotado em GBp")
        return currencies[ticker]

    monkeypatch.setattr(importer_service, "fetch_currency", fetch_currency)
    monkeypatch.setattr(importer_service, "ptax_by_day", lambda: PTAX)
    monkeypatch.setattr(importer_service, "from_yfinance", lambda _t: _frame(DAYS[:1]))
    monkeypatch.setattr(importer_service, "upsert_dataframe", upsert)
    return saved


def test_single_update_converts_usd_and_keeps_brl(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    saved = _stub_pipeline(monkeypatch, {"AAPL": Currency.USD, "PETR4": Currency.BRL})
    importer_service.update_from_yfinance("AAPL")
    importer_service.update_from_yfinance("PETR4")
    assert saved == [
        ("AAPL", 494.9, Currency.USD),
        ("PETR4", 101.0, Currency.BRL),
    ]


def test_batch_skips_the_ticker_in_another_currency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    saved = _stub_pipeline(monkeypatch, {"AAPL": Currency.USD})
    batch: dict[str, Any] = {"AAPL": _frame(DAYS[:1]), "VOD.L": _frame(DAYS[:1])}
    monkeypatch.setattr(importer_service, "from_yfinance_batch", lambda _t: batch)
    importer_service.update_from_yfinance_batch(["AAPL", "VOD.L"])
    assert saved == [("AAPL", 494.9, Currency.USD)]


def test_reimport_with_another_currency_rewrites_the_whole_history(
    database: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(importer_service, "fetch_info", lambda _ticker: {})
    repository.stock.add_stock("AAPL", "Apple", AssetClass.STOCK)

    # Importada como real antes de a moeda existir: R$ 101 por ação
    importer_service.upsert_dataframe(_frame(DAYS), "AAPL")
    # A moeda lida agora é dólar: o histórico já convertido substitui o antigo
    importer_service.upsert_dataframe(
        to_brl(_frame(DAYS), Currency.USD, PTAX), "AAPL", currency=Currency.USD
    )

    stock = repository.stock.get_by_ticker("AAPL")
    assert stock is not None
    assert repository.stock.get_currency("AAPL") is Currency.USD
    history = repository.stock.get_real_history(stock.id)
    assert [row.close for row in history] == [494.9, 494.9, 494.9, 505.0]


def test_csv_keeps_the_stored_currency(
    database: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(importer_service, "fetch_info", lambda _ticker: {})
    repository.stock.add_stock("AAPL", "Apple", AssetClass.STOCK, Currency.USD)

    importer_service.upsert_dataframe(_frame(DAYS[:1]), "AAPL")

    assert repository.stock.get_currency("AAPL") is Currency.USD


def test_ptax_is_the_sgs_dollar_series_from_the_real() -> None:
    source = INDICATOR_SOURCES[IndicatorSeries.PTAX]
    assert (source.first_date, source.fetch.func, source.fetch.args) == (  # type: ignore[attr-defined]
        date(1994, 7, 1),
        fetch_sgs,
        (1,),
    )
