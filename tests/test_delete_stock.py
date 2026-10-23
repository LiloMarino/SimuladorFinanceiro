"""Exclusão de ativo na Central de dados: o que sai do banco e quando a rota recusa."""

from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from backend.core import repository
from backend.core.dto.sector import StockSegmentDTO
from backend.core.dto.ticker_profile import TickerProfileDTO
from backend.core.enum import AssetClass, DataOrigin
from backend.core.exceptions.http_exceptions import ConflictError, NotFoundError
from backend.core.models.models import (
    Sectors,
    StockPriceHistory,
    TickerProfile,
)
from backend.routes import importer as importer_routes
from backend.routes.importer import delete_stock

BANKS = StockSegmentDTO(sector="Financeiro", segment="Bancos")
OIL = StockSegmentDTO(sector="Petróleo, Gás e Biocombustíveis", segment="Petróleo")


def _count(engine: Engine, model: type) -> int:
    with Session(engine) as session:
        return session.execute(select(func.count()).select_from(model)).scalar_one()


def _price(stock_id: int, version: int) -> StockPriceHistory:
    return StockPriceHistory(
        stock_id=stock_id,
        price_date=date(2020, 1, 2),
        open=10,
        high=11,
        low=9,
        close=10,
        volume=100,
        origin=DataOrigin.REAL.value,
        version=version,
    )


def test_delete_drops_every_version_profile_and_orphan_sector(
    database: Engine,
) -> None:
    broken = repository.stock.add_stock("BUGA3", "Bugada", AssetClass.STOCK)
    kept = repository.stock.add_stock("ITUB4", "Itaú", AssetClass.STOCK)
    repository.stock.classify("BUGA3", OIL)
    repository.stock.classify("ITUB4", BANKS)
    repository.stock.save_real_prices(broken.id, [_price(broken.id, 0)])
    repository.stock.save_real_prices(kept.id, [_price(kept.id, 0)])
    # Cópia congelada de uma partida salva
    with Session(database) as session, session.begin():
        session.add(_price(broken.id, 7))
    repository.stock.save_ticker_profile(
        TickerProfileDTO(
            ticker="BUGA3", name=None, quote_type=None, sector=None, industry=None
        )
    )

    assert repository.stock.delete("BUGA3") is True

    assert repository.stock.get_by_ticker("BUGA3") is None
    assert repository.stock.get_by_ticker("ITUB4") is not None
    # Sobra só o histórico do ativo que ficou
    assert _count(database, StockPriceHistory) == 1
    assert _count(database, TickerProfile) == 0
    # O setor do ativo apagado sai; o do ativo que ficou permanece
    assert [s.name for s in repository.stock.get_sectors()] == ["Financeiro"]
    assert _count(database, Sectors) == 1


def test_delete_unknown_ticker_returns_false(database: Engine) -> None:
    assert repository.stock.delete("XXXX3") is False


@pytest.fixture
def route_repository(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Os códigos que o repositório apagou; só BUGA3 existe e está em 2 partidas salvas."""
    deleted: list[str] = []
    stock = importer_routes.repository.stock
    monkeypatch.setattr(
        stock,
        "get_by_ticker",
        lambda ticker: object() if ticker in ("BUGA3", "LIVRE3") else None,
    )
    monkeypatch.setattr(
        stock, "count_simulations_trading", lambda ticker: 2 if ticker == "BUGA3" else 0
    )
    monkeypatch.setattr(stock, "delete", lambda ticker: deleted.append(ticker) or True)
    return deleted


def test_route_deletes_a_free_stock(route_repository: list[str]) -> None:
    delete_stock("LIVRE3")

    assert route_repository == ["LIVRE3"]


def test_route_refuses_a_stock_traded_in_saved_matches(
    route_repository: list[str],
) -> None:
    with pytest.raises(ConflictError, match="2 partidas salvas"):
        delete_stock("BUGA3")

    assert route_repository == []


def test_route_unknown_ticker_is_not_found(route_repository: list[str]) -> None:
    with pytest.raises(NotFoundError):
        delete_stock("XXXX3")
