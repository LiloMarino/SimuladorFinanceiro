"""O CDB da casa do Bancário: emissão mensal, taxa, teto, visibilidade, rotas e a política do bot."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core import repository
from backend.core.enum import (
    FixedIncomeType,
    IndicatorSeries,
    Profession,
    RateIndexType,
)
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.indicators import annualize_daily, monthly_average_rate
from backend.core.rates import Percent
from backend.core.runtime.user_manager import UserManager
from backend.core.utils import next_month_turn
from backend.features.fixed_income import house_cdb, treasury
from backend.features.fixed_income.market import FixedIncomeMarket
from backend.features.profession.banker import house_cdb_amount
from backend.features.profession.reserve import Reserve
from backend.features.simulation import simulation as simulation_module
from backend.features.simulation.simulation import Simulation
from backend.features.strategy.bots import resolve_bot
from backend.features.strategy.cdi import CdiReference
from backend.routes.dependencies import get_client_id
from backend.routes.operation import operation_router
from tests.conftest import SetIndicator
from tests.fakes import client, daily_series, monthly_series
from tests.test_bots import (  # noqa: F401
    person,
    refusal,
    room,
    rules,
    started,
)
from tests.test_clt import turn_of_month
from tests.test_profession_mechanics import match

OWNER = client("owner")
OTHER = client("other")
SELIC = Decimal("0.12")
IPCA = Decimal("0.04")
FIRST = date(2030, 10, 1)
CAP = Decimal(8000)
RICH = Decimal(100000)
HOUSE_NAMES = {"CDB da casa 1 ano", "CDB da casa 2 anos", "CDB da casa 3 anos"}


# =========================
# A regra pura
# =========================


def test_the_rate_is_the_treasury_prefixed_of_the_same_term_plus_one_point():
    assert house_cdb.house_rate(3, SELIC, IPCA) == Decimal("0.1245")
    for years in house_cdb.HOUSE_CDB_YEARS:
        tesouro = treasury.base_rate(
            RateIndexType.PREFIXADO, Decimal(years), SELIC, IPCA
        )
        assert house_cdb.house_rate(years, SELIC, IPCA) == tesouro + Decimal("0.01")


def test_the_issue_has_three_prefixed_cdbs_without_daily_liquidity(
    indicators: SetIndicator,
):
    indicators(
        IndicatorSeries.SELIC,
        daily_series(date(2030, 1, 1), date(2031, 1, 1), "0.0414"),
    )
    indicators(IndicatorSeries.IPCA, monthly_series(date(2030, 1, 1), 24, "0.33"))

    assets = house_cdb.issue(1, OWNER, date(2030, 10, 15), CAP)

    assert set(assets) == {1, 2, 3}
    assert {a.name for a in assets.values()} == HOUSE_NAMES
    for years, asset in assets.items():
        assert asset.investment_type is FixedIncomeType.CDB
        assert asset.rate_index is RateIndexType.PREFIXADO
        assert asset.daily_liquidity is False
        assert asset.player_cap == CAP
        assert asset.maturity_date == date(2030 + years, 10, 1)
        assert asset.offered_until == date(2030, 10, 31)


def test_the_uuids_are_stable_in_the_month_and_distinct_by_owner_and_month(
    indicators: SetIndicator,
):
    indicators(
        IndicatorSeries.SELIC,
        daily_series(date(2030, 1, 1), date(2031, 1, 1), "0.0414"),
    )
    indicators(IndicatorSeries.IPCA, monthly_series(date(2030, 1, 1), 24, "0.33"))

    mine = house_cdb.issue(1, OWNER, date(2030, 10, 1), CAP)
    again = house_cdb.issue(1, OWNER, date(2030, 10, 20), CAP)
    other = house_cdb.issue(1, OTHER, date(2030, 10, 1), CAP)
    next_month = house_cdb.issue(1, OWNER, date(2030, 11, 1), CAP)

    ids = {y: a.asset_uuid for y, a in mine.items()}
    assert ids == {y: a.asset_uuid for y, a in again.items()}
    assert not set(ids.values()) & {a.asset_uuid for a in other.values()}
    assert not set(ids.values()) & {a.asset_uuid for a in next_month.values()}


# =========================
# O catálogo e o dono
# =========================


@pytest.fixture
def economy(indicators: SetIndicator) -> None:
    indicators(
        IndicatorSeries.SELIC,
        daily_series(date(2018, 1, 1), date(2045, 1, 1), "0.0414"),
    )
    indicators(IndicatorSeries.IPCA, monthly_series(date(2018, 1, 1), 336, "0.33"))


@pytest.fixture
def house_market(
    monkeypatch: pytest.MonkeyPatch, economy: None, captured_events
) -> FixedIncomeMarket:
    monkeypatch.setattr(repository.fixed_income, "get_asset_by_uuid", lambda *_: None)
    result = FixedIncomeMarket(1, date(2040, 1, 1), start_date=date(2030, 9, 2))
    result.use_house_cdb(lambda day: {OWNER: CAP})
    return result


def test_the_market_issues_the_house_cdbs_only_to_the_owner(
    house_market: FixedIncomeMarket,
):
    house_market.refresh_assets(FIRST)

    assert {a.name for a in house_market.get_house_assets(OWNER)} == HOUSE_NAMES
    assert house_market.get_house_assets(OTHER) == []
    public = {a.name for a in house_market.get_available_assets()}
    assert not public & HOUSE_NAMES


def test_the_market_without_a_banker_issues_nothing(
    house_market: FixedIncomeMarket,
):
    house_market.use_house_cdb(lambda day: {})

    house_market.refresh_assets(FIRST)

    assert house_market.house_catalog() == []


def test_the_owner_resolves_the_asset_and_another_player_does_not(
    house_market: FixedIncomeMarket,
):
    house_market.refresh_assets(FIRST)
    asset = house_market.get_house_asset(OWNER, 3)
    assert asset is not None

    assert house_market.get_asset(OWNER, str(asset.asset_uuid)) == asset
    assert house_market.get_asset(OTHER, str(asset.asset_uuid)) is None


def test_the_emission_happens_once_a_month_at_the_first_tick_of_the_month(
    house_market: FixedIncomeMarket,
):
    calls: list[date] = []

    def caps(day: date) -> dict:
        calls.append(day)
        return {OWNER: CAP}

    house_market.use_house_cdb(caps)

    house_market.refresh_assets(FIRST)
    house_market.refresh_assets(date(2030, 10, 2))
    house_market.refresh_assets(date(2030, 10, 31))
    house_market.refresh_assets(date(2030, 11, 1))

    assert calls == [FIRST, date(2030, 11, 1)]


def test_the_offer_leaves_the_catalog_at_the_end_of_the_month_and_the_title_matures_later(
    house_market: FixedIncomeMarket,
):
    house_market.refresh_assets(FIRST)
    old = house_market.get_house_asset(OWNER, 1)
    assert old is not None

    house_market.refresh_assets(date(2030, 11, 1))

    now = {a.asset_uuid for a in house_market.get_house_assets(OWNER)}
    assert old.asset_uuid not in now
    assert old.offered_until == date(2030, 10, 31)
    assert house_market.get_asset(OWNER, str(old.asset_uuid)) == old
    assert house_market.get_asset(OTHER, str(old.asset_uuid)) is None


def test_a_reloaded_market_rebuilds_the_same_offers(
    house_market: FixedIncomeMarket, monkeypatch: pytest.MonkeyPatch
):
    house_market.refresh_assets(FIRST)
    before = house_market.get_house_assets(OWNER)
    reloaded = FixedIncomeMarket(1, date(2040, 1, 1), start_date=date(2030, 9, 2))
    reloaded.use_house_cdb(lambda day: {OWNER: CAP})

    reloaded.refresh_assets(FIRST)

    assert reloaded.get_house_assets(OWNER) == before
    asset = before[0]
    assert reloaded.get_asset(OTHER, str(asset.asset_uuid)) is None


# =========================
# A média de 24 meses da SELIC
# =========================


def test_the_average_takes_one_sample_per_month_at_the_first_trading_day(
    indicators: SetIndicator,
):
    # 1º de cada mês de 2030 num valor, e o resto dos dias em outro: só o 1º pregão conta
    values = daily_series(date(2030, 1, 1), date(2031, 12, 31), "0.0400")
    for month in range(1, 13):
        turn = next_month_turn(date(2030, month, 1) - timedelta(days=1))
        values[turn] = Decimal("0.0500")
    indicators(IndicatorSeries.SELIC, values)

    average = monthly_average_rate(IndicatorSeries.SELIC, date(2030, 12, 2), 12)

    assert average == annualize_daily(Percent(Decimal("0.0500")))


def test_the_average_skips_months_before_the_series_starts(indicators: SetIndicator):
    indicators(
        IndicatorSeries.SELIC,
        daily_series(date(2030, 1, 1), date(2031, 12, 31), "0.0400"),
    )

    with_gap = monthly_average_rate(IndicatorSeries.SELIC, date(2030, 3, 1), 24)
    short = monthly_average_rate(IndicatorSeries.SELIC, date(2030, 3, 1), 3)

    assert with_gap == short


def test_the_average_without_any_sample_is_empty(indicators: SetIndicator):
    indicators(IndicatorSeries.SELIC, {})

    assert monthly_average_rate(IndicatorSeries.SELIC, date(2030, 3, 1), 24) is None


# =========================
# A decisão do bot
# =========================


RESERVE = Reserve(cash=Decimal(30000), health_cost=Decimal(10000))


def test_the_amount_is_the_cap_when_the_cash_above_the_reserve_is_larger():
    amount = house_cdb_amount(Decimal("0.14"), Decimal("0.10"), Decimal(8000), RESERVE)

    assert amount == Decimal(8000)


def test_the_amount_is_the_cash_above_the_reserve_when_it_is_smaller_than_the_cap():
    amount = house_cdb_amount(Decimal("0.14"), Decimal("0.10"), Decimal(50000), RESERVE)

    assert amount == Decimal(20000)


def test_the_amount_is_zero_with_the_selic_at_or_below_the_average():
    assert house_cdb_amount(Decimal("0.10"), Decimal("0.10"), CAP, RESERVE) == 0
    assert house_cdb_amount(Decimal("0.09"), Decimal("0.10"), CAP, RESERVE) == 0


def test_the_amount_is_zero_below_the_reserve_and_without_series():
    broke = Reserve(cash=Decimal(9000), health_cost=Decimal(10000))

    assert house_cdb_amount(Decimal("0.14"), Decimal("0.10"), CAP, broke) == 0
    assert house_cdb_amount(None, Decimal("0.10"), CAP, RESERVE) == 0
    assert house_cdb_amount(Decimal("0.14"), None, CAP, RESERVE) == 0


# =========================
# Na partida
# =========================


pytestmark = pytest.mark.usefixtures("room")


def banker_match(monkeypatch: pytest.MonkeyPatch, **changes: object):
    """Uma partida com um Bancário (Ana) e um CLT (Beto), sem imprevistos, já na virada do primeiro mês com a emissão."""
    ana, beto = person("Ana"), person("Beto")
    sim = match(monkeypatch, **changes)
    sim.switch_profession(ana, Profession.BANKER)
    turn_of_month(sim)
    return sim, ana, beto


def net_salary_of(sim: Simulation, user) -> Decimal:
    day = sim.get_current_date().replace(day=1)
    assert sim._life is not None
    return sim._life_budget(sim._life, user.id).net_salary_on(day)


def house_of(sim: Simulation, user, years: int = 3):
    asset = sim._engine.fixed_income_market.get_house_asset(user.client_id, years)
    assert asset is not None
    return asset


def test_only_the_banker_gets_the_three_cdbs_at_the_first_trading_day(monkeypatch):
    sim, ana, beto = banker_match(monkeypatch)

    mine = sim.get_fixed_offers(ana.client_id)
    theirs = sim.get_fixed_offers(beto.client_id)

    house = [o for o in mine if o.profession_offer]
    assert {o.name for o in house} == HOUSE_NAMES
    assert not any(o.profession_offer for o in theirs)
    assert not {o.name for o in theirs} & HOUSE_NAMES


def test_the_cap_is_one_net_salary_per_cdb(monkeypatch):
    sim, ana, _ = banker_match(monkeypatch)
    salary = net_salary_of(sim, ana)

    caps = {years: house_of(sim, ana, years).player_cap for years in (1, 2, 3)}

    assert caps == {1: salary, 2: salary, 3: salary}
    assert salary > 0


def test_the_cap_of_each_cdb_is_independent(monkeypatch):
    sim, ana, _ = banker_match(monkeypatch, starting_cash=RICH)
    salary = net_salary_of(sim, ana)

    sim.buy_fixed_income(ana.client_id, house_of(sim, ana, 1), salary)
    sim.buy_fixed_income(ana.client_id, house_of(sim, ana, 2), salary)

    refusal(
        lambda: sim.buy_fixed_income(ana.client_id, house_of(sim, ana, 1), Decimal(1)),
        status=422,
    )
    sim.buy_fixed_income(ana.client_id, house_of(sim, ana, 3), salary)


def test_the_redeem_before_maturity_is_refused(monkeypatch):
    sim, ana, _ = banker_match(monkeypatch, starting_cash=RICH)
    asset = house_of(sim, ana)
    sim.buy_fixed_income(ana.client_id, asset, Decimal(1000))

    with pytest.raises(ConflictError):
        sim.redeem_fixed_income(ana.client_id, asset, Decimal(100))


def test_the_offer_leaves_the_catalog_after_the_month_but_the_position_stays(
    monkeypatch,
):
    sim, ana, _ = banker_match(monkeypatch, starting_cash=RICH)
    asset = house_of(sim, ana)
    sim.buy_fixed_income(ana.client_id, asset, Decimal(1000))

    turn_of_month(sim)

    assert asset.asset_uuid not in {
        o.asset_uuid for o in sim.get_fixed_offers(ana.client_id)
    }
    refusal(lambda: sim.buy_fixed_income(ana.client_id, asset, Decimal(100)))
    position = sim.get_fixed_positions(ana.client_id)[asset.asset_uuid]
    assert position.total_applied == Decimal(1000)


def test_the_position_reloads_from_the_events_after_the_room_is_rebuilt(monkeypatch):
    sim, ana, _ = banker_match(monkeypatch, starting_cash=RICH)
    asset = house_of(sim, ana)
    sim.buy_fixed_income(ana.client_id, asset, Decimal(1000))
    before = sim.get_fixed_positions(ana.client_id)[asset.asset_uuid]

    sim.clear_user_cache(ana.client_id)

    after = sim.get_fixed_positions(ana.client_id)[asset.asset_uuid]
    assert after.asset == before.asset
    assert after.total_applied == before.total_applied


def test_the_position_enters_the_networth_and_stays_out_of_the_coverable_cash(
    monkeypatch,
):
    sim, ana, _ = banker_match(monkeypatch, starting_cash=RICH)
    engine = sim._engine
    coverable = engine.coverable_cash(ana.client_id)
    worth = sim.get_portfolio(ana.client_id)

    sim.buy_fixed_income(ana.client_id, house_of(sim, ana), Decimal(1000))

    after = sim.get_portfolio(ana.client_id)
    assert after.fixed_income_value - worth.fixed_income_value == Decimal(1000)
    assert after.total_networth == worth.total_networth
    assert engine.coverable_cash(ana.client_id) == coverable - 1000


def test_the_other_player_does_not_see_quote_or_buy_the_offer(monkeypatch):
    sim, ana, beto = banker_match(monkeypatch, starting_cash=RICH)
    asset = house_of(sim, ana)
    uuid = str(asset.asset_uuid)

    assert sim.get_fixed_asset(beto.client_id, uuid) is None
    assert sim.get_fixed_offer(beto.client_id, uuid) is None
    assert sim.get_fixed_asset(ana.client_id, uuid) == asset


def http_as(user) -> TestClient:
    app = FastAPI()
    app.include_router(operation_router)
    app.dependency_overrides[get_client_id] = lambda: user.client_id
    return TestClient(app)


def test_the_routes_give_the_same_not_found_to_the_other_player(monkeypatch):
    sim, ana, beto = banker_match(monkeypatch, starting_cash=RICH)
    uuid = house_of(sim, ana).asset_uuid
    mine, theirs = http_as(ana), http_as(beto)

    assert str(uuid) in {o["asset_uuid"] for o in mine.get("/api/fixed-income").json()}
    listing = theirs.get("/api/fixed-income").json()
    assert str(uuid) not in {o["asset_uuid"] for o in listing}
    unknown = theirs.get("/api/fixed-income/00000000-0000-0000-0000-000000000000")
    for response in (
        theirs.get(f"/api/fixed-income/{uuid}"),
        theirs.get(f"/api/fixed-income/{uuid}/projection", params={"amount": 100}),
        theirs.post(f"/api/fixed-income/{uuid}/buy", json={"quantity": "100"}),
    ):
        assert response.status_code == 404
    assert unknown.status_code == 404
    assert theirs.get(f"/api/fixed-income/{uuid}").json() == unknown.json()

    bought = mine.post(f"/api/fixed-income/{uuid}/buy", json={"quantity": "100"})
    assert bought.status_code == 204, bought.text
    flagged = [o for o in mine.get("/api/fixed-income").json() if o["profession_offer"]]
    assert len(flagged) == 3


# =========================
# A política do Bancário-bot
# =========================


@pytest.fixture
def idle_strategy(monkeypatch: pytest.MonkeyPatch) -> None:
    """A estratégia de CDI deixa o caixa parado: o que o bot aplica sai direto do caixa."""
    monkeypatch.setattr(CdiReference, "next", lambda self, ctx, params: None)


def with_average(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    """A média de 24 meses da SELIC que a partida vê."""
    monkeypatch.setattr(
        simulation_module,
        "monthly_average_rate",
        lambda *_args, **_kwargs: Decimal(value),
    )


def banker_bot_match(
    monkeypatch: pytest.MonkeyPatch, profession: Profession = Profession.BANKER
):
    person("Ana")
    bot = UserManager.add_bot("Robô", resolve_bot("cdi_100", {}, profession=profession))
    return match(monkeypatch, starting_cash=RICH), bot


def applied_in_house(sim: Simulation, bot) -> Decimal:
    return sum(
        (
            p.total_applied
            for p in sim.get_fixed_positions(bot.client_id).values()
            if p.asset.issuer == house_cdb.ISSUER
        ),
        Decimal(0),
    )


def test_the_bot_applies_to_the_three_year_cdb_with_the_selic_above_the_average(
    idle_strategy, monkeypatch
):
    sim, bot = banker_bot_match(monkeypatch)
    with_average(monkeypatch, "0")

    turn_of_month(sim)

    [position] = [
        p
        for p in sim.get_fixed_positions(bot.client_id).values()
        if p.asset.issuer == house_cdb.ISSUER
    ]
    assert position.asset.name == "CDB da casa 3 anos"
    cap = house_of(sim, bot).player_cap
    assert cap is not None
    assert 0 < position.total_applied <= cap


def test_the_bot_does_not_apply_with_the_selic_below_the_average(
    idle_strategy, monkeypatch
):
    sim, bot = banker_bot_match(monkeypatch)
    with_average(monkeypatch, "9")

    turn_of_month(sim)

    assert applied_in_house(sim, bot) == 0


def test_the_bot_respects_the_reserve(idle_strategy, monkeypatch):
    person("Ana")
    bot = UserManager.add_bot(
        "Robô", resolve_bot("cdi_100", {}, profession=Profession.BANKER)
    )
    sim = match(monkeypatch, starting_cash=Decimal(1))
    with_average(monkeypatch, "0")

    turn_of_month(sim)

    assert applied_in_house(sim, bot) == 0


def test_the_human_banker_never_applies_by_policy(idle_strategy, monkeypatch):
    sim, ana, _ = banker_match(monkeypatch, starting_cash=RICH)
    with_average(monkeypatch, "0")

    turn_of_month(sim)

    assert (
        sum(
            (
                p.total_applied
                for p in sim.get_fixed_positions(ana.client_id).values()
                if p.asset.issuer == house_cdb.ISSUER
            ),
            Decimal(0),
        )
        == 0
    )


def test_the_bot_of_another_profession_never_applies(idle_strategy, monkeypatch):
    sim, bot = banker_bot_match(monkeypatch, Profession.CLT)
    with_average(monkeypatch, "0")

    turn_of_month(sim)

    assert applied_in_house(sim, bot) == 0
    assert sim._engine.fixed_income_market.get_house_assets(bot.client_id) == []


def test_the_bot_decides_only_at_the_month_turn(idle_strategy, monkeypatch):
    sim, bot = banker_bot_match(monkeypatch)
    with_average(monkeypatch, "0")

    sim.next_tick()

    assert sim.get_current_date().month == 3
    assert applied_in_house(sim, bot) == 0
