"""Gravação do futuro gerado, cópia na troca e o real ocupando o lugar do gerado."""

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any

import pandas as pd
import pytest
from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from backend.core import repository
from backend.core.dto.generated_future import (
    FutureParamsDTO,
    FuturePreviewDTO,
    FuturePreviewRequest,
    GeneratedFutureDTO,
)
from backend.core.dto.series_coverage import SeriesKind
from backend.core.enum import DataOrigin, IndicatorSeries
from backend.core.exceptions.http_exceptions import BadRequestError, ConflictError
from backend.core.indicators import annual_index_rate
from backend.core.models.models import (
    EconomicIndicatorHistory,
    Snapshots,
    StockCorporateEvent,
    StockPriceHistory,
)
from backend.features.import_data import future
from backend.features.import_data.coverage import get_series_coverage
from backend.features.import_data.importer_service import upsert_dataframe
from tests.fakes import simulation_settings
from tests.test_synthetic_series import LAST_REAL

UNTIL = date(2005, 6, 30)
PLAYED_UNTIL = date(2005, 2, 15)
# Sem nível nem surtos de inflação
NEUTRAL: dict[str, Any] = {
    "inflation_level": 0,
    "surge_frequency": 0,
    "surge_intensity": 6,
}


def params(seed: int) -> FutureParamsDTO:
    return FutureParamsDTO(until=UNTIL, seed=seed, temperature=1, **NEUTRAL)


@pytest.fixture
def progress(monkeypatch: pytest.MonkeyPatch) -> list[dict]:
    sent: list[dict] = []
    monkeypatch.setattr(future, "notify", lambda _event, payload: sent.append(payload))
    return sent


@pytest.fixture
def base(market: Engine, progress: list[dict]) -> Engine:
    return market


def stored_future() -> GeneratedFutureDTO:
    saved = repository.generated_future.get()
    assert saved is not None
    return saved


def saved_match(engine: Engine, start: date, played_until: date) -> int:
    """Uma partida salva que jogou de `start` a `played_until`."""
    simulation_id = repository.simulation.create_simulation(
        simulation_settings().model_copy(
            update={"name": f"Partida {uuid.uuid4().hex[:6]}", "start_date": start}
        )
    )
    user = repository.user.create_user(uuid.uuid4(), f"J{uuid.uuid4().hex[:6]}")
    with Session(engine) as session:
        session.add(
            Snapshots(
                simulation_id=simulation_id,
                user_id=user.id,
                snapshot_date=played_until,
                total_equity=Decimal(0),
                total_fixed=Decimal(0),
                total_cash=Decimal(0),
                total_contribution=Decimal(0),
                total_debt=Decimal(0),
                total_networth=Decimal(0),
                equity_by_class={},
                created_at=datetime.now(UTC),
            )
        )
        session.commit()
    return simulation_id


def generated_closes(engine: Engine, version: int = 0) -> dict[date, float]:
    stock = repository.stock.get_by_ticker("BANK_A")
    assert stock is not None
    with Session(engine) as session:
        rows = session.execute(
            select(StockPriceHistory.price_date, StockPriceHistory.close)
            .where(
                StockPriceHistory.stock_id == stock.id,
                StockPriceHistory.origin == DataOrigin.GENERATED.value,
                StockPriceHistory.version == version,
            )
            .order_by(StockPriceHistory.price_date)
        ).all()
    return dict(rows)


def test_record_writes_generated_rows_and_keeps_the_controls(
    base: Engine, progress: list[dict]
):
    saved = future.record(params(4821))

    closes = generated_closes(base)
    assert min(closes) > LAST_REAL and max(closes) <= UNTIL
    assert (saved.seed, saved.until, saved.real_advanced_until) == (4821, UNTIL, None)
    assert saved.saved_simulations_on_future == 0
    # Uma série por vez, na ordem em que entram, até a última
    assert progress[-1]["done"] == progress[-1]["total"] == len(progress)
    # A Central já mostra o trecho gerado pelo fim do gerado de cada série
    coverage = {s.key: s for s in get_series_coverage()}
    assert coverage["IBOV"].real_end == LAST_REAL
    assert coverage["IBOV"].generated_end == max(closes)


def test_regenerating_copies_the_played_days_to_the_saved_match(base: Engine):
    future.record(params(1))
    first = generated_closes(base)
    simulation_id = saved_match(base, date(2004, 10, 1), PLAYED_UNTIL)
    assert stored_future().saved_simulations_on_future == 1

    future.record(params(2))

    copy = generated_closes(base, simulation_id)
    assert copy == {d: c for d, c in first.items() if d <= PLAYED_UNTIL}
    day = max(copy)
    mine = repository.stock.get_closes_on(day, simulation_id=simulation_id)
    common = repository.stock.get_closes_on(day)
    assert mine["BANK_A"] == first[day]
    assert common["BANK_A"] == generated_closes(base)[day] != first[day]


def test_deleting_a_match_drops_its_frozen_copy_and_keeps_the_rest(base: Engine):
    future.record(params(1))
    first = saved_match(base, date(2004, 10, 1), PLAYED_UNTIL)
    other = saved_match(base, date(2004, 10, 1), PLAYED_UNTIL)
    future.record(params(2))
    assert generated_closes(base, first) and generated_closes(base, other)

    assert repository.simulation.delete(first)

    assert generated_closes(base, first) == {}
    assert generated_closes(base, other)
    assert generated_closes(base)
    with Session(base) as session:
        snapshots = session.scalars(
            select(Snapshots.simulation_id).where(Snapshots.simulation_id == first)
        ).all()
    assert snapshots == []
    assert not repository.simulation.delete(first)


def test_real_arriving_takes_the_place_of_the_generated(base: Engine):
    future.record(params(1))
    simulation_id = saved_match(base, date(2004, 10, 1), PLAYED_UNTIL)
    generated = generated_closes(base)
    days = [d for d in generated if d <= date(2005, 1, 31)]
    real = pd.DataFrame(
        {"Open": 1.0, "High": 1.0, "Low": 1.0, "Close": 1.0, "Volume": 1},
        index=pd.to_datetime(days[:-2]),
    )

    replaced = upsert_dataframe(real, "BANK_A")

    assert replaced is not None
    assert (replaced.days, replaced.start) == (len(days) - 2, days[0])
    assert min(generated_closes(base)) > days[-3]
    assert stored_future().real_advanced_until == days[-3]
    # A partida salva continua vendo o gerado que jogou
    assert generated_closes(base, simulation_id)[days[0]] == generated[days[0]]

    future.record(params(1))
    assert stored_future().real_advanced_until is None


def test_indicator_refresh_copies_before_the_upsert_changes_the_origin(base: Engine):
    future.record(params(1))
    simulation_id = saved_match(base, date(2004, 10, 1), PLAYED_UNTIL)
    with Session(base) as session:
        generated = dict(
            session.execute(
                select(
                    EconomicIndicatorHistory.ref_date, EconomicIndicatorHistory.value
                ).where(
                    EconomicIndicatorHistory.series == IndicatorSeries.SELIC.value,
                    EconomicIndicatorHistory.version == 0,
                    EconomicIndicatorHistory.ref_date <= date(2005, 1, 31),
                    EconomicIndicatorHistory.ref_date > LAST_REAL,
                )
            ).all()
        )

    repository.economic.save_history(
        IndicatorSeries.SELIC, [(day, Decimal("0.05")) for day in generated]
    )

    mine = repository.economic.get_history(IndicatorSeries.SELIC, simulation_id)
    common = repository.economic.get_history(IndicatorSeries.SELIC)
    day = min(generated)
    assert mine.value_on(day) == generated[day]
    assert common.value_on(day) == Decimal("0.05")


def test_cancelling_keeps_the_previous_future(
    base: Engine, monkeypatch: pytest.MonkeyPatch
):
    future.record(params(1))
    before = generated_closes(base)
    monkeypatch.setattr(future, "notify", lambda *_args: future.cancel_recording())

    with pytest.raises(ConflictError):
        future.record(params(2))

    assert generated_closes(base) == before
    assert stored_future().seed == 1


def test_preview_generates_without_recording(base: Engine):
    request = FuturePreviewRequest(
        until=UNTIL,
        seed=7,
        temperature=1,
        **(NEUTRAL | {"inflation_level": 10}),
        ticker="BANK_A",
    )

    preview = future.preview(request)

    assert generated_closes(base) == {}
    assert preview.asset is not None and preview.asset.generated
    assert preview.ibov_change.end == preview.ibov.generated[-1].value
    assert preview.laggard_start is not None and preview.laggard_start.key == "POWER"
    assert preview.selic_peak is not None and preview.ipca_peak is not None
    assert preview.trading_days > 100
    with Session(base) as session:
        assert session.scalar(select(func.count()).select_from(StockPriceHistory))

    with pytest.raises(BadRequestError):
        future.preview(request.model_copy(update={"until": LAST_REAL}))


def macro_preview(base: Engine, **controls: Any) -> FuturePreviewDTO:
    """A prévia de 10 anos, com os controles neutros alterados por `controls`."""
    return future.preview(
        FuturePreviewRequest(
            until=date(LAST_REAL.year + 10, 12, 31),
            seed=7,
            temperature=1,
            **(NEUTRAL | controls),
        )
    )


def record_macro() -> None:
    """PIB por trimestre até o 3º de 2004 e desemprego por mês até outubro de 2004."""
    repository.economic.save_history(
        IndicatorSeries.GDP_GROWTH,
        [
            (date(year, month, 1), Decimal("3.0"))
            for year in (2002, 2003, 2004)
            for month in (1, 4, 7, 10)
            if (year, month) <= (2004, 7)
        ],
    )
    repository.economic.save_history(
        IndicatorSeries.UNEMPLOYMENT,
        [(date(2002 + (m // 12), m % 12 + 1, 1), Decimal("8.0")) for m in range(34)],
    )


def test_preview_brings_gdp_and_unemployment_after_the_recorded_months(base: Engine):
    record_macro()

    preview = macro_preview(base)

    assert preview.gdp_growth.real[-1].date == date(2004, 9, 30)
    assert preview.gdp_growth.real[-1].value == 3.0
    assert preview.unemployment.real[-1].date == date(2004, 10, 31)
    for series in (preview.gdp_growth, preview.unemployment):
        assert series.generated[0].date > series.real[-1].date
        assert series.generated[-1].date == date(LAST_REAL.year + 10, 12, 31)
        assert all(-10 < point.value < 25 for point in series.generated)


def test_preview_rates_are_the_ones_the_game_reads(base: Engine):
    """A SELIC e o IPCA de 12 meses da prévia são os de annual_index_rate nos dias reais."""
    preview = macro_preview(base)

    selic = preview.selic.real[-1]
    ipca = preview.ipca_12m.real[-1]
    assert selic.value == pytest.approx(
        float(annual_index_rate(IndicatorSeries.SELIC, selic.date, stored=True)) * 100
    )
    assert ipca.value == pytest.approx(
        float(annual_index_rate(IndicatorSeries.IPCA, ipca.date, stored=True)) * 100
    )


def test_a_higher_inflation_level_drops_gdp_in_the_transition_and_settles_close_after(
    base: Engine,
):
    calm = [p.value for p in macro_preview(base).gdp_growth.generated]
    raised = [
        p.value for p in macro_preview(base, inflation_level=10).gdp_growth.generated
    ]

    # A subida do juro derruba o crescimento nos primeiros três anos
    assert min(raised[:36]) < min(calm[:36]) - 1
    # Depois de 10 anos o nível assentou: o último ano fica perto do sem nível
    assert abs(sum(raised[-12:]) / 12 - sum(calm[-12:]) / 12) < 0.5


def test_horizon_stops_thirty_years_after_the_last_real_day(base: Engine):
    last_year = LAST_REAL.year + future.MAX_FUTURE_YEARS
    request = FuturePreviewRequest(
        until=date(last_year + 1, 1, 2), seed=7, temperature=1, **NEUTRAL
    )

    with pytest.raises(BadRequestError, match=f"31/12/{last_year}"):
        future.preview(request)


def test_gdp_and_unemployment_appear_apart_from_the_market_indicators(base: Engine):
    kinds = {s.key: s.kind for s in get_series_coverage()}

    assert kinds["IBOV"] is SeriesKind.INDICATOR
    assert kinds["GDP_GROWTH"] is kinds["UNEMPLOYMENT"] is SeriesKind.MACRO


def test_fed_funds_is_macro_but_keeps_a_generated_future(base: Engine):
    coverage = {s.key: s for s in get_series_coverage()}

    assert coverage["FED_FUNDS"].kind is SeriesKind.MACRO
    assert coverage["FED_FUNDS"].real_end == LAST_REAL
    assert coverage["FED_FUNDS"].generated_end is None


def test_recording_writes_the_fed_funds_future(base: Engine, progress: list[dict]):
    future.record(params(7))

    coverage = {s.key: s for s in get_series_coverage()}
    assert coverage["FED_FUNDS"].generated_end == UNTIL


def test_the_focus_series_appear_as_expectations(base: Engine):
    kinds = {s.key: s.kind for s in get_series_coverage()}

    focus = ("FOCUS_SELIC", "FOCUS_IPCA", "FOCUS_GDP", "FOCUS_FX")
    assert all(kinds[key] is SeriesKind.EXPECTATION for key in focus)


def put_generated_dividends(engine: Engine, *days: date) -> int:
    """Dividendos gerados da série comum de BANK_A nas datas ex dadas."""
    stock = repository.stock.get_by_ticker("BANK_A")
    assert stock is not None
    with Session(engine) as session:
        session.add_all(
            StockCorporateEvent(
                stock_id=stock.id,
                ex_date=day,
                kind="DIVIDEND",
                value=Decimal("0.5"),
                origin=DataOrigin.GENERATED.value,
                version=0,
            )
            for day in days
        )
        session.commit()
    return stock.id


def events_of(engine: Engine, version: int) -> list[date]:
    with Session(engine) as session:
        return list(
            session.scalars(
                select(StockCorporateEvent.ex_date)
                .where(StockCorporateEvent.version == version)
                .order_by(StockCorporateEvent.ex_date)
            )
        )


def test_regenerating_freezes_the_played_dividends_and_drops_the_rest(base: Engine):
    future.record(params(1))
    simulation_id = saved_match(base, date(2004, 10, 1), PLAYED_UNTIL)
    put_generated_dividends(base, date(2005, 1, 10), date(2005, 4, 11))

    future.record(params(2))

    assert events_of(base, simulation_id) == [date(2005, 1, 10)]
    assert date(2005, 1, 10) not in events_of(base, 0)


def test_real_arriving_takes_the_place_of_the_generated_dividends(base: Engine):
    future.record(params(1))
    put_generated_dividends(base, date(2005, 1, 10), date(2005, 4, 11))
    days = [d for d in generated_closes(base) if d <= date(2005, 1, 31)]
    real = pd.DataFrame(
        {"Open": 1.0, "High": 1.0, "Low": 1.0, "Close": 1.0, "Volume": 1},
        index=pd.to_datetime(days),
    )

    upsert_dataframe(real, "BANK_A")

    # O dividendo gerado coberto pelo real sai; o que ficou depois dele permanece
    assert events_of(base, 0) == [date(2005, 4, 11)]
