"""Cotações em lote: limites por ativo, corte temporal e número de consultas."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import Engine, event
from sqlalchemy.orm import Session

from backend.core import repository
from backend.core.models.models import Stock, StockPriceHistory
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.simulation.simulation import Simulation
from backend.features.simulation.simulation_engine import SimulationEngine
from backend.features.variable_income.price_impact import PriceImpact

TODAY = date(2020, 1, 8)


def _price(stock_id: int, day: int, opening: float, close: float) -> StockPriceHistory:
    return StockPriceHistory(
        stock_id=stock_id,
        price_date=date(2020, 1, day),
        open=opening,
        high=max(opening, close),
        low=min(opening, close),
        close=close,
        volume=1000 + day,
    )


@pytest.fixture
def quotes(database: Engine) -> Engine:
    with Session(database) as session:
        stocks = [
            Stock(ticker=ticker, name=ticker, asset_class=asset_class)
            for ticker, asset_class in [
                ("ZETA3", "STOCK"),
                ("ALFA11", "FII"),
                ("FUTR3", "STOCK"),
                ("NONE3", "STOCK"),
                ("ZERO11", "ETF"),
            ]
        ]
        session.add_all(stocks)
        session.flush()
        # Inserção fora da ordem das datas: a consulta deve ordenar, não o banco.
        session.add_all(
            [
                _price(stocks[0].id, 10, 50, 60),
                _price(stocks[0].id, 8, 12, 10.25),
                _price(stocks[0].id, 2, 8, 9),
                _price(stocks[0].id, 6, 10, 12),
                _price(stocks[1].id, 6, 20, 20.5),
                _price(stocks[2].id, 10, 30, 31),
                _price(stocks[4].id, 8, 0, 2),
                _price(stocks[4].id, 6, 1, 0),
            ]
        )
        session.commit()
    return database


@contextmanager
def _selects(database: Engine) -> Iterator[list[str]]:
    statements: list[str] = []

    def capture(_connection: object, _cursor: object, sql: str, *_args: object) -> None:
        if sql.lstrip().upper().startswith("SELECT"):
            statements.append(sql)

    event.listen(database, "before_cursor_execute", capture)
    try:
        yield statements
    finally:
        event.remove(database, "before_cursor_execute", capture)


def test_quotes_use_last_known_price_without_looking_ahead(quotes: Engine) -> None:
    with _selects(quotes) as statements:
        candles = repository.stock.get_stocks_by_date(TODAY)

    assert len(statements) == 1
    assert [c.ticker for c in candles] == ["ZETA3", "ALFA11", "ZERO11"]
    assert [c.close for c in candles] == [10.25, 20.5, 2]
    assert [c.price_date for c in candles] == [TODAY, date(2020, 1, 6), TODAY]
    assert [c.asset_class.value for c in candles] == ["STOCK", "FII", "ETF"]
    assert candles[0].change == -1.75
    assert candles[0].change_pct == pytest.approx(-1.75 / 12)
    assert candles[0].volume == 1008
    assert candles[2].change == 2
    assert candles[2].change_pct == 0


def test_quotes_on_weekend_and_after_history_keep_last_price(quotes: Engine) -> None:
    friday = repository.stock.get_stocks_by_date(date(2020, 1, 10))
    weekend = repository.stock.get_stocks_by_date(date(2020, 1, 12))
    later = repository.stock.get_stocks_by_date(date(2021, 1, 1))
    assert friday == weekend == later
    assert [c.close for c in later] == [60, 20.5, 31, 2]


@pytest.mark.parametrize("days", [0, 1, 2, 30])
def test_recent_closes_limit_each_asset_and_keep_empty_series(
    quotes: Engine, days: int
) -> None:
    with _selects(quotes) as statements:
        closes = repository.stock.get_recent_closes(TODAY, days)

    def tail(values: list[float]) -> list[float]:
        return values[-days:] if days else []

    assert len(statements) == 1
    assert closes == {
        "ZETA3": tail([9, 12, 10.25]),
        "ALFA11": tail([20.5]),
        "FUTR3": [],
        "NONE3": [],
        "ZERO11": tail([0, 2]),
    }


def test_dates_before_history_return_no_quotes_or_closes(quotes: Engine) -> None:
    before = date(2019, 12, 31)
    assert repository.stock.get_stocks_by_date(before) == []
    assert repository.stock.get_recent_closes(before, 30) == {
        ticker: [] for ticker in ("ZETA3", "ALFA11", "FUTR3", "NONE3", "ZERO11")
    }


def test_empty_market_uses_one_query_for_each_read(database: Engine) -> None:
    with _selects(database) as statements:
        assert repository.stock.get_stocks_by_date(TODAY) == []
    assert len(statements) == 1
    with _selects(database) as statements:
        assert repository.stock.get_recent_closes(TODAY, 30) == {}
    assert len(statements) == 1


@pytest.mark.parametrize("count", [1, 50])
def test_query_count_does_not_grow_with_the_market(
    database: Engine, count: int
) -> None:
    with Session(database) as session:
        stocks = [
            Stock(ticker=f"ASSET{i}", name=f"Empresa {i}", asset_class="STOCK")
            for i in range(1, count + 1)
        ]
        session.add_all(stocks)
        session.flush()
        session.add_all(_price(stock.id, 8, 10, 11) for stock in stocks)
        session.commit()

    with _selects(database) as statements:
        assert len(repository.stock.get_stocks_by_date(TODAY)) == count
    assert len(statements) == 1
    with _selects(database) as statements:
        assert len(repository.stock.get_recent_closes(TODAY, 30)) == count
    assert len(statements) == 1


def test_detail_matches_quote_and_preserves_chronological_history(
    quotes: Engine,
) -> None:
    candles = repository.stock.get_stocks_by_date(TODAY)
    for candle in candles:
        details = repository.stock.get_stock_details(candle.ticker, TODAY)
        assert details is not None
        assert details.model_dump(exclude={"history"}) == candle.model_dump()
        assert [p.price_date for p in details.history] == sorted(
            p.price_date for p in details.history
        )
        assert all(p.price_date <= TODAY for p in details.history)


def test_detail_without_prices_preserves_empty_candle(quotes: Engine) -> None:
    for ticker in ("FUTR3", "NONE3"):
        details = repository.stock.get_stock_details(ticker, TODAY)
        assert details is not None
        assert details.history == []
        assert details.price_date == TODAY
        assert (
            details.open == details.close == details.change == details.change_pct == 0
        )
    assert repository.stock.get_stock_details("UNKNOWN", TODAY) is None


def test_last_imported_price_is_limited_in_sql(quotes: Engine) -> None:
    stock = repository.stock.get_by_ticker("ZETA3")
    assert stock is not None
    with _selects(quotes) as statements:
        history = repository.stock.get_last_stock_price_history(stock.id)
    assert len(statements) == 1
    assert "LIMIT" in statements[0].upper()
    assert history is not None
    assert history.price_date == date(2020, 1, 10)
    assert history.close == 60
    empty = repository.stock.get_by_ticker("NONE3")
    assert empty is not None
    assert repository.stock.get_last_stock_price_history(empty.id) is None


@pytest.mark.parametrize(
    ("version", "expected"),
    [(0, [9, 12, 10.25]), (1, [9, 102, 103]), (2, [9, 12, 203])],
)
def test_batch_reads_respect_frozen_versions_without_duplicate_dates(
    quotes: Engine, version: int, expected: list[float]
) -> None:
    stock = repository.stock.get_by_ticker("ZETA3")
    assert stock is not None
    with Session(quotes) as session:
        for copy_version, day, close in [
            (1, 6, 102),
            (1, 8, 103),
            (2, 8, 203),
            (1, 12, 999),
        ]:
            price = _price(stock.id, day, close - 1, close)
            price.version = copy_version
            price.origin = "GENERATED"
            session.add(price)
        session.commit()

    with _selects(quotes) as statements:
        candles = repository.stock.get_stocks_by_date(TODAY, simulation_id=version)
    assert len(statements) == 1
    candle = next(c for c in candles if c.ticker == "ZETA3")
    assert candle.close == expected[-1]
    with _selects(quotes) as statements:
        closes = repository.stock.get_recent_closes(TODAY, 30, simulation_id=version)
    assert len(statements) == 1
    assert closes["ZETA3"] == expected
    assert (
        repository.stock.get_recent_closes(TODAY, 2, simulation_id=version)["ZETA3"]
        == expected[-2:]
    )
    detail = repository.stock.get_stock_details("ZETA3", TODAY, simulation_id=version)
    assert detail is not None
    assert detail.model_dump(exclude={"history"}) == candle.model_dump()
    assert [p.close for p in detail.history] == expected


def test_batch_reads_use_active_match_version_and_import_uses_only_real_common_prices(
    quotes: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    stock = repository.stock.get_by_ticker("ZETA3")
    assert stock is not None
    with Session(quotes) as session:
        copy = _price(stock.id, 8, 90, 99)
        copy.version = 7
        copy.origin = "GENERATED"
        generated = _price(stock.id, 12, 70, 75)
        generated.origin = "GENERATED"
        session.add_all([copy, generated])
        session.commit()
    monkeypatch.setattr(SimulationManager, "get_active_simulation_id", lambda: 7)
    candles = repository.stock.get_stocks_by_date(TODAY)
    assert next(c.close for c in candles if c.ticker == "ZETA3") == 99
    assert repository.stock.get_recent_closes(TODAY, 2)["ZETA3"] == [12, 99]
    assert repository.stock.get_recent_closes(TODAY, 2, simulation_id=0)["ZETA3"] == [
        12,
        10.25,
    ]
    last_imported = repository.stock.get_last_stock_price_history(stock.id)
    assert last_imported is not None
    assert (last_imported.price_date, last_imported.close) == (date(2020, 1, 10), 60)


def test_market_keeps_quote_and_sparkline_consistent_and_reuses_classification(
    quotes: Engine,
) -> None:
    sim = object.__new__(Simulation)
    sim._current_date = TODAY
    sim._engine = SimulationEngine(TODAY, Decimal("1000"), 1, date(2030, 1, 1))
    sim._price_impact = PriceImpact(1, False, 0.02, 20)
    with _selects(quotes) as statements:
        market = sim.get_market()
    assert len(statements) == 3  # cotações, fechamentos e classificação
    assert [q.ticker for q in market] == ["ZETA3", "ALFA11", "ZERO11"]
    assert market[0].sparkline == [9, 12, 10.25]
    assert all(q.sparkline[-1] == q.close for q in market)

    with _selects(quotes) as statements:
        assert sim.get_market() == market
    assert len(statements) == 2
