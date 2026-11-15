"""Marcação de estatal na importação: banco, rotas, sugestão e cópia para a partida."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, ClassVar

import pytest
from pydantic import ValidationError
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from backend.core import repository
from backend.core.dto.sector import StockSegmentDTO
from backend.core.dto.state_company import StateOwnedStockRequest
from backend.core.enum import (
    AssetClass,
    StateCompanyOrigin,
    StateCompanyStatus,
    StateLever,
)
from backend.core.exceptions.http_exceptions import NotFoundError
from backend.core.models.models import StateCompanies, StateOwnedStocks
from backend.features.import_data import importer_service
from backend.routes.importer import (
    get_segment_suggestion,
    mark_state_owned,
    unmark_state_owned,
)
from tests.fakes import simulation_settings

PETR = StateOwnedStockRequest(
    government_share=Decimal("0.36"), shares=13_000_000_000, lever=StateLever.FUEL
)


def _petr() -> None:
    repository.stock.add_stock("PETR4", "Petrobras", AssetClass.STOCK)


def test_mark_stores_and_reads_back(database: Engine) -> None:
    _petr()

    mark = repository.state_company.mark("PETR4", PETR)

    assert mark is not None
    assert mark.ticker == "PETR4"
    assert repository.state_company.get_mark("PETR4") == mark
    assert repository.state_company.marks() == [mark]


def test_mark_again_replaces_the_previous_mark(database: Engine) -> None:
    _petr()
    repository.state_company.mark("PETR4", PETR)

    repository.state_company.mark(
        "PETR4",
        StateOwnedStockRequest(government_share=Decimal("0.5"), shares=1000),
    )

    marks = repository.state_company.marks()
    assert len(marks) == 1
    assert marks[0].government_share == Decimal("0.5")
    assert marks[0].shares == 1000
    assert marks[0].lever is None


def test_mark_unknown_ticker_returns_none(database: Engine) -> None:
    assert repository.state_company.mark("XXXX3", PETR) is None


def test_unmark_removes_only_that_stock(database: Engine) -> None:
    _petr()
    repository.stock.add_stock("BBAS3", "Banco do Brasil", AssetClass.STOCK)
    repository.state_company.mark("PETR4", PETR)
    repository.state_company.mark("BBAS3", PETR)

    assert repository.state_company.unmark("PETR4") is True
    assert repository.state_company.unmark("PETR4") is False
    assert [m.ticker for m in repository.state_company.marks()] == ["BBAS3"]


def test_deleting_the_stock_drops_its_mark(database: Engine) -> None:
    _petr()
    repository.state_company.mark("PETR4", PETR)

    repository.stock.delete("PETR4")

    assert repository.state_company.marks() == []


@pytest.mark.parametrize(
    "values",
    [
        {"government_share": Decimal(0), "shares": 10},
        {"government_share": Decimal("1.1"), "shares": 10},
        {"government_share": Decimal("0.5"), "shares": 0},
    ],
)
def test_request_rejects_out_of_range_values(values: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        StateOwnedStockRequest(**values)


def test_copy_marks_opens_the_imported_companies_of_the_match(
    database: Engine,
) -> None:
    _petr()
    repository.stock.add_stock("BBAS3", "Banco do Brasil", AssetClass.STOCK)
    repository.stock.add_stock("VALE3", "Vale", AssetClass.STOCK)
    repository.state_company.mark("PETR4", PETR)
    repository.state_company.mark(
        "BBAS3",
        StateOwnedStockRequest(
            government_share=Decimal("0.5"), shares=2_000, lever=StateLever.BANK
        ),
    )
    simulation_id = repository.simulation.create_simulation(simulation_settings())

    assert repository.state_company.copy_marks(simulation_id) == 2

    companies = {
        c.ticker: c for c in repository.state_company.of_simulation(simulation_id)
    }
    assert set(companies) == {"PETR4", "BBAS3"}
    petr = companies["PETR4"]
    assert petr.origin is StateCompanyOrigin.IMPORTED
    assert petr.status is StateCompanyStatus.ACTIVE
    assert petr.lever is StateLever.FUEL
    assert petr.government_share == Decimal("0.36")
    assert petr.shares == 13_000_000_000
    assert petr.invested == 0


def test_the_match_keeps_its_copy_when_the_base_mark_changes(
    database: Engine,
) -> None:
    _petr()
    repository.state_company.mark("PETR4", PETR)
    simulation_id = repository.simulation.create_simulation(simulation_settings())
    repository.state_company.copy_marks(simulation_id)

    repository.state_company.unmark("PETR4")

    assert [
        c.ticker for c in repository.state_company.of_simulation(simulation_id)
    ] == ["PETR4"]
    with Session(database) as session:
        assert session.execute(select(StateOwnedStocks)).first() is None
        assert session.execute(select(StateCompanies)).first() is not None


def test_copy_marks_is_empty_without_marks(database: Engine) -> None:
    simulation_id = repository.simulation.create_simulation(simulation_settings())

    assert repository.state_company.copy_marks(simulation_id) == 0
    assert repository.state_company.of_simulation(simulation_id) == []


def test_routes_mark_and_unmark(database: Engine) -> None:
    _petr()

    mark_state_owned("PETR4", PETR)
    assert repository.state_company.get_mark("PETR4") is not None

    unmark_state_owned("PETR4")
    assert repository.state_company.get_mark("PETR4") is None


def test_routes_answer_not_found_for_unknown_ticker(database: Engine) -> None:
    with pytest.raises(NotFoundError):
        mark_state_owned("XXXX3", PETR)
    with pytest.raises(NotFoundError):
        unmark_state_owned("XXXX3")


@pytest.mark.parametrize(
    ("segment", "lever"),
    [
        (
            StockSegmentDTO(
                sector="Petróleo, Gás e Biocombustíveis", segment="Oil & Gas Integrated"
            ),
            StateLever.FUEL,
        ),
        (
            StockSegmentDTO(
                sector="Utilidade Pública", segment="Utilities - Regulated Electric"
            ),
            StateLever.ENERGY,
        ),
        (
            StockSegmentDTO(sector="Financeiro", segment="Banks - Regional"),
            StateLever.BANK,
        ),
        (StockSegmentDTO(sector="Saúde", segment="Biotechnology"), None),
    ],
)
def test_lever_suggestion_follows_sector_and_segment(
    segment: StockSegmentDTO, lever: StateLever | None
) -> None:
    assert importer_service.suggest_lever(segment) is lever


class FakeTicker:
    info: ClassVar[dict[str, Any]] = {}
    calls = 0


@pytest.fixture
def source(monkeypatch: pytest.MonkeyPatch) -> type[FakeTicker]:
    """O yfinance trocado por um que conta as consultas e devolve o `info`."""
    FakeTicker.calls = 0

    class Ticker:
        def __init__(self, _ticker: str) -> None:
            FakeTicker.calls += 1

        @property
        def info(self) -> dict[str, Any]:
            return FakeTicker.info

    monkeypatch.setattr(importer_service.yf, "Ticker", Ticker)
    return FakeTicker


def test_fetched_profile_records_shares_outstanding(
    database: Engine, source: type[FakeTicker]
) -> None:
    source.info = {
        "longName": "Petrobras",
        "sector": "Energy",
        "industry": "Oil & Gas Integrated",
        "sharesOutstanding": 12_900_000_000.0,
    }

    importer_service.fetch_info("PETR4")

    stored = repository.stock.get_ticker_profile("PETR4")
    assert stored is not None
    assert stored.shares_outstanding == 12_900_000_000


def test_profile_without_shares_stores_none(
    database: Engine, source: type[FakeTicker]
) -> None:
    source.info = {"sector": "Energy"}

    importer_service.fetch_info("PETR4")

    stored = repository.stock.get_ticker_profile("PETR4")
    assert stored is not None
    assert stored.shares_outstanding is None


def test_suggestion_route_brings_shares_and_lever(
    database: Engine, source: type[FakeTicker]
) -> None:
    source.info = {
        "sector": "Energy",
        "industry": "Oil & Gas Integrated",
        "sharesOutstanding": 12_900_000_000,
    }

    suggestion = get_segment_suggestion("PETR4")

    assert suggestion is not None
    assert suggestion.sector == "Petróleo, Gás e Biocombustíveis"
    assert suggestion.segment == "Oil & Gas Integrated"
    assert suggestion.shares_outstanding == 12_900_000_000
    assert suggestion.lever is StateLever.FUEL


def test_suggestion_is_none_when_the_source_does_not_know_the_sector(
    database: Engine, source: type[FakeTicker]
) -> None:
    source.info = {"quoteType": "ETF"}

    assert get_segment_suggestion("BOVA11") is None
