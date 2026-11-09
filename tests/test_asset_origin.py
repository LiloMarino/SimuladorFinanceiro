"""A origem do ativo (nacional ou internacional): inferida na importação e trocada na Central de dados."""

from __future__ import annotations

import pandas as pd
import pytest
from sqlalchemy import Engine

from backend.core import repository
from backend.core.enum import AssetClass, AssetOrigin, Currency
from backend.features.import_data import importer_service
from backend.features.import_data.importer_service import infer_origin
from backend.routes import importer


@pytest.mark.parametrize(
    ("asset_class", "currency", "origin"),
    [
        (AssetClass.STOCK, Currency.BRL, AssetOrigin.DOMESTIC),
        (AssetClass.STOCK, None, AssetOrigin.DOMESTIC),
        (AssetClass.FII, Currency.BRL, AssetOrigin.DOMESTIC),
        (AssetClass.STOCK, Currency.USD, AssetOrigin.FOREIGN),
        (AssetClass.CRYPTO, Currency.USD, AssetOrigin.FOREIGN),
        (AssetClass.BDR, Currency.BRL, AssetOrigin.FOREIGN),
    ],
)
def test_only_the_dollar_and_the_bdr_class_are_inferred_as_foreign(
    asset_class: AssetClass, currency: Currency | None, origin: AssetOrigin
) -> None:
    assert infer_origin(asset_class, currency) is origin


def _frame() -> pd.DataFrame:
    days = ["2024-01-02", "2024-01-03"]
    return pd.DataFrame(
        {
            "Open": [10.0, 10.5],
            "High": [10.0, 10.5],
            "Low": [10.0, 10.5],
            "Close": [10.0, 10.5],
            "Volume": [1000, 1000],
            "Dividends": [0.0, 0.0],
            "Stock Splits": [0.0, 0.0],
        },
        index=pd.to_datetime(days),
    )


def test_a_new_asset_in_dollars_is_born_foreign_and_a_choice_survives_the_reimport(
    database: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(importer_service, "fetch_info", lambda _ticker: {})

    importer_service.upsert_dataframe(_frame(), "AAPL", currency=Currency.USD)
    importer_service.upsert_dataframe(_frame(), "PETR4")

    origins = repository.stock.get_origins()
    assert origins["AAPL"] is AssetOrigin.FOREIGN
    assert origins["PETR4"] is AssetOrigin.DOMESTIC

    # O host marca um ETF de índice de fora e reimporta: a escolha fica
    importer.update_asset_origin(
        "PETR4", importer.AssetOriginRequest(origin=AssetOrigin.FOREIGN)
    )
    importer_service.upsert_dataframe(_frame(), "PETR4", overwrite=True)

    assert repository.stock.get_origins()["PETR4"] is AssetOrigin.FOREIGN


def test_changing_the_origin_of_an_unknown_asset_is_not_found(database: Engine) -> None:
    with pytest.raises(Exception, match="não encontrado"):
        importer.update_asset_origin(
            "NOPE3", importer.AssetOriginRequest(origin=AssetOrigin.FOREIGN)
        )
