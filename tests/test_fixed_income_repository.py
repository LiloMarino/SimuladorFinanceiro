"""O título de renda fixa pertence à partida que o emitiu e sai junto com ela."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from backend.core import repository
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.enum import FixedIncomeEventType, FixedIncomeType, RateIndexType
from backend.core.models.models import EventFixedIncome, FixedIncomeAsset
from tests.fakes import client, simulation_settings

ASSET = FixedIncomeAssetDTO(
    name="CDB Teste",
    issuer="Banco Teste",
    investment_type=FixedIncomeType.CDB,
    rate_index=RateIndexType.PREFIXADO,
    maturity_date=date(2022, 1, 1),
    interest_rate=Decimal("0.12"),
)


def _match(name: str) -> int:
    settings = simulation_settings().model_copy(update={"name": name})
    return repository.simulation.create_simulation(settings)


def _buy(database: Engine, simulation_id: int, user_id: int, asset_id: int) -> None:
    portfolio_id = repository.portfolio.create(simulation_id, [user_id])[user_id]
    with Session(database) as session, session.begin():
        session.add(
            EventFixedIncome(
                simulation_id=simulation_id,
                portfolio_id=portfolio_id,
                asset_id=asset_id,
                event_type=FixedIncomeEventType.BUY.value,
                amount=Decimal(100),
                tax_withheld=Decimal(0),
                event_date=date(2020, 1, 2),
                created_at=datetime.now(UTC),
            )
        )


def test_the_same_title_in_two_matches_is_one_row_per_match(database: Engine):
    first, second = _match("Primeira"), _match("Segunda")

    first_id = repository.fixed_income.get_or_create_asset(first, ASSET)

    assert repository.fixed_income.get_or_create_asset(first, ASSET) == first_id
    assert repository.fixed_income.get_or_create_asset(second, ASSET) != first_id
    assert repository.fixed_income.get_asset_by_uuid(second, str(ASSET.asset_uuid))


def test_deleting_a_match_takes_its_titles_and_their_events(database: Engine):
    user = repository.user.create_user(client("Ana"), "Ana")
    first, second = _match("Primeira"), _match("Segunda")
    _buy(
        database,
        first,
        user.id,
        repository.fixed_income.get_or_create_asset(first, ASSET),
    )
    kept = repository.fixed_income.get_or_create_asset(second, ASSET)
    _buy(database, second, user.id, kept)

    assert repository.simulation.delete(first)

    with Session(database) as session:
        assets = session.scalars(select(FixedIncomeAsset.id)).all()
        events = session.scalar(select(func.count()).select_from(EventFixedIncome))
    assert assets == [kept]
    assert events == 1
