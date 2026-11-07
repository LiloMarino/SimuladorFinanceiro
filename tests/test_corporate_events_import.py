"""Preço bruto, desdobramentos e dividendos que a importação grava."""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest
from sqlalchemy import Engine

from backend.core import repository
from backend.core.enum import AssetClass, CorporateEventKind, DataOrigin
from backend.core.models.models import StockPriceHistory
from backend.features.import_data import importer_service
from backend.features.import_data.corporate_events import (
    events_from_frame,
    to_raw_prices,
)


def _frame(
    days: list[str],
    closes: list[float],
    splits: list[float] | None = None,
    dividends: list[float] | None = None,
    volume: int = 1000,
) -> pd.DataFrame:
    size = len(days)
    return pd.DataFrame(
        {
            "Open": closes,
            "High": closes,
            "Low": closes,
            "Close": closes,
            "Volume": [volume] * size,
            "Dividends": dividends or [0.0] * size,
            "Stock Splits": splits or [0.0] * size,
        },
        index=pd.to_datetime(days),
    )


DAYS = ["2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]


def test_split_brings_the_older_prices_back_to_what_was_traded() -> None:
    # Ajustado por um 2:1 em 04/01: o pregão de 04/01 em diante já é o preço negociado
    adjusted = _frame(
        DAYS,
        [5.0, 5.5, 6.0, 6.5],
        splits=[0.0, 0.0, 2.0, 0.0],
        dividends=[0.0, 0.1, 0.0, 0.0],
    )

    raw = to_raw_prices(adjusted)

    assert raw["Close"].tolist() == [10.0, 11.0, 6.0, 6.5]
    # O dividendo de antes do desdobramento também volta ao valor pago na época
    assert raw["Dividends"].tolist() == [0.0, 0.2, 0.0, 0.0]
    # O mesmo valor negociado vira metade das cotas antes do desdobramento
    assert raw["Volume"].tolist() == [500, 500, 1000, 1000]


def test_reverse_split_multiplies_by_the_inverse_ratio() -> None:
    # Grupamento 10:1 (razão 0,1): antes dele o preço bruto era um décimo
    adjusted = _frame(DAYS, [50.0, 51.0, 52.0, 53.0], splits=[0.0, 0.0, 0.1, 0.0])

    raw = to_raw_prices(adjusted)

    assert raw["Close"].tolist() == [5.0, 5.1, 52.0, 53.0]
    assert raw["Volume"].tolist() == [10_000, 10_000, 1000, 1000]


def test_two_splits_compound_for_the_oldest_days() -> None:
    adjusted = _frame(DAYS, [2.0, 3.0, 6.0, 7.0], splits=[0.0, 2.0, 0.0, 0.0])
    adjusted.loc["2024-01-04", "Stock Splits"] = 3.0

    raw = to_raw_prices(adjusted)

    assert raw["Close"].tolist() == [12.0, 9.0, 6.0, 7.0]


def test_frame_without_split_and_csv_stay_as_they_came() -> None:
    quiet = _frame(DAYS, [10.0, 10.1, 10.2, 10.3], dividends=[0.0, 0.0, 0.3, 0.0])
    assert to_raw_prices(quiet)["Close"].tolist() == quiet["Close"].tolist()

    csv = quiet.drop(columns=["Dividends", "Stock Splits"])
    assert to_raw_prices(csv) is csv
    assert events_from_frame(csv, 1) == []


def test_events_list_splits_and_dividends_by_ex_date() -> None:
    raw = to_raw_prices(
        _frame(
            DAYS,
            [5.0, 5.5, 6.0, 6.5],
            splits=[0.0, 0.0, 2.0, 0.0],
            dividends=[0.0, 0.1, 0.0, 0.05],
        )
    )

    events = events_from_frame(raw, 7)

    assert [(e.ex_date, e.kind, e.value) for e in events] == [
        (date(2024, 1, 3), CorporateEventKind.DIVIDEND, 0.2),
        (date(2024, 1, 4), CorporateEventKind.SPLIT, 2.0),
        (date(2024, 1, 5), CorporateEventKind.DIVIDEND, 0.05),
    ]


def test_import_stores_raw_prices_and_real_events(
    database: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(importer_service, "fetch_info", lambda _ticker: {})
    repository.stock.add_stock("BBAS3", "Banco do Brasil", AssetClass.STOCK)
    adjusted = _frame(
        DAYS, [5.0, 5.5, 6.0, 6.5], splits=[0.0, 0.0, 2.0, 0.0], dividends=[0.1] * 4
    )

    importer_service.upsert_dataframe(to_raw_prices(adjusted), "BBAS3")

    stock = repository.stock.get_by_ticker("BBAS3")
    assert stock is not None
    assert [r.close for r in repository.stock.get_real_history(stock.id)] == [
        10.0,
        11.0,
        6.0,
        6.5,
    ]
    events = repository.corporate_event.get_real()
    assert [(e.kind, e.value) for e in events if e.ex_date == date(2024, 1, 4)] == [
        (CorporateEventKind.SPLIT, 2.0),
        (CorporateEventKind.DIVIDEND, 0.1),
    ]


def test_new_split_in_an_incremental_import_does_not_look_like_an_error(
    database: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    """O preço que cai a um terço no dia do 3:1 é mercado, não erro da fonte."""
    monkeypatch.setattr(importer_service, "fetch_info", lambda _ticker: {})
    stock = repository.stock.add_stock("VALE3", "Vale", AssetClass.STOCK)
    repository.stock.save_real_prices(
        stock.id,
        [
            StockPriceHistory(
                stock_id=stock.id,
                price_date=date(2024, 1, 2),
                open=30.0,
                high=30.0,
                low=30.0,
                close=30.0,
                volume=100,
                origin=DataOrigin.REAL.value,
            )
        ],
    )
    adjusted = _frame(
        ["2024-01-02", "2024-01-03", "2024-01-04"],
        [10.0, 10.2, 10.4],
        splits=[0.0, 3.0, 0.0],
    )

    importer_service.upsert_dataframe(to_raw_prices(adjusted), "VALE3")

    history = repository.stock.get_real_history(stock.id)
    # Dia corrigido pela fonte teria o volume zerado
    assert [(r.close, r.volume) for r in history] == [
        (30.0, 100),
        (10.2, 1000),
        (10.4, 1000),
    ]


def test_events_land_even_when_the_prices_are_already_up_to_date(
    database: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(importer_service, "fetch_info", lambda _ticker: {})
    frame = _frame(DAYS, [10.0, 10.1, 10.2, 10.3])
    importer_service.upsert_dataframe(frame, "ITUB4")
    assert repository.corporate_event.get_real() == []

    with_dividend = _frame(
        DAYS, [10.0, 10.1, 10.2, 10.3], dividends=[0.0, 0.0, 0.4, 0.0]
    )
    importer_service.upsert_dataframe(with_dividend, "ITUB4")

    assert [(e.ex_date, e.value) for e in repository.corporate_event.get_real()] == [
        (date(2024, 1, 4), 0.4)
    ]


def test_crypto_never_gets_events(
    database: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(importer_service, "fetch_info", lambda _ticker: {})
    repository.stock.add_stock("BTC-USD", "Bitcoin", AssetClass.CRYPTO)
    frame = _frame(DAYS, [10.0, 10.1, 10.2, 10.3], dividends=[0.0, 0.0, 0.4, 0.0])

    importer_service.upsert_dataframe(frame, "BTC-USD")

    assert repository.corporate_event.get_real() == []
