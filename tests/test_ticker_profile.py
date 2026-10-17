"""Sugestão de código ao digitar o ativo e cache do perfil do yfinance."""

from __future__ import annotations

from typing import Any, ClassVar

import pytest
from sqlalchemy import Engine

from backend.core import repository
from backend.core.dto.ticker_profile import TickerProfileDTO
from backend.core.exceptions.http_exceptions import (
    BadGatewayError,
    ServiceUnavailableError,
)
from backend.features.import_data import importer_service


class FakeSearch:
    quotes: ClassVar[list[dict[str, Any]]] = []
    calls: ClassVar[list[str]] = []

    def __init__(self, query: str, **_kwargs: object) -> None:
        FakeSearch.calls.append(query)


@pytest.fixture
def search(monkeypatch: pytest.MonkeyPatch) -> type[FakeSearch]:
    FakeSearch.quotes = []
    FakeSearch.calls = []
    monkeypatch.setattr(importer_service.yf, "Search", FakeSearch)
    return FakeSearch


def _quote(symbol: str, name: str, exchange: str = "SAO") -> dict[str, Any]:
    return {"symbol": symbol, "longname": name, "exchange": exchange}


def test_search_below_two_characters_does_not_query_the_source(
    search: type[FakeSearch],
) -> None:
    """Com menos de 2 caracteres a busca devolve vazio sem consultar o yfinance."""
    assert importer_service.search_tickers(" P ") == []
    assert search.calls == []


def test_search_keeps_only_b3_tickers_without_repeats(
    search: type[FakeSearch],
) -> None:
    """Fica só o código da B3 (bolsa SAO, final .SA, formato PETR4/KNRI11), sem o .SA, sem repetidos e na ordem do Yahoo."""
    search.quotes = [
        _quote("PETR4.SA", "Petróleo Brasileiro S.A."),
        _quote("PETR4.SA", "Repetido"),
        _quote("AAPL", "Apple", exchange="NMS"),
        _quote("BTC-USD", "Bitcoin", exchange="CCC"),
        _quote("PETR4.L", "Outra bolsa"),
        _quote("PETRO.SA", "Sem número da classe"),
        _quote("KNRI11.SA", "Kinea Renda Imobiliária"),
    ]
    result = importer_service.search_tickers("petr")
    assert [(s.ticker, s.name) for s in result] == [
        ("PETR4", "Petróleo Brasileiro S.A."),
        ("KNRI11", "Kinea Renda Imobiliária"),
    ]


def test_search_source_failure_becomes_service_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Falha do yfinance na busca vira 503, para o front deixar o texto digitado valer."""

    def boom(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("sem rede")

    monkeypatch.setattr(importer_service.yf, "Search", boom)
    with pytest.raises(ServiceUnavailableError):
        importer_service.search_tickers("petr")


class FakeTicker:
    info: ClassVar[dict[str, Any] | Exception] = {}
    calls = 0


@pytest.fixture
def source(monkeypatch: pytest.MonkeyPatch) -> type[FakeTicker]:
    """O yfinance trocado por um que conta as consultas e devolve (ou levanta) o `info`."""
    FakeTicker.calls = 0

    class Ticker:
        def __init__(self, _ticker: str) -> None:
            FakeTicker.calls += 1

        @property
        def info(self) -> dict[str, Any]:
            if isinstance(FakeTicker.info, Exception):
                raise FakeTicker.info
            return FakeTicker.info

    monkeypatch.setattr(importer_service.yf, "Ticker", Ticker)
    return FakeTicker


def test_profile_is_fetched_once_then_read_from_the_table(
    database: Engine, source: type[FakeTicker]
) -> None:
    """A segunda leitura usa a linha guardada e não vai ao yfinance."""
    source.info = {
        "longName": "Petrobras",
        "quoteType": "EQUITY",
        "sector": "Energy",
        "industry": "Oil & Gas Integrated",
    }
    first = importer_service.fetch_info("PETR4")
    second = importer_service.fetch_info("PETR4")
    assert first == second
    assert second["sector"] == "Energy"
    assert second["longName"] == "Petrobras"
    assert source.calls == 1


def test_empty_response_is_stored_so_it_is_not_asked_again(
    database: Engine, source: type[FakeTicker]
) -> None:
    """O ETF que o yfinance devolve sem setor também fica guardado, e não é reconsultado."""
    source.info = {"quoteType": "ETF"}
    assert importer_service.fetch_info("BOVA11")["sector"] is None
    importer_service.fetch_info("BOVA11")
    assert source.calls == 1


def test_source_failure_stores_nothing(
    database: Engine, source: type[FakeTicker]
) -> None:
    """Se o yfinance falhar, nada é gravado e a próxima leitura tenta de novo."""
    source.info = RuntimeError("sem rede")
    assert importer_service.fetch_info("PETR4") == {}
    assert repository.stock.get_ticker_profile("PETR4") is None
    source.info = {"sector": "Energy"}
    assert importer_service.fetch_info("PETR4")["sector"] == "Energy"
    assert source.calls == 2


def test_refresh_replaces_the_stored_profile(
    database: Engine, source: type[FakeTicker]
) -> None:
    """Atualizar o perfil refaz a consulta e troca a linha guardada."""
    repository.stock.save_ticker_profile(
        TickerProfileDTO(
            ticker="PETR4", name=None, quote_type=None, sector=None, industry=None
        )
    )
    source.info = {"longName": "Petrobras", "sector": "Energy"}
    importer_service.refresh_profile("PETR4")
    profile = repository.stock.get_ticker_profile("PETR4")
    assert profile is not None
    assert (profile.name, profile.sector) == ("Petrobras", "Energy")


def test_refresh_source_failure_becomes_bad_gateway(
    database: Engine, source: type[FakeTicker]
) -> None:
    """Falha do yfinance ao atualizar vira 502 e o perfil guardado fica como estava."""
    repository.stock.save_ticker_profile(
        TickerProfileDTO(
            ticker="PETR4",
            name="Petrobras",
            quote_type=None,
            sector="Energy",
            industry=None,
        )
    )
    source.info = RuntimeError("sem rede")
    with pytest.raises(BadGatewayError):
        importer_service.refresh_profile("PETR4")
    profile = repository.stock.get_ticker_profile("PETR4")
    assert profile is not None
    assert profile.sector == "Energy"
