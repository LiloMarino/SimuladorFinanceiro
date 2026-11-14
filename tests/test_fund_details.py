"""Os cálculos puros da página da gestora: controle, composição e posições."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import cast

import pytest

from backend.core.dto.fund import FundDTO, FundOfferSaleDTO, FundSeriesPointDTO
from backend.core.dto.user import UserDTO
from backend.features.funds import fund_details
from backend.features.funds.fund_account import FundAccount
from backend.features.funds.fund_book import Fund, FundBook
from backend.features.funds.fund_details import (
    FundDetailsBuilder,
    Line,
    composition_of,
    control_quotas,
    positions_of,
)
from backend.features.simulation.simulation_engine import SimulationEngine
from tests.fakes import client

LINES: list[Line] = [
    ("PETR4", "Petrobras", "stocks", Decimal(10), Decimal(300)),
    (None, "Caixa", "cash", None, Decimal(100)),
    (None, "Tesouro Selic", "treasury", None, Decimal(500)),
    ("VALE3", "Vale", "stocks", Decimal(5), Decimal(100)),
]


@pytest.mark.parametrize(
    ("total", "expected"),
    [(100, 51), (101, 51), (1, 1), (2, 2), (1000, 501)],
)
def test_control_is_more_than_half_of_the_quotas(total: int, expected: int):
    assert control_quotas(Decimal(total)) == expected


def test_control_of_fractional_quotas_rounds_the_half_down_before_adding_one():
    assert control_quotas(Decimal("100.6")) == 51


def test_positions_put_the_cash_first_and_the_rest_by_value():
    positions = positions_of(LINES)

    assert [p.name for p in positions] == [
        "Caixa",
        "Tesouro Selic",
        "Petrobras",
        "Vale",
    ]
    assert positions[2].quantity == 10
    assert positions[2].ticker == "PETR4"


def test_positions_carry_the_fraction_of_the_whole_portfolio():
    positions = positions_of(LINES)

    assert [p.fraction for p in positions] == [
        Decimal("0.1"),
        Decimal("0.5"),
        Decimal("0.3"),
        Decimal("0.1"),
    ]


def test_composition_sums_by_class_in_a_fixed_order():
    composition = composition_of(LINES)

    assert [(c.asset_class, c.value, c.fraction) for c in composition] == [
        ("cash", Decimal(100), Decimal("0.1")),
        ("stocks", Decimal(400), Decimal("0.4")),
        ("fixed_income", Decimal(0), Decimal(0)),
        ("treasury", Decimal(500), Decimal("0.5")),
    ]


def test_composition_of_an_empty_portfolio_is_all_zero():
    composition = composition_of([])

    assert len(composition) == 4
    assert {c.fraction for c in composition} == {Decimal(0)}


# =========================
# Desempenho, taxas e quem tem as cotas
# =========================

TODAY = date(2004, 9, 1)


def builder() -> FundDetailsBuilder:
    return FundDetailsBuilder(
        cast("FundBook", None),
        cast("SimulationEngine", None),
        1,
        lambda: {1: "chart-1", 2: "chart-2"},
    )


def point(day: date, nav: str) -> FundSeriesPointDTO:
    return FundSeriesPointDTO(day=day, close=None, nav=Decimal(nav))


def fund_with(**terms: object) -> Fund:
    base: dict[str, object] = {
        "id": 1,
        "ticker": "AURA11",
        "stock_id": 1,
        "portfolio_id": 100,
        "client_id": client("aura"),
        "founder_user_id": 1,
        "manager_user_id": 1,
        "name": "Aura",
        "quotas": Decimal(0),
        "maker_quotas": Decimal(0),
        "maker_cash": Decimal(0),
        "offer_remaining": None,
        "listed_on": None,
        "offer_quotas": None,
        "offer_price": None,
        "offer_closed_on": None,
        "management_fee": Decimal("0.12"),
        "performance_fee": Decimal("0.10"),
        "pending_management_fee": None,
        "pending_performance_fee": None,
        "pending_from": None,
        "high_water_mark": None,
        "high_water_mark_on": None,
        "last_performance_on": None,
    }
    base.update(terms)
    dto = FundDTO(**base)  # type: ignore[arg-type]
    return Fund(
        terms=dto,
        account=FundAccount(
            client_id=dto.client_id,
            quotas=Decimal(110),
            maker_quotas=Decimal(10),
        ),
    )


@pytest.fixture
def flat_cdi(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(fund_details, "cdi_growth", lambda start, end: Decimal("1.02"))


def test_return_is_the_nav_growth_since_the_first_point_of_the_window(flat_cdi):
    series = [point(date(2003, 9, 2), "100"), point(date(2004, 8, 31), "105")]

    result = builder()._returns(series, Decimal(110), date(2003, 8, 1), TODAY)

    assert result == (Decimal("0.1"), None, Decimal("0.02"))


def test_return_of_a_fund_younger_than_a_year_says_since_when(flat_cdi):
    series = [point(date(2004, 3, 3), "100")]

    _, since, _ = builder()._returns(series, Decimal(110), date(2004, 3, 2), TODAY)

    assert since == date(2004, 3, 3)


def test_return_without_series_or_nav_is_unknown(flat_cdi):
    series = [point(date(2004, 3, 3), "100")]

    assert builder()._returns([], Decimal(110), None, TODAY) == (None, None, None)
    assert builder()._returns(series, None, None, TODAY) == (None, None, None)
    zero = [point(date(2004, 3, 3), "0")]
    assert builder()._returns(zero, Decimal(1), None, TODAY) == (None, None, None)


def test_fees_before_the_offer_have_no_performance_dates(flat_cdi):
    fund = fund_with()

    fees = builder()._fees(fund, None, TODAY, [])

    assert fees.management_monthly_estimate == 0
    assert fees.performance_estimate is None
    assert fees.next_performance_on is None
    assert fees.received_12m == 0


def test_fees_estimate_the_month_and_the_semester_from_the_water_mark(flat_cdi):
    fund = fund_with(
        listed_on=date(2004, 3, 2),
        high_water_mark=Decimal(100),
        high_water_mark_on=date(2004, 3, 2),
    )

    fees = builder()._fees(fund, Decimal(110), TODAY, [])

    # 12% ao ano: 1% ao mês sobre R$ 110 por cota nas 100 cotas fora do formador
    assert fees.management_monthly_estimate == Decimal("110.00")
    # Linha d'água de R$ 102 (100 corrigidos pelo CDI): 10% de R$ 8 por cota nas 100 cotas
    assert fees.performance_estimate == Decimal("80.00")
    assert fees.next_performance_on == date(2004, 9, 1)
    assert (fees.high_water_mark, fees.high_water_mark_on) == (
        Decimal(100),
        date(2004, 3, 2),
    )


def test_next_performance_counts_from_the_last_charge(flat_cdi):
    fund = fund_with(
        listed_on=date(2004, 3, 2),
        high_water_mark=Decimal(100),
        high_water_mark_on=date(2004, 9, 1),
        last_performance_on=date(2004, 9, 1),
    )

    fees = builder()._fees(fund, Decimal(100), date(2004, 9, 2), [])

    assert fees.next_performance_on == date(2005, 3, 1)
    assert fees.performance_estimate == 0


def user(user_id: int, nickname: str, *, bot: bool = False) -> UserDTO:
    return UserDTO(
        id=user_id, client_id=client(nickname), nickname=nickname, is_bot=bot
    )


def sale(buyer: int | None, quotas: str) -> FundOfferSaleDTO:
    return FundOfferSaleDTO(
        day=date(2004, 3, 2),
        buyer_user_id=buyer,
        quotas=Decimal(quotas),
        price=Decimal(100),
    )


def test_buyers_list_players_by_quotas_and_sum_the_bots_in_one_line():
    users = [user(1, "ana"), user(2, "bruno"), user(3, "bot-a", bot=True)]
    users.append(user(4, "bot-b", bot=True))
    sales = [sale(1, "2"), sale(2, "5"), sale(3, "3"), sale(4, "4"), sale(1, "1")]

    result = builder()._buyers(sales, users)

    assert [(b.kind, b.nickname, b.quotas, b.color) for b in result] == [
        ("player", "bruno", 5, "chart-2"),
        ("player", "ana", 3, "chart-1"),
        ("bot", "Bots", 7, None),
    ]


def test_buyers_without_bots_have_no_bot_line():
    users = [user(1, "ana")]

    result = builder()._buyers([sale(1, "2")], users)

    assert [b.kind for b in result] == ["player"]
    assert builder()._buyers([], users) == []


def test_a_sale_without_buyer_is_the_market_maker():
    users = [user(1, "ana")]

    result = builder()._buyers([sale(1, "2"), sale(None, "4")], users)

    assert [(b.kind, b.user_id, b.nickname, b.quotas) for b in result] == [
        ("player", 1, "ana", 2),
        ("maker", None, "Formador de mercado", 4),
    ]


def test_holders_include_bots_and_the_maker_and_skip_empty_positions():
    users = [user(1, "ana"), user(2, "bruno"), user(3, "bot", bot=True)]
    sizes = {users[0].client_id: 60, users[1].client_id: 0, users[2].client_id: 30}
    positions = SimpleNamespace(
        get_positions=lambda c: {"AURA11": SimpleNamespace(size=Decimal(sizes[c]))}
    )
    engine = SimpleNamespace(broker=positions)
    holders_builder = FundDetailsBuilder(
        cast("FundBook", None),
        cast("SimulationEngine", engine),
        1,
        lambda: {1: "chart-1", 3: "chart-3"},
    )

    result = holders_builder._holders(fund_with(), users)

    assert [(h.kind, h.nickname, h.quotas, h.color) for h in result] == [
        ("player", "ana", 60, "chart-1"),
        ("bot", "bot", 30, "chart-3"),
        ("maker", "Formador de mercado", 10, None),
    ]
    assert [h.share for h in result] == [
        Decimal(60) / 110,
        Decimal(30) / 110,
        Decimal(10) / 110,
    ]
