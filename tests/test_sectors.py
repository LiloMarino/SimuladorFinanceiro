"""Classificação das ações por setor e segmento: o que o banco guarda, o que o
importador sugere e como a carteira agrupa."""

from __future__ import annotations

from decimal import Decimal

import pandas as pd
import pytest
from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from backend.core import repository
from backend.core.dto.sector import StockSegmentDTO
from backend.core.dto.stock import StockDTO
from backend.core.enum import AssetClass
from backend.core.models.models import Sectors, Segments
from backend.core.sectors import allocate_by_sector
from backend.features.import_data import importer_service

BANKS = StockSegmentDTO(sector="Financeiro", segment="Bancos")
INSURANCE = StockSegmentDTO(sector="Financeiro", segment="Seguros")
OIL = StockSegmentDTO(sector="Petróleo, Gás e Biocombustíveis", segment="Petróleo")


def _count(engine: Engine, model: type) -> int:
    with Session(engine) as session:
        return session.execute(select(func.count()).select_from(model)).scalar_one()


def test_classify_reuses_names_and_drops_orphans(database: Engine) -> None:
    """Setor e segmento são criados pelo nome uma vez só; o que fica sem ação sai."""
    for ticker in ("ITUB4", "BBDC4", "PETR4"):
        repository.stock.add_stock(ticker, ticker, AssetClass.STOCK)

    repository.stock.classify("ITUB4", BANKS)
    repository.stock.classify("BBDC4", BANKS)
    repository.stock.classify("PETR4", OIL)
    assert (_count(database, Sectors), _count(database, Segments)) == (2, 2)
    assert repository.stock.get_classification()["BBDC4"] == BANKS

    # Petróleo perde a única ação: setor e segmento somem da lista de sugestões
    repository.stock.classify("PETR4", None)
    repository.stock.classify("BBDC4", INSURANCE)
    assert repository.stock.get_classification() == {
        "ITUB4": BANKS,
        "BBDC4": INSURANCE,
    }
    assert [(s.name, s.segments) for s in repository.stock.get_sectors()] == [
        ("Financeiro", ["Bancos", "Seguros"])
    ]


def test_classify_unknown_ticker_returns_none(database: Engine) -> None:
    assert repository.stock.classify("XXXX3", BANKS) is None


def test_suggestion_translates_yfinance_sector() -> None:
    assert importer_service.suggest_segment(
        {"sector": "Financial Services", "industry": "Banks - Regional"}
    ) == StockSegmentDTO(sector="Financeiro", segment="Banks - Regional")
    assert importer_service.suggest_segment({"sector": "Energy"}) == StockSegmentDTO(
        sector="Petróleo, Gás e Biocombustíveis", segment="Energy"
    )
    assert importer_service.suggest_segment({}) is None


@pytest.fixture
def import_calls(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, object]]:
    """Ação já existente sem preço novo a gravar; registra o que o importador faz."""
    calls: list[tuple[str, object]] = []
    monkeypatch.setattr(
        importer_service,
        "fetch_info",
        lambda ticker: (
            calls.append(("info", ticker))
            or {"sector": "Energy", "industry": "Oil & Gas Integrated"}
        ),
    )
    monkeypatch.setattr(
        repository.stock,
        "classify",
        lambda ticker, segment: calls.append(("classify", segment)),
    )
    monkeypatch.setattr(
        repository.stock, "get_last_stock_price_history", lambda _id: None
    )
    monkeypatch.setattr(repository.stock, "add_stock_price_history", lambda _rows: None)
    return calls


def _existing_stock(monkeypatch: pytest.MonkeyPatch, classified: bool) -> None:
    monkeypatch.setattr(
        repository.stock,
        "get_by_ticker",
        lambda ticker: StockDTO(
            id=1, ticker=ticker, name="Petrobras", asset_class=AssetClass.STOCK
        ),
    )
    monkeypatch.setattr(
        repository.stock,
        "get_classification",
        lambda: {"PETR4": OIL} if classified else {},
    )


def test_import_suggests_for_unclassified_stock(
    monkeypatch: pytest.MonkeyPatch, import_calls: list[tuple[str, object]]
) -> None:
    _existing_stock(monkeypatch, classified=False)
    importer_service.upsert_dataframe(pd.DataFrame(), "PETR4")
    assert import_calls == [
        ("info", "PETR4"),
        (
            "classify",
            StockSegmentDTO(
                sector="Petróleo, Gás e Biocombustíveis",
                segment="Oil & Gas Integrated",
            ),
        ),
    ]


def test_import_keeps_manual_classification(
    monkeypatch: pytest.MonkeyPatch, import_calls: list[tuple[str, object]]
) -> None:
    _existing_stock(monkeypatch, classified=True)
    importer_service.upsert_dataframe(pd.DataFrame(), "PETR4")
    assert import_calls == []


def test_allocation_groups_by_sector_with_unclassified() -> None:
    """Frações sobre o total da renda variável; ação sem classificação vira None."""
    sectors = allocate_by_sector(
        {
            "ITUB4": Decimal("500"),
            "BBSE3": Decimal("100"),
            "PETR4": Decimal("300"),
            "XPTO3": Decimal("100"),
        },
        {"ITUB4": BANKS, "BBSE3": INSURANCE, "PETR4": OIL},
    )

    assert [(s.sector, s.value, s.fraction) for s in sectors] == [
        ("Financeiro", Decimal("600"), Decimal("0.6")),
        ("Petróleo, Gás e Biocombustíveis", Decimal("300"), Decimal("0.3")),
        (None, Decimal("100"), Decimal("0.1")),
    ]
    assert [(s.segment, s.fraction) for s in sectors[0].segments] == [
        ("Bancos", Decimal("0.5")),
        ("Seguros", Decimal("0.1")),
    ]
