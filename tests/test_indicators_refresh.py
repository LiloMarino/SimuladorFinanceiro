from __future__ import annotations

from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.fetch_log import FetchLogDTO
from backend.core.enum import IndicatorSeries
from backend.features.import_data import indicators
from backend.features.import_data.indicators import refresh_indicators

CDI = IndicatorSeries.CDI


class FakeEconomicStore:
    """Banco de indicadores em memória: último dia guardado, linhas e tentativas."""

    def __init__(self) -> None:
        self.last_date: date | None = None
        self.saved: list[tuple[date, Decimal]] = []
        self.log: FetchLogDTO | None = None

    def get_last_real_date(self, series: IndicatorSeries) -> date | None:
        return self.last_date

    def save_history(self, series: IndicatorSeries, rows) -> None:
        self.saved += rows

    def get_fetch_log(self, series: IndicatorSeries) -> FetchLogDTO | None:
        return self.log

    def save_fetch_attempt(self, series, attempted_at, succeeded) -> None:
        self.log = FetchLogDTO(
            series=series,
            attempted_at=attempted_at,
            succeeded_at=attempted_at
            if succeeded
            else (self.log.succeeded_at if self.log else None),
        )


@pytest.fixture
def store(monkeypatch: pytest.MonkeyPatch) -> FakeEconomicStore:
    fake = FakeEconomicStore()
    for name in (
        "get_last_real_date",
        "save_history",
        "get_fetch_log",
        "save_fetch_attempt",
    ):
        monkeypatch.setattr(repository.economic, name, getattr(fake, name))
    return fake


@pytest.fixture
def fetched(monkeypatch: pytest.MonkeyPatch) -> list[tuple[date, date]]:
    """Troca a busca do CDI por uma que registra o período e devolve uma linha."""
    calls: list[tuple[date, date]] = []

    def fetch(start: date, end: date) -> list[tuple[date, Decimal]]:
        calls.append((start, end))
        return [(start, Decimal("0.04"))]

    source = indicators.INDICATOR_SOURCES[CDI]
    monkeypatch.setitem(indicators.INDICATOR_SOURCES, CDI, replace(source, fetch=fetch))
    return calls


def test_first_load_fetches_the_whole_series(store, fetched):
    """Sem dado guardado, a busca começa no primeiro dia da série."""
    refresh_indicators([CDI])

    assert fetched[0][0] == date(1986, 3, 6)
    assert store.saved == [(date(1986, 3, 6), Decimal("0.04"))]


def test_incremental_fetch_starts_on_the_first_day_of_the_month(store, fetched):
    """Com dado guardado, recomeça no dia 1 do mês do último valor."""
    store.last_date = date(2024, 5, 17)

    refresh_indicators([CDI])

    assert fetched[0][0] == date(2024, 5, 1)


def test_recent_attempt_is_skipped_unless_forced(store, fetched):
    """Tentativa há menos de 6 horas pula a série; `force` busca mesmo assim."""
    store.log = FetchLogDTO(
        series=CDI,
        attempted_at=datetime.now(UTC) - timedelta(hours=1),
        succeeded_at=None,
    )

    refresh_indicators([CDI])
    assert fetched == []

    refresh_indicators([CDI], force=True)
    assert len(fetched) == 1


def test_failure_records_the_attempt_and_keeps_the_data(store, monkeypatch):
    """Falha na busca registra a tentativa sem sucesso e não grava nada."""

    def broken(start: date, end: date):
        raise TimeoutError

    source = indicators.INDICATOR_SOURCES[CDI]
    monkeypatch.setitem(
        indicators.INDICATOR_SOURCES, CDI, replace(source, fetch=broken)
    )

    failed = refresh_indicators([CDI])

    assert failed == [CDI]
    assert store.saved == []
    assert store.log is not None and store.log.succeeded_at is None


def quarters(values: list[str]) -> list[tuple[date, Decimal]]:
    """Índice trimestral datado no dia 1 de cada trimestre, a partir de 2019."""
    return [
        (date(2019 + i // 4, 1 + 3 * (i % 4), 1), Decimal(v))
        for i, v in enumerate(values)
    ]


def test_gdp_growth_compares_the_last_four_quarters_with_the_four_before():
    index = quarters(["100", "100", "100", "100", "102", "103", "104", "105"])

    (growth,) = indicators.gdp_growth(index)

    # (102 + 103 + 104 + 105) ÷ 400 - 1 = 3,5%, no trimestre que fecha a conta
    assert growth == (date(2020, 10, 1), Decimal("3.50"))


def test_gdp_growth_fetches_the_whole_index_and_keeps_from_the_start(monkeypatch):
    asked: list[date] = []

    def fake_sgs(code: int, start: date, end: date):
        asked.append(start)
        return quarters(["100"] * 4 + ["101"] * 6)

    monkeypatch.setattr(indicators, "fetch_sgs", fake_sgs)

    rows = indicators.fetch_gdp_growth(date(2021, 1, 1), date(2021, 12, 31))

    assert asked == [indicators.GDP_INDEX_START]
    assert [day for day, _ in rows] == [date(2021, 1, 1), date(2021, 4, 1)]
