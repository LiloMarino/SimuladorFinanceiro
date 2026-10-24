"""Correção dos erros de dado na base já importada e na importação incremental."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import pytest
from sqlalchemy import Engine

from backend.core import repository
from backend.core.dto.import_settings import ImportSettingsDTO
from backend.core.enum import AssetClass, DataOrigin
from backend.core.models.models import StockPriceHistory
from backend.features.import_data import importer_service
from backend.features.import_data.coverage import get_series_coverage

FIRST_DAY = date(2024, 1, 2)


def _row(stock_id: int, offset: int, close: float) -> StockPriceHistory:
    return StockPriceHistory(
        stock_id=stock_id,
        price_date=FIRST_DAY + timedelta(days=offset),
        open=close,
        high=close,
        low=close,
        close=close,
        volume=500,
        origin=DataOrigin.REAL.value,
    )


def _closes(stock_id: int) -> list[float]:
    return [row.close for row in repository.stock.get_real_history(stock_id)]


def _coverage(ticker: str):
    return next(s for s in get_series_coverage() if s.key == ticker)


def test_stored_error_is_corrected_once_and_counted(database: Engine) -> None:
    stock = repository.stock.add_stock("CMIG4", "Cemig", AssetClass.STOCK)
    closes = [10.0, 10.0, 0.05, 12.0, 12.0]
    repository.stock.save_real_prices(
        stock.id, [_row(stock.id, i, c) for i, c in enumerate(closes)]
    )

    result = importer_service.correct_stored_prices()

    assert (result.corrected_days, result.stocks) == (1, 1)
    assert _closes(stock.id) == [10.0, 10.0, 11.0, 12.0, 12.0]
    corrected = repository.stock.get_real_history(stock.id)[2]
    assert corrected.volume == 0
    assert _coverage("CMIG4").corrected_days == 1

    # Reaplicar não encontra mais nada para corrigir
    again = importer_service.correct_stored_prices()
    assert (again.corrected_days, again.stocks) == (0, 0)
    assert _coverage("CMIG4").corrected_days == 1


def test_crypto_is_left_out_of_the_correction(database: Engine) -> None:
    coin = repository.stock.add_stock("DOGE-USD", "Dogecoin", AssetClass.CRYPTO)
    closes = [10.0, 10.0, 0.05, 12.0, 12.0]
    repository.stock.save_real_prices(
        coin.id, [_row(coin.id, i, c) for i, c in enumerate(closes)]
    )

    result = importer_service.correct_stored_prices()

    assert result.corrected_days == 0
    assert _closes(coin.id) == closes
    assert _coverage("DOGE-USD").corrected_days == 0


def test_incremental_import_uses_the_last_stored_close_as_anchor(
    database: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    stock = repository.stock.add_stock("UGPA3", "Ultrapar", AssetClass.STOCK)
    repository.stock.save_real_prices(stock.id, [_row(stock.id, 0, 10.0)])
    monkeypatch.setattr(importer_service, "fetch_info", lambda _ticker: {})
    incoming = pd.DataFrame(
        {
            "Open": [0.05, 10.2, 10.3],
            "High": [0.05, 10.2, 10.3],
            "Low": [0.05, 10.2, 10.3],
            "Close": [0.05, 10.2, 10.3],
            "Volume": [1, 1, 1],
        },
        index=pd.to_datetime(["2024-01-03", "2024-01-04", "2024-01-05"]),
    )

    importer_service.upsert_dataframe(incoming, "UGPA3")

    assert _closes(stock.id) == [10.0, 10.1, 10.2, 10.3]
    assert _coverage("UGPA3").corrected_days == 1


def test_import_setting_defaults_to_correcting_and_remembers_the_choice(
    database: Engine,
) -> None:
    assert repository.import_settings.get().correct_price_errors is True

    repository.import_settings.save(ImportSettingsDTO(correct_price_errors=False))
    assert repository.import_settings.get().correct_price_errors is False

    repository.import_settings.save(ImportSettingsDTO(correct_price_errors=True))
    assert repository.import_settings.get().correct_price_errors is True


def test_import_with_the_correction_off_keeps_the_source_prices(
    database: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    stock = repository.stock.add_stock("GOAU4", "Gerdau", AssetClass.STOCK)
    monkeypatch.setattr(importer_service, "fetch_info", lambda _ticker: {})
    repository.import_settings.save(ImportSettingsDTO(correct_price_errors=False))
    incoming = pd.DataFrame(
        {col: [10.0, 0.05, 10.0] for col in ("Open", "High", "Low", "Close")}
        | {"Volume": [1, 1, 1]},
        index=pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"]),
    )

    importer_service.upsert_dataframe(incoming, "GOAU4")

    assert _closes(stock.id) == [10.0, 0.05, 10.0]
    assert _coverage("GOAU4").corrected_days == 0
