"""Gravação do futuro gerado, cópia na troca e o real ocupando o lugar do gerado."""

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

import pandas as pd
import pytest
from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from backend.core import repository
from backend.core.dto.generated_future import (
    FutureParamsDTO,
    FuturePreviewRequest,
    GeneratedFutureDTO,
)
from backend.core.enum import DataOrigin, IndicatorSeries
from backend.core.exceptions.http_exceptions import BadRequestError, ConflictError
from backend.core.models.models import (
    EconomicIndicatorHistory,
    Snapshots,
    StockPriceHistory,
)
from backend.features.import_data import future
from backend.features.import_data.coverage import get_series_coverage
from backend.features.import_data.importer_service import upsert_dataframe
from tests.fakes import simulation_settings
from tests.test_synthetic_series import LAST_REAL

UNTIL = date(2005, 6, 30)
PLAYED_UNTIL = date(2005, 2, 15)


def params(seed: int) -> FutureParamsDTO:
    return FutureParamsDTO(until=UNTIL, seed=seed, temperature=1, inflation_shock=0)


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
                total_networth=Decimal(0),
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
        until=UNTIL, seed=7, temperature=1, inflation_shock=10, ticker="BANK_A"
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
