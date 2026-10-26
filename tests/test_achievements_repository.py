from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.sector import StockSegmentDTO
from backend.core.enum import AssetClass, DataOrigin, EquityEventType
from backend.core.models.models import StockPriceHistory
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


def test_sector_day_trade_and_flow_measures(match: tuple[int, int]):
    user_id, simulation_id = match
    sectors = {"AAA": "Energia", "BBB": "Energia", "CCC": "Bancos"}
    for ticker, sector in sectors.items():
        repository.stock.add_stock(ticker, ticker, AssetClass.STOCK)
        repository.stock.classify(ticker, StockSegmentDTO(sector=sector, segment="X"))
    repository.stock.add_stock("DDD", "DDD", AssetClass.STOCK)
    buy, sell = EquityEventType.BUY, EquityEventType.SELL
    repository.event.insert_many(
        [
            order(user_id, simulation_id, "AAA", buy, date(2020, 1, 2)),
            order(user_id, simulation_id, "BBB", buy, date(2020, 1, 2)),
            order(user_id, simulation_id, "CCC", buy, date(2020, 1, 2)),
            # Sem setor, não conta
            order(user_id, simulation_id, "DDD", buy, date(2020, 1, 2)),
            # CCC comprada e vendida no mesmo dia: day trade, e sai da carteira
            order(user_id, simulation_id, "CCC", sell, date(2020, 1, 2)),
            order(user_id, simulation_id, "AAA", sell, date(2020, 1, 3)),
        ]
    )
    stats = repository.achievements

    # AAA foi vendida inteira: sobram BBB (Energia) e DDD (sem setor)
    assert stats.held_sectors(simulation_id, user_id) == 1
    assert stats.day_traded_assets(simulation_id, user_id) == 1
    assert stats.equity_flows(simulation_id, user_id, date(2020, 1, 3)) == [
        ("AAA", date(2020, 1, 3), Decimal(-10))
    ]


def test_real_market_end_ignores_generated_days(match: tuple[int, int]):
    _, simulation_id = match
    stock = repository.stock.add_stock("AAA", "AAA", AssetClass.STOCK)
    assert repository.achievements.real_market_end(simulation_id) is None

    def row(day: date, origin: DataOrigin) -> StockPriceHistory:
        return StockPriceHistory(
            stock_id=stock.id,
            price_date=day,
            open=1,
            high=1,
            low=1,
            close=1,
            volume=1,
            origin=origin.value,
        )

    repository.stock.save_real_prices(
        stock.id,
        [
            row(date(2020, 1, 2), DataOrigin.REAL),
            row(date(2020, 1, 3), DataOrigin.REAL),
            row(date(2020, 1, 6), DataOrigin.GENERATED),
        ],
    )

    assert repository.achievements.real_market_end(simulation_id) == date(2020, 1, 3)
