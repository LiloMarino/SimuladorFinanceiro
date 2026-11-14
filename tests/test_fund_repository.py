"""As gestoras no banco: registro, fechamentos do pregão, vela da partida e isolamento do catálogo."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from backend.core import repository
from backend.core.dto.candle import CandleDTO
from backend.core.dto.fund import FundDayDTO
from backend.core.enum import AssetClass
from tests.fakes import client, simulation_settings

DAY = date(2020, 1, 6)
TICKER = "AURA11"


class Match:
    def __init__(self, simulation_id: int, user_id: int) -> None:
        self.simulation_id = simulation_id
        self.user_id = user_id
        stock = repository.stock.add_stock(TICKER, "Aura", AssetClass.FUND)
        self.stock_id = stock.id
        self.fund = repository.fund.create(
            simulation_id=simulation_id,
            stock_id=stock.id,
            ticker=TICKER,
            client_id=uuid4(),
            founder_user_id=user_id,
            manager_user_id=user_id,
            name="Aura",
            management_fee=Decimal("0.02"),
            performance_fee=Decimal("0.20"),
        )

    def candle(self, day: date, close: float) -> CandleDTO:
        return CandleDTO(
            id=self.stock_id,
            ticker=TICKER,
            name="Aura",
            asset_class=AssetClass.FUND,
            open=close,
            high=close,
            low=close,
            close=close,
            volume=10,
            price_date=day,
            change=0,
            change_pct=0,
        )


def day(when: date, nav: str = "100") -> FundDayDTO:
    return FundDayDTO(
        day=when,
        nav=Decimal(nav),
        quotas=Decimal(1000),
        traded_quantity=Decimal(10),
        traded_value=Decimal(1000),
        ranking_price=Decimal(nav),
    )


@pytest.fixture
def match(database: object) -> Match:
    user = repository.user.create_user(client("Ana"), "Ana")
    simulation_id = repository.simulation.create_simulation(simulation_settings())
    return Match(simulation_id, user.id)


def test_fund_is_born_empty_with_a_portfolio_without_owner(match: Match):
    [fund] = repository.fund.of_simulation(match.simulation_id)

    assert fund == match.fund
    assert fund.quotas == 0 and fund.listed_on is None
    assert repository.portfolio.ids(match.simulation_id) == {}


def test_save_keeps_every_mutable_column(match: Match):
    saved = match.fund.model_copy(
        update={
            "quotas": Decimal(1200),
            "maker_quotas": Decimal(120),
            "maker_cash": Decimal(-12000),
            "offer_remaining": Decimal(80),
            "listed_on": DAY,
            "pending_management_fee": Decimal("0.01"),
            "pending_performance_fee": Decimal("0.10"),
            "pending_from": date(2020, 2, 3),
            "high_water_mark": Decimal("100.5"),
            "high_water_mark_on": DAY,
            "last_performance_on": DAY,
        }
    )

    repository.fund.save(saved)

    assert repository.fund.of_simulation(match.simulation_id) == [saved]


def test_days_come_back_oldest_first_and_the_same_day_is_replaced(match: Match):
    fund_id = match.fund.id
    for offset in range(5):
        repository.fund.save_day(fund_id, day(date(2020, 1, 6 + offset)))
    repository.fund.save_day(fund_id, day(date(2020, 1, 10), "130"))

    recent = repository.fund.days(fund_id, date(2020, 1, 11), 3)

    assert [d.day.day for d in recent] == [8, 9, 10]
    assert recent[-1].nav == Decimal("130")


def test_drop_days_from_clears_the_day_and_the_following(match: Match):
    fund_id = match.fund.id
    for offset in range(5):
        repository.fund.save_day(fund_id, day(date(2020, 1, 6 + offset)))

    repository.fund.drop_days_from(fund_id, date(2020, 1, 9))

    assert [d.day.day for d in repository.fund.days(fund_id, date(2020, 2, 1), 10)] == [
        6,
        7,
        8,
    ]


def test_quota_candle_is_visible_only_to_its_own_match(match: Match):
    other = repository.simulation.create_simulation(
        simulation_settings().model_copy(update={"name": "Outra"})
    )
    repository.fund.save_candle(match.simulation_id, match.candle(DAY, 101.5))

    assert repository.fund.last_close(match.simulation_id, match.stock_id, DAY) == 101.5
    assert repository.fund.last_close(other, match.stock_id, DAY) is None
    assert (
        repository.fund.last_close(
            match.simulation_id, match.stock_id, date(2020, 1, 3)
        )
        is None
    )


def test_saving_the_candle_again_replaces_it(match: Match):
    repository.fund.save_candle(match.simulation_id, match.candle(DAY, 101.5))
    repository.fund.save_candle(match.simulation_id, match.candle(DAY, 99.0))

    assert repository.fund.last_close(match.simulation_id, match.stock_id, DAY) == 99.0


def test_quota_stays_out_of_the_imported_stock_lists(match: Match):
    repository.fund.save_candle(match.simulation_id, match.candle(DAY, 101.5))

    assert TICKER not in {s.ticker for s in repository.stock.get_stocks()}
    assert TICKER not in {
        c.ticker for c in repository.stock.get_stocks_by_date(DAY, match.simulation_id)
    }
