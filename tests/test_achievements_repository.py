from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.enum import AssetClass, EquityEventType
from backend.features.achievements import service
from tests.fakes import client, simulation_settings

DAY = date(2020, 1, 2)


@pytest.fixture
def match(database: object) -> tuple[int, int]:
    """Um jogador e uma partida no banco; devolve `(user_id, simulation_id)`."""
    user = repository.user.create_user(client("Ana"), "Ana")
    simulation_id = repository.simulation.create_simulation(simulation_settings())
    return user.id, simulation_id


def order(
    user_id: int, simulation_id: int, ticker: str, kind: EquityEventType, day: date
) -> EquityEventDTO:
    return EquityEventDTO(
        simulation_id=simulation_id,
        user_id=user_id,
        event_date=day,
        ticker=ticker,
        event_type=kind,
        quantity=Decimal(10),
        price=Decimal(20),
    )


def test_unlock_is_idempotent_and_returns_only_the_new_ones(match: tuple[int, int]):
    user_id, simulation_id = match

    first = repository.achievements.unlock(
        user_id, ["first_buy", "first_sale"], simulation_id, DAY
    )
    again = repository.achievements.unlock(
        user_id, ["first_buy", "hands_on"], simulation_id, DAY
    )

    assert first == ["first_buy", "first_sale"]
    assert again == ["hands_on"]
    assert repository.achievements.unlocked_codes(user_id) == {
        "first_buy",
        "first_sale",
        "hands_on",
    }


def test_progress_keeps_the_best_value(match: tuple[int, int]):
    user_id, _ = match

    repository.achievements.save_progress(user_id, {"networth_1m": Decimal(600)})
    repository.achievements.save_progress(user_id, {"networth_1m": Decimal(200)})
    repository.achievements.save_progress(user_id, {"networth_1m": Decimal(900)})

    assert repository.achievements.best_progress(user_id) == {
        "networth_1m": Decimal(900)
    }


def test_new_flag_lasts_until_the_player_marks_them_seen(match: tuple[int, int]):
    user_id, simulation_id = match
    repository.achievements.unlock(user_id, ["first_buy"], simulation_id, DAY)

    before = {a.code: a for a in service.list_achievements(user_id)}
    service.mark_seen(user_id)
    after = {a.code: a for a in service.list_achievements(user_id)}

    unlock = before["first_buy"].unlock
    assert unlock is not None
    assert unlock.is_new
    assert (unlock.game_date, unlock.simulation_name) == (DAY, "Partida")
    assert after["first_buy"].unlock is not None
    assert not after["first_buy"].unlock.is_new
    assert after["first_sale"].unlock is None


def test_deleting_the_match_keeps_its_achievements(match: tuple[int, int]):
    user_id, simulation_id = match
    repository.achievements.unlock(user_id, ["first_buy"], simulation_id, DAY)

    repository.simulation.delete(simulation_id)

    unlock = {a.code: a for a in service.list_achievements(user_id)}["first_buy"].unlock
    assert unlock is not None
    assert (unlock.simulation_id, unlock.simulation_name) == (None, None)
    assert unlock.game_date == DAY


def test_other_players_do_not_see_each_others_achievements(match: tuple[int, int]):
    user_id, simulation_id = match
    other = repository.user.create_user(client("Bia"), "Bia")
    repository.achievements.unlock(user_id, ["first_buy"], simulation_id, DAY)

    listed = {a.code: a for a in service.list_achievements(other.id)}

    assert listed["first_buy"].unlock is None


def test_event_measures_follow_the_orders(match: tuple[int, int]):
    user_id, simulation_id = match
    for ticker in ("AAA", "BBB"):
        repository.stock.add_stock(ticker, ticker, AssetClass.STOCK)
    buy, sell = EquityEventType.BUY, EquityEventType.SELL
    repository.event.insert_many(
        [
            order(user_id, simulation_id, "AAA", buy, date(2020, 1, 2)),
            order(user_id, simulation_id, "BBB", buy, date(2020, 1, 3)),
            order(user_id, simulation_id, "AAA", sell, date(2020, 1, 6)),
        ]
    )
    stats = repository.achievements

    assert stats.equity_orders(simulation_id, user_id, None) == 3
    assert stats.equity_orders(simulation_id, user_id, "SELL") == 1
    assert stats.equity_order_dates(simulation_id, user_id, "BUY") == [
        date(2020, 1, 2),
        date(2020, 1, 3),
    ]
    # AAA foi vendida inteira, sobra BBB
    assert stats.held_assets(simulation_id, user_id) == 1
    assert stats.fixed_income_buys(simulation_id, user_id) == 0
