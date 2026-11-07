"""Tesouro Direto: curva de taxas, catálogo, emissão, preço a mercado, venda e o painel."""

from __future__ import annotations

import math
import threading
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_DOWN, Decimal
from typing import cast

import pytest

from backend.core import repository
from backend.core.dto.events.base_event import BaseEventDTO
from backend.core.dto.events.fixed_income import FixedIncomeEventDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.enum import (
    FixedIncomeEventType,
    FixedIncomeType,
    IndicatorSeries,
    InitialAccount,
    RateIndexType,
)
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.indicators import annual_index_rate
from backend.core.utils import last_day_of_month, next_business_day
from backend.features.economy.growth import MacroCourse
from backend.features.fixed_income import treasury, treasury_panel
from backend.features.fixed_income.accrual import (
    iof_rate,
    redemption_date,
    sale_breakdown,
)
from backend.features.fixed_income.entities.fixed_income_position import (
    FixedIncomePosition,
)
from backend.features.fixed_income.fixed_broker import FixedBroker, load_fixed_assets
from backend.features.fixed_income.liquidity import (
    loss_free,
    redeemable_today,
    sellable_any_day,
    total_redeemable,
)
from backend.features.fixed_income.market import FixedIncomeMarket
from backend.features.government import budget
from backend.features.government.budget import BudgetCourse
from backend.features.tax_policy import DEFAULT_TAX_POLICY
from tests.conftest import SetIndicator
from tests.fakes import FakeSimulationEngine, client, daily_series, monthly_series

START = date(2030, 9, 2)
FIRST_MONTH = date(2030, 10, 1)
INVESTOR = client("investor")
ASSET_ID = 7
CENT = Decimal("0.01")
PREMIUM = Decimal("0.02")

PREFIXED = RateIndexType.PREFIXADO
SELIC = RateIndexType.SELIC
IPCA = RateIndexType.IPCA


@pytest.fixture(autouse=True)
def economy(indicators: SetIndicator) -> None:
    """SELIC ~11% e IPCA ~4% ao ano, constantes, de 2018 a 2045."""
    indicators(
        IndicatorSeries.SELIC,
        daily_series(date(2018, 1, 1), date(2045, 1, 1), "0.0414"),
    )
    indicators(IndicatorSeries.IPCA, monthly_series(date(2018, 1, 1), 336, "0.33"))


@pytest.fixture
def fixed_income_db(
    monkeypatch: pytest.MonkeyPatch, captured_events: list[BaseEventDTO]
) -> None:
    """Banco de renda fixa em memória: sem histórico, e o ativo grava sempre com o mesmo id."""
    monkeypatch.setattr(
        repository.fixed_income, "get_events", lambda simulation_id, user_id: []
    )
    monkeypatch.setattr(
        repository.fixed_income, "get_or_create_asset", lambda asset: ASSET_ID
    )


def issued(
    rate_index: RateIndexType,
    nth: int = 0,
    month: date = FIRST_MONTH,
    premium: Decimal = Decimal(0),
) -> FixedIncomeAssetDTO:
    """O `nth` título (por vencimento) do indexador emitido no mês."""
    titles = sorted(
        (
            a
            for a in treasury.issue(1, START, month, premium).values()
            if a.rate_index is rate_index
        ),
        key=lambda a: a.maturity_date,
    )
    return titles[nth]


def cdb(daily_liquidity: bool = False) -> FixedIncomeAssetDTO:
    return FixedIncomeAssetDTO(
        name="CDB Teste",
        issuer="Banco Teste",
        investment_type=FixedIncomeType.CDB,
        rate_index=PREFIXED,
        maturity_date=date(2032, 1, 4),
        interest_rate=Decimal("0.12"),
        daily_liquidity=daily_liquidity,
    )


def position(
    asset: FixedIncomeAssetDTO,
    applied: str = "10000",
    current: str | None = None,
    bought: date = FIRST_MONTH,
) -> FixedIncomePosition:
    held = FixedIncomePosition(
        asset=asset, total_applied=Decimal(applied), first_applied_date=bought
    )
    if current is not None:
        held.current_value = Decimal(current)
    return held


# ---------------------------------------------------------------- curva de taxas


def test_prefixed_base_rate_follows_the_curve_of_the_term():
    """Prefixado = SELIC - 1 ponto + 0,15 ponto por ano de prazo: com 6,25 anos e SELIC 11,24%, 11,18%."""
    rate = treasury.base_rate(
        PREFIXED, Decimal("6.25"), Decimal("0.1124"), Decimal("0.0459")
    )

    assert rate == Decimal("0.111775")


def test_ipca_base_rate_is_the_real_spread_over_inflation():
    """IPCA+ = SELIC - IPCA + 0,10 ponto por ano: com 4,62 anos, SELIC 11,24% e IPCA 4,59%, 7,11%."""
    rate = treasury.base_rate(
        IPCA, Decimal("4.62"), Decimal("0.1124"), Decimal("0.0459")
    )

    assert rate == Decimal("0.07112")


@pytest.mark.parametrize("years", ["0.5", "3", "20"])
def test_selic_spread_is_flat_for_any_term(years: str):
    rate = treasury.base_rate(
        SELIC, Decimal(years), Decimal("0.1124"), Decimal("0.0459")
    )

    assert rate == treasury.SELIC_SPREAD


def test_cdi_is_not_a_treasury_index():
    with pytest.raises(ValueError, match="Tesouro"):
        treasury.base_rate(
            RateIndexType.CDI, Decimal(3), Decimal("0.1124"), Decimal("0.0459")
        )


def test_rate_on_is_the_base_of_the_first_of_the_month_plus_the_premium():
    maturity = date(2034, 1, 1)
    first = date(2030, 11, 1)
    rates = treasury.MarketRates.on(first)
    base = treasury.base_rate(
        PREFIXED, treasury.years_between(first, maturity), rates.selic, rates.ipca
    )

    on_first = treasury.rate_on(PREFIXED, maturity, first, PREMIUM)
    on_last = treasury.rate_on(PREFIXED, maturity, date(2030, 11, 29), PREMIUM)

    assert on_first == on_last == base + PREMIUM


def test_years_between_a_matured_title_is_zero():
    assert treasury.years_between(date(2031, 1, 1), date(2030, 1, 1)) == 0


@pytest.mark.parametrize(
    ("debt", "band"),
    [
        ("0", 0),
        ("0.5", 0),
        ("0.5001", 1),
        ("0.8", 1),
        ("0.8001", 2),
        ("1", 2),
        ("1.01", 3),
    ],
)
def test_debt_band_limits_belong_to_the_lower_band(debt: str, band: int):
    assert treasury.band_index(Decimal(debt)) == band


# ---------------------------------------------------------------- catálogo


def names(on: date) -> list[str]:
    return [t.name for t in treasury.catalog(START, on)]


def test_catalog_at_the_start_takes_the_nearest_maturity_that_meets_the_target():
    assert names(date(2030, 9, 1)) == [
        "Tesouro Selic 2034",
        "Tesouro Prefixado 2034",
        "Tesouro Prefixado 2038",
        "Tesouro IPCA+ 2036",
        "Tesouro IPCA+ 2041",
        "Tesouro IPCA+ 2051",
    ]


def test_each_title_is_sold_until_the_december_that_drops_it_below_its_floor():
    titles = treasury.catalog(START, date(2030, 9, 1))

    assert [t.sold_until for t in titles] == [
        date(2032, 12, 31),
        date(2032, 12, 31),
        date(2032, 12, 31),
        date(2033, 12, 31),
        date(2034, 12, 31),
        date(2036, 12, 31),
    ]
    assert all(t.replacement_name is None for t in titles)


def test_the_last_december_of_a_title_names_its_replacement():
    titles = treasury.catalog(START, date(2032, 12, 1))

    assert [(t.name, t.replacement_name) for t in titles[:3]] == [
        ("Tesouro Selic 2034", "Tesouro Selic 2036"),
        ("Tesouro Prefixado 2034", "Tesouro Prefixado 2037"),
        ("Tesouro Prefixado 2038", "Tesouro Prefixado 2041"),
    ]
    assert all(t.replacement_name is None for t in titles[3:])


def test_january_brings_the_replacement_into_the_catalog():
    assert names(date(2033, 1, 1)) == [
        "Tesouro Selic 2036",
        "Tesouro Prefixado 2037",
        "Tesouro Prefixado 2041",
        "Tesouro IPCA+ 2036",
        "Tesouro IPCA+ 2041",
        "Tesouro IPCA+ 2051",
    ]
    ipca_2036 = treasury.catalog(START, date(2033, 1, 1))[3]
    assert ipca_2036.replacement_name == "Tesouro IPCA+ 2039"


def test_catalog_keeps_swapping_year_after_year():
    assert names(date(2035, 1, 1)) == [
        "Tesouro Selic 2038",
        "Tesouro Prefixado 2037",
        "Tesouro Prefixado 2041",
        "Tesouro IPCA+ 2039",
        "Tesouro IPCA+ 2045",
        "Tesouro IPCA+ 2051",
    ]


def test_catalog_is_the_same_all_month_long():
    assert treasury.catalog(START, date(2031, 4, 1)) == treasury.catalog(
        START, date(2031, 4, 30)
    )


def months_from_start(years: int) -> Iterator[date]:
    first = treasury.month_start(START)
    while first.year < START.year + years:
        yield first
        first = last_day_of_month(first) + timedelta(days=1)


def test_every_title_keeps_its_floor_at_the_first_of_january_of_the_year():
    """Em 1º de janeiro o prazo de todo título à venda no ano está no piso ou acima."""
    for first in months_from_start(20):
        for title in treasury.catalog(START, first):
            new_year = date(first.year, 1, 1)
            assert (
                treasury.years_between(new_year, title.maturity)
                >= title.step.floor_years
            ), (first, title.name)
            assert title.sold_until.year >= first.year
            assert title.maturity > title.sold_until


def test_a_title_is_in_the_catalog_until_its_sold_until_and_never_after():
    first_catalog = treasury.catalog(START, FIRST_MONTH)
    for title in first_catalog:
        last_month = treasury.month_start(title.sold_until)
        assert title.name in names(last_month)
        assert title.name not in names(title.sold_until + timedelta(days=1))


# ---------------------------------------------------------------- emissão


def test_issue_locks_the_rate_with_the_premium_included():
    month = date(2030, 10, 15)
    rates = treasury.MarketRates.on(FIRST_MONTH)

    assets = treasury.issue(1, START, month, PREMIUM)

    assert len(assets) == 6
    for asset in assets.values():
        assert asset.investment_type is FixedIncomeType.TESOURO_DIRETO
        base = treasury.base_rate(
            asset.rate_index,
            treasury.years_between(FIRST_MONTH, asset.maturity_date),
            rates.selic,
            rates.ipca,
        )
        assert asset.interest_rate == base + PREMIUM
        assert asset.risk_premium == PREMIUM


def test_issue_without_premium_leaves_the_risk_premium_empty():
    assets = treasury.issue(1, START, FIRST_MONTH, Decimal(0))

    assert all(a.risk_premium is None for a in assets.values())


def test_offer_stays_open_until_the_end_of_the_month():
    assets = treasury.issue(1, START, date(2030, 10, 15), Decimal(0))

    assert {a.offered_until for a in assets.values()} == {date(2030, 10, 31)}


def test_issue_keys_the_assets_by_their_uuid():
    assets = treasury.issue(1, START, FIRST_MONTH, Decimal(0))

    assert all(key == str(a.asset_uuid) for key, a in assets.items())


def test_issue_uuids_are_stable_in_the_month_and_distinct_across_months_and_games():
    in_month = treasury.issue(1, START, date(2030, 10, 3), Decimal(0))
    again = treasury.issue(1, START, date(2030, 10, 28), PREMIUM)
    next_month = treasury.issue(1, START, date(2030, 11, 1), Decimal(0))
    other_game = treasury.issue(2, START, FIRST_MONTH, Decimal(0))

    assert set(in_month) == set(again)
    assert not set(in_month) & set(next_month)
    assert not set(in_month) & set(other_game)


@pytest.fixture
def market(monkeypatch: pytest.MonkeyPatch, captured_events) -> FixedIncomeMarket:
    monkeypatch.setattr(repository.fixed_income, "get_asset_by_uuid", lambda _: None)
    return FixedIncomeMarket(1, date(2040, 1, 1), start_date=START)


def test_market_offers_the_six_treasury_titles_every_month(market: FixedIncomeMarket):
    market.refresh_assets(FIRST_MONTH)

    offered = [
        a
        for a in market.get_available_assets()
        if a.investment_type is FixedIncomeType.TESOURO_DIRETO
    ]
    assert sorted(a.name for a in offered) == sorted(names(FIRST_MONTH))


def test_banks_do_not_draw_treasury_titles(market: FixedIncomeMarket):
    tesouro = 0
    day = FIRST_MONTH
    for _ in range(12):
        market.refresh_assets(day)
        others = [
            a
            for a in market.get_available_assets()
            if a.issuer != treasury.ISSUER
            and a.investment_type is FixedIncomeType.TESOURO_DIRETO
        ]
        tesouro += len(others)
        day = last_day_of_month(day) + timedelta(days=1)

    assert tesouro == 0


def test_an_old_issue_stays_resolvable_until_it_matures(market: FixedIncomeMarket):
    market.refresh_assets(FIRST_MONTH)
    [old] = [
        a for a in market.get_available_assets() if a.name == names(FIRST_MONTH)[0]
    ]

    market.refresh_assets(date(2030, 11, 1))

    assert old.asset_uuid not in {a.asset_uuid for a in market.get_available_assets()}
    assert market.get_asset(str(old.asset_uuid)) == old


# ---------------------------------------------------------------- preço a mercado


def test_selic_title_is_never_marked():
    asset = issued(SELIC)

    assert treasury.mark_factor(asset, date(2031, 6, 3), PREMIUM) == 1


def test_non_treasury_title_is_never_marked():
    assert treasury.mark_factor(cdb(), date(2031, 6, 3), PREMIUM) == 1


def test_a_matured_title_is_worth_its_curve():
    asset = issued(PREFIXED).model_copy(update={"maturity_date": date(2031, 1, 2)})

    assert treasury.mark_factor(asset, date(2031, 1, 2), PREMIUM) == 1


@pytest.mark.parametrize("rate_index", [PREFIXED, IPCA])
def test_price_is_the_curve_when_the_rate_did_not_move(rate_index: RateIndexType):
    """Comprado e vendido no mesmo mês e sem prêmio, a taxa de hoje é a da compra."""
    asset = issued(rate_index)

    assert treasury.mark_factor(asset, date(2030, 10, 24), Decimal(0)) == 1


@pytest.mark.parametrize("rate_index", [PREFIXED, IPCA])
def test_a_higher_rate_today_marks_the_price_down(rate_index: RateIndexType):
    """Com o prêmio de 2 pontos subindo depois da compra, o título comprado mais barato vale menos que a curva."""
    asset = issued(rate_index)

    factor = treasury.mark_factor(asset, date(2030, 10, 24), PREMIUM)

    assert Decimal("0.8") < factor < 1


@pytest.mark.parametrize("rate_index", [PREFIXED, IPCA])
def test_a_lower_rate_today_marks_the_price_up(rate_index: RateIndexType):
    """Comprado com prêmio e vendido sem ele, a taxa caiu e o título vale mais que a curva."""
    asset = issued(rate_index, premium=PREMIUM)

    factor = treasury.mark_factor(asset, date(2030, 10, 24), Decimal(0))

    assert 1 < factor < Decimal("1.2")


def test_the_longer_title_moves_more_than_the_shorter_one():
    """Por 2 pontos de alta, o Prefixado de 7 anos perde mais preço que o de 3."""
    short = issued(PREFIXED, 0)
    long = issued(PREFIXED, 1)
    today = date(2030, 10, 24)

    assert treasury.mark_factor(long, today, PREMIUM) < treasury.mark_factor(
        short, today, PREMIUM
    )


def test_market_value_and_mark_come_from_the_curve_amount():
    asset = issued(PREFIXED)
    held = position(asset, current="10500")
    today = date(2030, 10, 24)

    factor = treasury.mark_factor(asset, today, PREMIUM)

    assert held.market_value(today, PREMIUM) == Decimal("10500") * factor
    assert held.mark(today, PREMIUM) == held.market_value(today, PREMIUM) - Decimal(
        "10500"
    )


def test_a_selic_position_is_worth_its_curve():
    held = position(issued(SELIC), current="10500")

    assert held.market_value(date(2031, 3, 3), PREMIUM) == Decimal("10500")
    assert held.mark(date(2031, 3, 3), PREMIUM) == 0


# ---------------------------------------------------------------- venda a mercado


def test_full_sale_taxes_the_gain_over_the_applied_not_over_the_curve():
    """Aplicou 20.000, a curva rendeu 6.682,67 e a marcação tirou 2.416,42: o mercado vale 24.266,25; o IR de 15% é sobre o ganho real de 4.266,25."""
    sale = sale_breakdown(
        Decimal("24266.25"),
        Decimal(20000),
        FixedIncomeType.TESOURO_DIRETO,
        800,
        None,
    )

    assert sale.gross == Decimal("24266.25")
    assert sale.income_tax.quantize(CENT) == Decimal("639.94")
    assert sale.net == Decimal("23626.31")
    assert sale.remaining == 0


def test_partial_sale_taxes_only_the_gain_share_of_the_part_sold():
    """Mercado 9.427,81 sobre 8.000 aplicados: 15,1% do valor é ganho. Vendendo 3.000 aos 17,5% de IR, 454,37 de ganho pagam 79,51."""
    sale = sale_breakdown(
        Decimal("9427.81"),
        Decimal(8000),
        FixedIncomeType.TESOURO_DIRETO,
        500,
        Decimal(3000),
    )

    assert sale.gross == Decimal(3000)
    assert sale.income_tax.quantize(CENT) == Decimal("79.51")
    assert sale.net == Decimal("2920.49")
    assert sale.remaining == Decimal("6427.81")


def test_a_sale_below_the_applied_pays_no_income_tax():
    sale = sale_breakdown(
        Decimal(8000),
        Decimal(10000),
        FixedIncomeType.TESOURO_DIRETO,
        400,
        None,
    )

    assert sale.income_tax == 0
    assert sale.iof == 0
    assert sale.net == Decimal(8000)


def test_iof_still_charges_a_gain_sold_within_thirty_days():
    sale = sale_breakdown(
        Decimal(10100),
        Decimal(10000),
        FixedIncomeType.TESOURO_DIRETO,
        10,
        None,
    )

    assert sale.iof.quantize(CENT) == (Decimal(100) * iof_rate(10)).quantize(CENT)
    assert sale.iof > 0


def test_a_gross_above_the_market_sells_everything():
    sale = sale_breakdown(
        Decimal(9000),
        Decimal(8000),
        FixedIncomeType.TESOURO_DIRETO,
        500,
        Decimal(99999),
    )

    assert sale.gross == Decimal(9000)
    assert sale.remaining == 0


# ---------------------------------------------------------------- corretora


def broker_on(
    day: date, cash: str = "10000"
) -> tuple[FixedBroker, FakeSimulationEngine]:
    engine = FakeSimulationEngine(cash={INVESTOR: Decimal(cash)}, current_date=day)
    return FixedBroker(engine, threading.RLock()), engine


def tick_until(broker: FixedBroker, engine: FakeSimulationEngine, day: date) -> None:
    while engine.current_date < day:
        engine.current_date = next_business_day(engine.current_date)
        broker.apply_daily_interest(engine.current_date)


def redeem_events(events: list[BaseEventDTO]) -> list[FixedIncomeEventDTO]:
    return [
        e
        for e in events
        if isinstance(e, FixedIncomeEventDTO)
        and e.event_type is FixedIncomeEventType.REDEEM
    ]


@dataclass
class Holding:
    broker: FixedBroker
    engine: FakeSimulationEngine
    asset: FixedIncomeAssetDTO
    today: date


@pytest.fixture
def holding(fixed_income_db, captured_events) -> Holding:
    """10.000 aplicados num Prefixado em 1º/10/2030, vistos em 3/3/2031 com o prêmio de 2 pontos."""
    broker, engine = broker_on(FIRST_MONTH)
    asset = issued(PREFIXED)
    broker.buy(INVESTOR, asset, Decimal(10000))
    today = date(2031, 3, 3)
    tick_until(broker, engine, today)
    engine.use_risk_premium(lambda _day: PREMIUM)
    return Holding(broker, engine, asset, today)


def live(holding: Holding) -> FixedIncomePosition:
    return holding.broker.get_fixed_positions(INVESTOR)[holding.asset.asset_uuid]


def test_full_sale_credits_the_market_net_and_closes_the_position(
    holding: Holding, captured_events
):
    before = live(holding)
    curve = before.current_value
    market = before.market_value(holding.today, PREMIUM)
    expected = sale_breakdown(
        market,
        before.total_applied,
        FixedIncomeType.TESOURO_DIRETO,
        (holding.today - before.first_applied_date).days,
        None,
    )

    net = holding.broker.sell_treasury(INVESTOR, holding.asset, None)

    assert market < curve
    assert net == expected.net
    assert holding.engine.cash[INVESTOR] == expected.net
    assert holding.asset.asset_uuid not in holding.broker.get_fixed_positions(INVESTOR)
    [event] = redeem_events(captured_events)
    assert event.amount == curve.quantize(CENT)
    assert event.event_date == holding.today


def test_partial_sale_leaves_the_matching_share_of_the_curve(
    holding: Holding, captured_events
):
    before = live(holding)
    curve, applied = before.current_value, before.total_applied
    market = before.market_value(holding.today, PREMIUM)
    gross = (market / 2).quantize(CENT)

    net = holding.broker.sell_treasury(INVESTOR, holding.asset, gross)

    after = live(holding)
    [event] = redeem_events(captured_events)
    curve_part = (gross / market * curve).quantize(CENT)
    assert event.amount == curve_part
    assert after.current_value == curve - curve_part
    assert after.total_applied == pytest.approx(
        applied * (1 - curve_part / curve), abs=Decimal("0.0001")
    )
    assert after.market_value(holding.today, PREMIUM) == pytest.approx(
        market - gross, abs=CENT
    )
    assert holding.engine.cash[INVESTOR] == net
    assert net <= gross


def test_selling_all_but_a_fraction_of_a_cent_sells_everything(holding: Holding):
    market = live(holding).market_value(holding.today, PREMIUM)

    holding.broker.sell_treasury(
        INVESTOR, holding.asset, market.quantize(CENT, ROUND_DOWN)
    )

    assert holding.asset.asset_uuid not in holding.broker.get_fixed_positions(INVESTOR)


def test_selling_more_than_the_market_value_is_rejected(
    holding: Holding, captured_events
):
    market = live(holding).market_value(holding.today, PREMIUM)

    with pytest.raises(UnprocessableEntityError):
        holding.broker.sell_treasury(INVESTOR, holding.asset, market + 1)

    assert holding.engine.cash[INVESTOR] == 0
    assert redeem_events(captured_events) == []
    assert holding.asset.asset_uuid in holding.broker.get_fixed_positions(INVESTOR)


@pytest.mark.parametrize("gross", ["0", "-5"])
def test_a_non_positive_gross_is_rejected(holding: Holding, gross: str):
    with pytest.raises(UnprocessableEntityError):
        holding.broker.sell_treasury(INVESTOR, holding.asset, Decimal(gross))


def test_only_treasury_titles_sell_at_market(holding: Holding):
    with pytest.raises(ConflictError):
        holding.broker.sell_treasury(INVESTOR, cdb(daily_liquidity=True), None)


def test_selling_a_title_without_a_position_is_rejected(holding: Holding):
    other = issued(PREFIXED, 1)

    with pytest.raises(NotFoundError):
        holding.broker.sell_treasury(INVESTOR, other, None)


def test_replay_of_a_partial_sale_matches_the_live_position(
    holding: Holding, captured_events, monkeypatch: pytest.MonkeyPatch
):
    market = live(holding).market_value(holding.today, PREMIUM)
    holding.broker.sell_treasury(INVESTOR, holding.asset, (market / 3).quantize(CENT))
    tick_until(holding.broker, holding.engine, date(2031, 3, 12))
    monkeypatch.setattr(
        repository.fixed_income,
        "get_events",
        lambda simulation_id, user_id: [
            (holding.asset, e)
            for e in captured_events
            if isinstance(e, FixedIncomeEventDTO)
        ],
    )

    rebuilt = load_fixed_assets(1, INVESTOR, holding.engine.current_date)[
        holding.asset.asset_uuid
    ]

    now = live(holding)
    assert rebuilt.current_value.quantize(CENT) == now.current_value.quantize(CENT)
    assert rebuilt.total_applied.quantize(CENT) == now.total_applied.quantize(CENT)
    assert rebuilt.first_applied_date == now.first_applied_date


def test_a_title_that_left_the_catalog_is_still_sellable(holding: Holding):
    later = date(2033, 6, 1)
    tick_until(holding.broker, holding.engine, later)

    net = holding.broker.sell_treasury(INVESTOR, holding.asset, None)

    assert holding.asset.name not in names(later)
    assert net > 0
    assert holding.engine.cash[INVESTOR] == net


# ---------------------------------------------------------------- liquidez


@pytest.mark.parametrize(
    ("make_asset", "sellable", "free_of_loss"),
    [
        (lambda: cdb(daily_liquidity=True), True, True),
        (lambda: cdb(daily_liquidity=False), False, False),
        (lambda: issued(PREFIXED), True, False),
        (lambda: issued(IPCA), True, False),
        (lambda: issued(SELIC), True, True),
    ],
    ids=[
        "cdb-daily",
        "cdb-locked",
        "tesouro-prefixed",
        "tesouro-ipca",
        "tesouro-selic",
    ],
)
def test_liquidity_comes_from_the_type_of_the_title(
    make_asset: Callable[[], FixedIncomeAssetDTO], sellable: bool, free_of_loss: bool
):
    asset = make_asset()
    assert sellable_any_day(asset) is sellable
    assert loss_free(asset) is free_of_loss


def test_treasury_is_redeemable_today_at_its_market_net():
    held = position(issued(PREFIXED), current="10500")
    today = date(2030, 10, 24)

    net = redeemable_today(held, today, DEFAULT_TAX_POLICY, PREMIUM)

    assert net == held.sell_breakdown(today, None, PREMIUM, DEFAULT_TAX_POLICY).net


def test_a_locked_cdb_is_not_redeemable_today():
    assert redeemable_today(position(cdb()), date(2030, 10, 24)) is None


def test_total_redeemable_counts_treasury_and_skips_locked_titles():
    treasury_position = position(issued(PREFIXED), current="10500")
    today = date(2030, 10, 24)
    expected = redeemable_today(treasury_position, today, DEFAULT_TAX_POLICY, PREMIUM)

    total = total_redeemable(
        [treasury_position, position(cdb())], today, DEFAULT_TAX_POLICY, PREMIUM
    )

    assert total == expected


def test_net_worth_counts_the_treasury_at_the_market_price():
    engine = FakeSimulationEngine(current_date=date(2030, 10, 24))
    engine.use_risk_premium(lambda _day: PREMIUM)
    held = position(issued(PREFIXED), current="10500")
    selic = position(issued(SELIC), current="3000")

    value = engine.fixed_market_value([held, selic])

    assert value == held.market_value(engine.current_date, PREMIUM) + Decimal(3000)
    assert value < Decimal(13500)


# ---------------------------------------------------------------- painel


def test_catalog_panel_shows_the_six_titles_with_locked_rate_open_in_base_and_premium():
    today = date(2030, 10, 15)
    assets = treasury.issue(1, START, today, PREMIUM).values()

    panel = treasury_panel.build_catalog(START, today, assets, None, True)

    assert panel.next_review == date(2030, 11, 1)
    assert panel.thermometer is None
    assert [t.name for t in panel.titles] == names(today)
    for title in panel.titles:
        assert title.premium == PREMIUM
        assert title.base_rate + title.premium == title.rate
        assert title.effective_annual_rate is not None
        assert title.months_to_maturity > 0


def test_catalog_panel_hides_the_equivalent_rate_when_the_game_asks():
    today = date(2030, 10, 15)
    assets = treasury.issue(1, START, today, Decimal(0)).values()

    panel = treasury_panel.build_catalog(START, today, assets, None, False)

    assert all(t.effective_annual_rate is None for t in panel.titles)
    assert all(t.premium == 0 for t in panel.titles)


def test_catalog_panel_review_date_rolls_over_the_year():
    today = date(2030, 12, 20)
    assets = treasury.issue(1, START, today, Decimal(0)).values()

    panel = treasury_panel.build_catalog(START, today, assets, None, True)

    assert panel.next_review == date(2031, 1, 1)


def test_history_has_one_point_per_month_with_the_rates_of_the_first_day():
    points = treasury.history(START, date(2031, 3, 15), lambda _day: PREMIUM, None)

    history = treasury_panel.build_history(points, True)

    assert [h.month for h in history] == [
        date(2030, 9, 1),
        date(2030, 10, 1),
        date(2030, 11, 1),
        date(2030, 12, 1),
        date(2031, 1, 1),
        date(2031, 2, 1),
        date(2031, 3, 1),
    ]
    first = history[0]
    assert first.selic == annual_index_rate(IndicatorSeries.SELIC, date(2030, 9, 1))
    assert first.ipca == annual_index_rate(IndicatorSeries.IPCA, date(2030, 9, 1))
    assert first.premium == PREMIUM
    assert first.debt is None
    assert first.band_index is None
    assert len(first.quotes) == 6
    assert all(q.effective_annual_rate is not None for q in first.quotes)


def test_history_follows_the_catalog_swap_and_hides_the_equivalent_rate():
    points = treasury.history(START, date(2033, 2, 1), lambda _day: Decimal(0), None)

    history = treasury_panel.build_history(points, False)

    december, january = history[-3], history[-2]
    assert december.month == date(2032, 12, 1)
    assert [q.name for q in december.quotes] == names(date(2032, 12, 1))
    assert [q.name for q in january.quotes] == names(date(2033, 1, 1))
    assert all(q.effective_annual_rate is None for h in history for q in h.quotes)


def test_history_places_the_debt_in_its_band():
    debts = {
        date(2030, 9, 1): Decimal("0.45"),
        date(2030, 10, 1): Decimal("0.9"),
    }
    points = treasury.history(
        START, date(2030, 10, 1), lambda _day: Decimal(0), lambda day: debts[day]
    )

    history = treasury_panel.build_history(points, True)

    assert [(h.debt, h.band_index) for h in history] == [
        (Decimal("0.45"), 0),
        (Decimal("0.9"), 2),
    ]


@dataclass
class ClosedMonth:
    month_end: date
    debt: Decimal
    premium: Decimal


class StubBudget:
    """O orçamento reduzido ao que o termômetro lê: os meses fechados e o último deles."""

    def __init__(self, months: list[ClosedMonth]):
        self._months = months

    def months_until(self, day: date) -> list[ClosedMonth]:
        return [m for m in self._months if m.month_end <= day]

    def latest(self, day: date) -> ClosedMonth:
        return self.months_until(day)[-1]


def debt_course(debts: list[str]) -> BudgetCourse:
    """Um mês fechado por dívida, a partir de janeiro de 2020, com o prêmio da dívida do mês."""
    months: list[ClosedMonth] = []
    first = date(2020, 1, 1)
    for debt in debts:
        months.append(
            ClosedMonth(
                last_day_of_month(first), Decimal(debt), budget.premium(Decimal(debt))
            )
        )
        first = last_day_of_month(first) + timedelta(days=1)
    return cast(BudgetCourse, StubBudget(months))


def test_thermometer_reads_the_band_and_the_gap_to_the_next_one():
    course = debt_course(["0.7"])

    thermometer = treasury_panel.build_thermometer(course, date(2020, 2, 10))

    assert thermometer.band == "Moderado"
    assert thermometer.band_index == 1
    assert thermometer.debt == Decimal("0.7")
    assert thermometer.premium == budget.premium(Decimal("0.7"))
    assert thermometer.next_band == "Alto"
    assert thermometer.next_band_limit == Decimal("0.8")
    assert thermometer.debt_to_next_band == Decimal("0.1")
    assert thermometer.premium_per_debt_point == budget.premium(
        Decimal("0.71")
    ) - budget.premium(Decimal("0.7"))
    assert thermometer.premium_per_debt_point > 0


def test_thermometer_has_no_pace_before_twelve_closed_months():
    course = debt_course(["0.70", "0.71", "0.72"])

    thermometer = treasury_panel.build_thermometer(course, date(2020, 3, 31))

    assert thermometer.debt_change_12m is None
    assert thermometer.months_to_next_band is None


def test_thermometer_projects_the_months_to_the_next_band_at_the_yearly_pace():
    """Dívida de 70% a 76% em 12 meses (0,5 ponto por mês): faltam 4 pontos para 80%, 8 meses."""
    debts = [f"{Decimal('0.70') + Decimal('0.005') * i:.3f}" for i in range(13)]
    course = debt_course(debts)

    thermometer = treasury_panel.build_thermometer(course, date(2021, 1, 31))

    assert thermometer.debt == Decimal("0.760")
    assert thermometer.debt_change_12m == Decimal("0.060")
    assert thermometer.debt_to_next_band == Decimal("0.040")
    assert thermometer.months_to_next_band == math.ceil(
        Decimal("0.040") / (Decimal("0.060") / 12)
    )
    assert thermometer.months_to_next_band == 8


def test_thermometer_has_no_forecast_when_the_debt_is_not_rising():
    debts = [f"{Decimal('0.75') - Decimal('0.002') * i:.3f}" for i in range(13)]
    course = debt_course(debts)

    thermometer = treasury_panel.build_thermometer(course, date(2021, 1, 31))

    assert thermometer.debt_change_12m is not None
    assert thermometer.debt_change_12m < 0
    assert thermometer.months_to_next_band is None
    assert thermometer.next_band == "Alto"


def test_thermometer_in_the_top_band_has_no_next_one():
    course = debt_course(["1.05"])

    thermometer = treasury_panel.build_thermometer(course, date(2020, 2, 10))

    assert thermometer.band == "Crítico"
    assert thermometer.band_index == 3
    assert thermometer.next_band is None
    assert thermometer.next_band_limit is None
    assert thermometer.debt_to_next_band is None
    assert thermometer.months_to_next_band is None


def test_thermometer_with_the_real_budget_is_consistent_with_its_band():
    real = BudgetCourse(
        date(2020, 1, 1),
        lambda _day: DEFAULT_TAX_POLICY,
        budget.initial_account(date(2020, 1, 1), InitialAccount.PLAYABLE),
        MacroCourse(date(2020, 1, 1)),
    )

    thermometer = treasury_panel.build_thermometer(real, date(2021, 3, 15))

    assert thermometer.band_index == treasury.band_index(thermometer.debt)
    assert thermometer.band == treasury.BAND_NAMES[thermometer.band_index]
    assert thermometer.debt_change_12m is not None
    assert thermometer.premium == real.premium_on(date(2021, 3, 15))


def sale_position() -> tuple[FixedIncomePosition, date]:
    asset = issued(PREFIXED)
    return position(asset, applied="20000", current="26682.67"), date(2031, 3, 3)


def test_position_panel_splits_yield_from_marking():
    held, today = sale_position()

    panel = treasury_panel.build_position(held, today, PREMIUM)

    assert panel.total_applied == Decimal(20000)
    assert panel.yield_amount == Decimal("6682.67")
    assert panel.mark == panel.market_value - Decimal("26682.67")
    assert panel.mark < 0
    assert panel.bought_rate == held.asset.interest_rate
    assert panel.today_rate == treasury.rate_on(
        PREFIXED, held.asset.maturity_date, today, PREMIUM
    )
    assert panel.today_rate > panel.bought_rate


def test_sale_quote_adds_up_to_the_gross_sold():
    """Aplicado + rendimento da curva + marcação reconstituem o bruto vendido."""
    held, today = sale_position()
    market = held.market_value(today, PREMIUM)
    amount = (market / 2).quantize(CENT)

    quote = treasury_panel.build_sale_quote(
        held, amount, Decimal(500), today, PREMIUM, DEFAULT_TAX_POLICY
    )

    assert quote.max_amount == market
    assert quote.applied_amount is not None
    assert quote.yield_amount is not None
    assert quote.mark is not None
    assert quote.applied_amount + quote.yield_amount + quote.mark == amount
    assert quote.mark < 0
    assert quote.net_amount is not None
    assert quote.iof is not None
    assert quote.income_tax is not None
    assert quote.net_amount == amount - quote.iof - quote.income_tax
    assert quote.cash_before == 500
    assert quote.cash_after == 500 + quote.net_amount
    assert quote.remaining == pytest.approx(market - amount, abs=Decimal("0.0001"))
    assert quote.full is False
    assert quote.days_held == (today - FIRST_MONTH).days
    assert quote.maturity_date == redemption_date(held.asset.maturity_date)


def test_sale_quote_compares_with_waiting_for_the_maturity():
    held, today = sale_position()
    market = held.market_value(today, PREMIUM)

    quote = treasury_panel.build_sale_quote(
        held, market / 2, Decimal(0), today, PREMIUM, DEFAULT_TAX_POLICY
    )

    assert quote.maturity_gross_amount is not None
    assert quote.maturity_income_tax is not None
    assert quote.maturity_net_amount is not None
    # Esperar rende mais bruto que o preço de hoje, e o líquido sai do bruto menos o IR
    assert quote.maturity_gross_amount > quote.maturity_net_amount
    assert quote.maturity_net_amount == pytest.approx(
        quote.maturity_gross_amount - quote.maturity_income_tax, abs=CENT
    )
    assert quote.net_amount is not None
    assert quote.maturity_net_amount > quote.net_amount


def test_selling_the_whole_market_value_quotes_a_full_sale():
    held, today = sale_position()
    market = held.market_value(today, PREMIUM)

    quote = treasury_panel.build_sale_quote(
        held, market, Decimal(0), today, PREMIUM, DEFAULT_TAX_POLICY
    )

    assert quote.full is True
    assert quote.remaining == 0


@pytest.mark.parametrize("which", ["zero", "above"])
def test_sale_quote_leaves_the_values_empty_for_an_amount_that_cannot_be_sold(
    which: str,
):
    held, today = sale_position()
    market = held.market_value(today, PREMIUM)
    amount = Decimal(0) if which == "zero" else market + 1

    quote = treasury_panel.build_sale_quote(
        held, amount, Decimal(500), today, PREMIUM, DEFAULT_TAX_POLICY
    )

    assert quote.max_amount == market
    assert quote.full is False
    assert quote.cash_before == 500
    for empty in (
        quote.applied_amount,
        quote.yield_amount,
        quote.mark,
        quote.iof,
        quote.income_tax,
        quote.net_amount,
        quote.cash_after,
        quote.remaining,
        quote.maturity_gross_amount,
        quote.maturity_income_tax,
        quote.maturity_net_amount,
    ):
        assert empty is None
