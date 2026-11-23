"""O Corretor: a comissão sobre o volume da sala, o relatório mensal da casa, o placar, a tabela da partida, o selo e a política do bot."""

from __future__ import annotations

import random
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from backend.core import repository
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.house_report import HouseRecommendationDTO
from backend.core.dto.profession import BrokerState
from backend.core.dto.profession_page import BrokerMechanicDTO
from backend.core.enum import (
    AssetClass,
    EquityEventType,
    HouseResult,
    MechanicStatus,
    OrderAction,
    Profession,
)
from backend.core.house_report import (
    COMMISSION_CAP,
    COMMISSION_RATE,
    Candidate,
    Draft,
    Verdict,
    commission,
    deadline_of,
    draw_report,
    hit_rate,
    judge,
    next_report_on,
    previous_month_start,
    reached,
    report_day,
)
from backend.core.life_budget import LifeBudget
from backend.core.models.models import Portfolios
from backend.core.runtime.user_manager import UserManager
from backend.features.profession.broker import (
    bot_budget_each,
    bot_buys,
    tradable_today,
    verdicts_of,
)
from backend.features.strategy.bots import resolve_bot
from tests.fakes import client, simulation_settings
from tests.test_bots import (  # noqa: F401
    person,
    professions_rules,
    room,
    started,
)
from tests.test_profession_mechanics import match

SALARY = Decimal(5000)
START = date(2004, 3, 29)


def broker_budget(state: BrokerState | None = None) -> LifeBudget:
    life = LifeBudget(
        monthly_salary=SALARY,
        monthly_expense=Decimal(3000),
        withdrawal_rate=Decimal("0.04"),
        inflation_adjusted=False,
        start_date=START,
    ).for_profession(Profession.BROKER)
    return life.with_mechanic_state(lambda: state or BrokerState())


# --- A renda: a parte fixa e a comissão


def test_the_fixed_part_is_seventy_percent_of_the_room_salary():
    assert broker_budget().net_salary_on(START) == Decimal(3500)
    assert broker_budget().fixed_income_on(START) == Decimal(3500)


def test_the_commission_is_the_fraction_of_the_volume_split_among_the_brokers():
    # 0,05% de R$ 2.000.000 = R$ 1.000, dividido entre 4 Corretores
    result = commission(Decimal(2_000_000), 4, Decimal(3500))

    assert Decimal("0.0005") == COMMISSION_RATE
    assert result.amount == Decimal(250)
    assert not result.capped


def test_the_commission_stops_at_one_times_the_fixed_part():
    # 0,05% de R$ 20.000.000 = R$ 10.000 para um Corretor só: corta em R$ 3.500
    result = commission(Decimal(20_000_000), 1, Decimal(3500))

    assert COMMISSION_CAP == 1
    assert result.amount == Decimal(3500)
    assert result.uncapped == Decimal(10_000)
    assert result.capped


def test_a_room_that_traded_nothing_pays_only_the_fixed_part():
    state = BrokerState(volume=Decimal(0), brokers=3)

    assert commission(Decimal(0), 3, Decimal(3500)).amount == 0
    assert broker_budget(state).net_salary_on(START) == Decimal(3500)


def test_the_income_adds_the_commission_to_the_fixed_part_up_to_one_point_four():
    split = BrokerState(volume=Decimal(2_000_000), brokers=4)
    capped = BrokerState(volume=Decimal(200_000_000), brokers=1)

    assert broker_budget(split).net_salary_on(START) == Decimal(3750)
    assert broker_budget(capped).net_salary_on(START) == Decimal(7000)


def test_the_broker_has_no_layoff_and_no_market_driver():
    budget = broker_budget(BrokerState(volume=Decimal(2_000_000), brokers=4))

    assert budget.income_loss() is None
    assert budget.rule.driver is None
    assert budget.net_salary_on(START, income_lost=True) == Decimal(3750)


def test_the_commission_belongs_to_the_broker_only():
    budget = LifeBudget(
        monthly_salary=SALARY,
        monthly_expense=Decimal(3000),
        withdrawal_rate=Decimal("0.04"),
        inflation_adjusted=False,
        start_date=START,
    ).for_profession(Profession.CLT)

    clt = budget.with_mechanic_state(
        lambda: BrokerState(volume=Decimal(10**9), brokers=1)
    )

    assert clt.net_salary_on(START) == SALARY


def test_the_volume_of_the_month_that_closed_is_read_from_the_first_to_the_last_day():
    assert previous_month_start(date(2004, 5, 3)) == date(2004, 4, 1)
    assert previous_month_start(date(2004, 1, 5)) == date(2003, 12, 1)


# --- O volume que conta


@pytest.fixture
def traded(database: Engine) -> tuple[int, int, Engine]:
    """Um jogador com a carteira, uma carteira sem dono e uma ação de cada classe numa partida; devolve `(simulation_id, portfolio_id, engine)`."""
    user = repository.user.create_user(client("Ana"), "Ana")
    for ticker, asset_class in (
        ("ACAO3", AssetClass.STOCK),
        ("FIIX11", AssetClass.FII),
        ("ETFX11", AssetClass.ETF),
        ("BDRX34", AssetClass.BDR),
        ("BTC", AssetClass.CRYPTO),
        ("FUNDA", AssetClass.FUND),
    ):
        repository.stock.add_stock(ticker, ticker, asset_class)
    simulation_id = repository.simulation.create_simulation(simulation_settings())
    portfolio_id = repository.portfolio.create(simulation_id, [user.id])[user.id]
    return simulation_id, portfolio_id, database


def equity(
    simulation_id: int,
    portfolio_id: int,
    ticker: str,
    kind: EquityEventType,
    *,
    day: date = date(2004, 4, 6),
    quantity: str = "10",
    price: str = "100",
) -> EquityEventDTO:
    return EquityEventDTO(
        simulation_id=simulation_id,
        portfolio_id=portfolio_id,
        event_date=day,
        ticker=ticker,
        event_type=kind,
        quantity=Decimal(quantity),
        price=Decimal(price),
    )


def test_the_volume_counts_buys_and_sells_of_stocks_fiis_etfs_and_bdrs(traded):
    simulation_id, portfolio_id, _ = traded
    buy, sell = EquityEventType.BUY, EquityEventType.SELL

    repository.event.insert_many(
        [
            equity(simulation_id, portfolio_id, "ACAO3", buy),
            equity(simulation_id, portfolio_id, "FIIX11", sell),
            equity(simulation_id, portfolio_id, "ETFX11", buy),
            equity(simulation_id, portfolio_id, "BDRX34", sell),
        ]
    )

    volume = repository.event.get_traded_volume(
        simulation_id, date(2004, 4, 1), date(2004, 5, 1)
    )
    assert volume == Decimal(4000)


def test_the_volume_leaves_out_crypto_fund_shares_and_the_other_events(traded):
    simulation_id, portfolio_id, _ = traded

    repository.event.insert_many(
        [
            equity(simulation_id, portfolio_id, "BTC", EquityEventType.BUY),
            equity(simulation_id, portfolio_id, "FUNDA", EquityEventType.BUY),
            equity(simulation_id, portfolio_id, "ACAO3", EquityEventType.SPLIT),
            equity(simulation_id, portfolio_id, "ACAO3", EquityEventType.FRACTION_SELL),
            equity(simulation_id, portfolio_id, "ACAO3", EquityEventType.BUY),
        ]
    )

    assert repository.event.get_traded_volume(
        simulation_id, date(2004, 4, 1), date(2004, 5, 1)
    ) == Decimal(1000)


def test_the_volume_leaves_out_portfolios_without_a_player_and_other_months(traded):
    simulation_id, portfolio_id, engine = traded
    with Session(engine) as session:
        orphan = Portfolios(
            simulation_id=simulation_id,
            user_id=None,
            created_at=datetime.now(UTC),
            starting_cash=Decimal(0),
        )
        session.add(orphan)
        session.commit()
        orphan_id = orphan.id
    buy = EquityEventType.BUY

    repository.event.insert_many(
        [
            equity(simulation_id, orphan_id, "ACAO3", buy),
            equity(simulation_id, portfolio_id, "ACAO3", buy, day=date(2004, 3, 31)),
            equity(simulation_id, portfolio_id, "ACAO3", buy, day=date(2004, 5, 3)),
            equity(simulation_id, portfolio_id, "ACAO3", buy, day=date(2004, 4, 1)),
        ]
    )

    assert repository.event.get_traded_volume(
        simulation_id, date(2004, 4, 1), date(2004, 5, 1)
    ) == Decimal(1000)


# --- O dia do relatório


def test_the_report_comes_on_the_fifth_business_day_of_the_month():
    # Abril de 2004 começa numa quinta: 1, 2, 5, 6 e 7
    assert report_day(date(2004, 4, 1)) == date(2004, 4, 7)
    # Março de 2004 começa numa segunda: 5 é a sexta
    assert report_day(date(2004, 3, 1)) == date(2004, 3, 5)
    # Fevereiro de 2004 começa num domingo: 2, 3, 4, 5 e 6
    assert report_day(date(2004, 2, 1)) == date(2004, 2, 6)


def test_a_match_that_starts_after_the_day_gets_the_first_report_next_month():
    started_on = date(2004, 3, 29)

    assert next_report_on(started_on, set()) == date(2004, 4, 7)


def test_the_next_report_is_this_months_until_it_comes_and_next_months_after():
    month = date(2004, 4, 1)

    assert next_report_on(date(2004, 4, 6), set()) == date(2004, 4, 7)
    assert next_report_on(date(2004, 4, 7), set()) == date(2004, 4, 7)
    assert next_report_on(date(2004, 4, 7), {month}) == date(2004, 5, 7)
    assert next_report_on(date(2004, 4, 20), {month}) == date(2004, 5, 7)


# --- O sorteio


def walk(seed: int, price: Decimal, start: date, days: int) -> Candidate:
    """Um passeio aleatório de máxima e mínima por dia útil depois de `start`."""
    rng = random.Random(seed)
    rows: list[tuple[date, Decimal, Decimal]] = []
    close = price
    day = start
    for _ in range(days):
        day += timedelta(days=1)
        if day.weekday() >= 5:
            continue
        close = close * Decimal(str(1 + rng.gauss(0.0005, 0.02)))
        rows.append(
            (
                day,
                close * Decimal("1.005"),
                close * Decimal("0.995"),
            )
        )
    return Candidate(f"T{seed}", price, rows)


def universe(size: int, start: date, days: int = 130) -> list[Candidate]:
    return [walk(seed, Decimal(100), start, days) for seed in range(size)]


DAY = date(2004, 4, 7)
END = date(2004, 12, 31)


def test_a_report_has_three_to_five_stocks():
    sizes = {
        len(draw_report(f"seed-{n}", DAY, END, universe(12, DAY))) for n in range(40)
    }

    assert sizes <= {3, 4, 5}
    assert sizes == {3, 4, 5}


def test_each_deadline_is_the_end_of_a_month_one_to_three_months_ahead():
    ends = {date(2004, 5, 31), date(2004, 6, 30), date(2004, 7, 31)}

    deadlines = {
        draft.deadline
        for n in range(30)
        for draft in draw_report(f"seed-{n}", DAY, END, universe(12, DAY))
    }

    assert deadlines == ends


def test_the_deadline_never_passes_the_end_of_the_match():
    end = date(2004, 5, 20)

    drafts = [
        draft
        for n in range(20)
        for draft in draw_report(f"seed-{n}", DAY, end, universe(12, DAY))
    ]

    assert drafts
    assert {draft.deadline for draft in drafts} == {end}
    assert deadline_of(DAY, 3, end) == end


def test_the_same_seed_and_day_draw_the_same_report():
    candidates = universe(12, DAY)

    first = draw_report("room-7", DAY, END, candidates)

    assert draw_report("room-7", DAY, END, candidates) == first
    assert draw_report("room-8", DAY, END, candidates) != first
    assert draw_report("room-7", date(2004, 5, 7), END, candidates) != first


def test_a_stock_without_a_future_is_skipped():
    empty = Candidate("VAZIA", Decimal(100), [])

    drafts = draw_report("seed", DAY, END, [empty, *universe(8, DAY)])

    assert "VAZIA" not in {draft.ticker for draft in drafts}


def window_of(
    draft: Draft, candidate: Candidate
) -> list[tuple[date, Decimal, Decimal]]:
    return [row for row in candidate.future if DAY < row[0] <= draft.deadline]


def test_the_house_is_right_about_sixty_percent_of_the_time():
    """A casa lê o futuro guardado com ruído: acerta o lado do movimento em ~62% das recomendações, entre 55% e 70%."""
    hits = total = 0
    for n in range(400):
        candidates = universe(10, DAY)
        by_ticker = {c.ticker: c for c in candidates}
        for draft in draw_report(f"room-{n}", DAY, END, candidates):
            window = window_of(draft, by_ticker[draft.ticker])
            total += 1
            hits += any(
                reached(draft.side, draft.target, high, low) for _, high, low in window
            )

    assert total > 1000
    assert 0.55 <= hits / total <= 0.70


def test_the_target_sits_on_the_recommended_side_of_todays_price():
    for draft in draw_report("seed", DAY, END, universe(12, DAY)):
        if draft.side is OrderAction.BUY:
            assert draft.target > draft.price
        else:
            assert draft.target < draft.price


# --- O placar


def test_a_buy_hits_when_the_high_touches_the_target():
    verdict = judge(
        OrderAction.BUY,
        Decimal(110),
        date(2004, 5, 31),
        date(2004, 5, 11),
        Decimal("110.40"),
        Decimal(104),
        Decimal(105),
    )

    assert verdict is not None
    assert (verdict.result, verdict.price) == (HouseResult.HIT, Decimal("110.40"))


def test_a_sell_hits_when_the_low_touches_the_target():
    verdict = judge(
        OrderAction.SELL,
        Decimal(90),
        date(2004, 5, 31),
        date(2004, 5, 11),
        Decimal(96),
        Decimal("89.50"),
        Decimal(95),
    )

    assert verdict is not None
    assert (verdict.result, verdict.price) == (HouseResult.HIT, Decimal("89.50"))


def test_the_high_does_not_hit_a_sell_and_the_low_does_not_hit_a_buy():
    assert (
        judge(
            OrderAction.SELL,
            Decimal(90),
            date(2004, 5, 31),
            date(2004, 5, 11),
            Decimal(120),
            Decimal(95),
            Decimal(100),
        )
        is None
    )
    assert (
        judge(
            OrderAction.BUY,
            Decimal(110),
            date(2004, 5, 31),
            date(2004, 5, 11),
            Decimal(105),
            Decimal(80),
            Decimal(100),
        )
        is None
    )


def test_the_deadline_closing_without_the_target_is_a_miss_at_the_close():
    verdict = judge(
        OrderAction.BUY,
        Decimal(110),
        date(2004, 5, 31),
        date(2004, 6, 1),
        Decimal(104),
        Decimal(99),
        Decimal(101),
    )

    assert verdict is not None
    assert (verdict.result, verdict.price) == (HouseResult.MISS, Decimal(101))


def test_before_the_deadline_without_the_target_the_recommendation_stays_open():
    assert (
        judge(
            OrderAction.BUY,
            Decimal(110),
            date(2004, 5, 31),
            date(2004, 5, 28),
            Decimal(104),
            Decimal(99),
            Decimal(101),
        )
        is None
    )


def test_the_hit_rate_is_nothing_without_a_resolved_recommendation():
    assert hit_rate(0, 0) is None
    assert hit_rate(14, 22) == Decimal(14) / Decimal(22)


# --- A tabela da partida


@pytest.fixture
def simulation_id(database: Engine) -> int:
    return repository.simulation.create_simulation(simulation_settings())


def drafts(*tickers: str) -> list[Draft]:
    return [
        Draft(
            ticker,
            OrderAction.BUY if n % 2 == 0 else OrderAction.SELL,
            Decimal(100),
            Decimal(110) if n % 2 == 0 else Decimal(90),
            date(2004, 5, 31),
        )
        for n, ticker in enumerate(tickers)
    ]


def test_the_report_is_stored_as_it_came_out_and_read_back(simulation_id: int):
    month = date(2004, 4, 1)

    saved = repository.house_report.insert_report(
        simulation_id, month, date(2004, 4, 7), drafts("AAAA3", "BBBB3", "CCCC3")
    )

    read = repository.house_report.of_month(simulation_id, month)
    assert [item.id for item in read] == [item.id for item in saved]
    assert [(i.ticker, i.side, i.target) for i in read] == [
        ("AAAA3", OrderAction.BUY, Decimal(110)),
        ("BBBB3", OrderAction.SELL, Decimal(90)),
        ("CCCC3", OrderAction.BUY, Decimal(110)),
    ]
    assert all(i.result is None and i.resolved_on is None for i in read)
    assert repository.house_report.months(simulation_id) == [month]


def test_the_months_come_newest_first_and_each_month_keeps_its_own_items(
    simulation_id: int,
):
    repository.house_report.insert_report(
        simulation_id, date(2004, 4, 1), date(2004, 4, 7), drafts("AAAA3")
    )
    repository.house_report.insert_report(
        simulation_id, date(2004, 5, 1), date(2004, 5, 7), drafts("BBBB3", "CCCC3")
    )

    assert repository.house_report.months(simulation_id) == [
        date(2004, 5, 1),
        date(2004, 4, 1),
    ]
    assert [
        i.ticker
        for i in repository.house_report.of_month(simulation_id, date(2004, 4, 1))
    ] == ["AAAA3"]


def test_the_scoreboard_counts_only_the_resolved_ones(simulation_id: int):
    items = repository.house_report.insert_report(
        simulation_id,
        date(2004, 4, 1),
        date(2004, 4, 7),
        drafts("AAAA3", "BBBB3", "CCCC3"),
    )
    repository.house_report.resolve(
        {
            items[0].id: Verdict(HouseResult.HIT, Decimal("110.40")),
            items[1].id: Verdict(HouseResult.MISS, Decimal(97)),
        },
        date(2004, 5, 31),
    )

    assert repository.house_report.scoreboard(simulation_id) == (1, 2)
    open_ones = repository.house_report.open_before(simulation_id, date.max)
    assert [i.ticker for i in open_ones] == ["CCCC3"]


def test_resuming_removes_the_later_report_and_reopens_the_later_results(
    simulation_id: int,
):
    april = repository.house_report.insert_report(
        simulation_id, date(2004, 4, 1), date(2004, 4, 7), drafts("AAAA3", "BBBB3")
    )
    repository.house_report.insert_report(
        simulation_id, date(2004, 5, 1), date(2004, 5, 7), drafts("CCCC3")
    )
    repository.house_report.resolve(
        {
            april[0].id: Verdict(HouseResult.HIT, Decimal("110.40")),
            april[1].id: Verdict(HouseResult.MISS, Decimal(97)),
        },
        date(2004, 5, 31),
    )
    repository.house_report.resolve(
        {april[0].id: Verdict(HouseResult.HIT, Decimal("110.40"))}, date(2004, 4, 20)
    )

    repository.house_report.rewind(simulation_id, date(2004, 5, 10))

    assert repository.house_report.months(simulation_id) == [
        date(2004, 5, 1),
        date(2004, 4, 1),
    ]
    repository.house_report.rewind(simulation_id, date(2004, 4, 30))

    assert repository.house_report.months(simulation_id) == [date(2004, 4, 1)]
    read = {
        i.ticker: i
        for i in repository.house_report.of_month(simulation_id, date(2004, 4, 1))
    }
    assert read["AAAA3"].result is HouseResult.HIT
    assert read["BBBB3"].result is None


def test_deleting_the_match_deletes_its_report(simulation_id: int):
    repository.house_report.insert_report(
        simulation_id, date(2004, 4, 1), date(2004, 4, 7), drafts("AAAA3")
    )

    repository.simulation.delete(simulation_id)

    assert repository.house_report.months(simulation_id) == []


def recommendation(
    side: OrderAction, target: str, deadline: date, ticker: str = "AAAA3"
) -> HouseRecommendationDTO:
    return HouseRecommendationDTO(
        id=1,
        report_month=date(2004, 4, 1),
        issued_on=date(2004, 4, 7),
        ticker=ticker,
        side=side,
        price=Decimal(100),
        target=Decimal(target),
        deadline=deadline,
        result=None,
        result_price=None,
        resolved_on=None,
    )


# --- O dia no pregão


def test_only_stocks_traded_today_enter_the_draw():
    class Candle:
        def __init__(self, ticker: str, asset_class: AssetClass, price_date: date):
            self.ticker = ticker
            self.asset_class = asset_class
            self.price_date = price_date

    candles = [
        Candle("ACAO3", AssetClass.STOCK, DAY),
        Candle("FIIX11", AssetClass.FII, DAY),
        Candle("PARADA3", AssetClass.STOCK, DAY - timedelta(days=3)),
    ]

    assert [c.ticker for c in tradable_today(candles, DAY)] == ["ACAO3"]  # type: ignore[arg-type]


def test_the_verdicts_read_the_high_the_low_and_the_close_of_the_day():
    class Candle:
        ticker = "AAAA3"
        price_date = date(2004, 5, 31)
        high = 109.0
        low = 99.0
        close = 101.0

    open_ones = [recommendation(OrderAction.BUY, "110", date(2004, 5, 31))]

    verdicts = verdicts_of(open_ones, [Candle()], date(2004, 5, 31), date(2004, 6, 1))  # type: ignore[list-item]

    assert verdicts[1].result is HouseResult.MISS
    assert verdicts[1].price == Decimal("101.0")


# --- A partida: o relatório, o bloco, o selo e o bot


def broker_match(monkeypatch: pytest.MonkeyPatch, *others: str):
    """A partida com a Ana no Corretor e os `others` em CLT; devolve a partida e as pessoas na ordem."""
    people = [person(name) for name in ("Ana", *others)]
    sim = match(monkeypatch)
    sim.switch_profession(people[0], Profession.BROKER)
    return sim, people


def until(sim, day: date) -> None:
    while sim.get_current_date() < day:
        sim.next_tick()


def block_of(sim, user) -> BrokerMechanicDTO:
    mechanic = sim.get_profession_page(user.client_id).mechanic
    assert isinstance(mechanic, BrokerMechanicDTO)
    return mechanic


@pytest.mark.usefixtures("room")
def test_before_the_first_report_the_block_is_available_and_names_the_day(monkeypatch):
    sim, (ana,) = broker_match(monkeypatch)

    block = block_of(sim, ana)

    assert block.status is MechanicStatus.AVAILABLE
    assert block.current is None and block.previous is None
    assert block.next_report_on == date(2004, 4, 7)
    assert (block.hits, block.resolved, block.hit_rate) == (0, 0, None)
    assert block.volume == 0 and block.commission == 0
    assert block.income == block.fixed_income == Decimal("5600")
    assert sim.get_house_picks(ana.client_id) == []


@pytest.mark.usefixtures("room")
def test_the_report_comes_out_on_the_fifth_business_day_and_is_stored(monkeypatch):
    sim, (ana,) = broker_match(monkeypatch)

    until(sim, date(2004, 4, 6))
    assert block_of(sim, ana).current is None
    until(sim, date(2004, 4, 7))

    block = block_of(sim, ana)
    assert block.status is MechanicStatus.ACTIVE
    assert block.current is not None
    assert block.current.month == date(2004, 4, 1)
    assert block.current.issued_on == date(2004, 4, 7)
    assert 3 <= len(block.current.items) <= 5
    assert all(
        date(2004, 4, 30) <= i.deadline <= date(2004, 7, 31)
        for i in block.current.items
    )
    assert block.next_report_on == date(2004, 5, 7)
    stored = repository.house_report.of_month(sim.settings.id, date(2004, 4, 1))
    assert [i.id for i in stored] == [i.id for i in block.current.items]


@pytest.mark.usefixtures("room")
def test_the_report_is_not_issued_twice_in_the_month(monkeypatch):
    sim, _ = broker_match(monkeypatch)

    until(sim, date(2004, 4, 14))

    assert repository.house_report.months(sim.settings.id) == [date(2004, 4, 1)]


@pytest.mark.usefixtures("room")
def test_the_picks_route_hands_the_stock_and_the_side_only_to_the_broker(monkeypatch):
    sim, (ana, bia) = broker_match(monkeypatch, "Bia")

    until(sim, date(2004, 4, 7))

    block = block_of(sim, ana)
    picks = sim.get_house_picks(ana.client_id)
    assert [(p.ticker, p.side) for p in picks] == [
        (i.ticker, i.side)
        for i in block.current.items  # type: ignore[union-attr]
    ]
    assert sim.get_house_picks(bia.client_id) == []


@pytest.mark.usefixtures("room")
def test_the_block_of_another_profession_is_not_the_brokers(monkeypatch):
    sim, (_, bia) = broker_match(monkeypatch, "Bia")

    mechanic = sim.get_profession_page(bia.client_id).mechanic

    assert not isinstance(mechanic, BrokerMechanicDTO)


@pytest.mark.usefixtures("room")
def test_the_open_recommendation_resolves_on_the_day_the_deadline_closes(monkeypatch):
    sim, (ana,) = broker_match(monkeypatch)
    until(sim, date(2004, 4, 7))
    items = repository.house_report.of_month(sim.settings.id, date(2004, 4, 1))
    # Alvos fora de alcance: só o fim do prazo decide
    repository.house_report.rewind(sim.settings.id, date(2004, 4, 6))
    reissued = repository.house_report.insert_report(
        sim.settings.id,
        date(2004, 4, 1),
        date(2004, 4, 7),
        [
            Draft(i.ticker, OrderAction.BUY, i.price, Decimal(10**6), date(2004, 4, 30))
            for i in items
        ],
    )
    sim._house_open = None
    sim._house_months = None

    until(sim, date(2004, 4, 29))
    assert repository.house_report.scoreboard(sim.settings.id) == (0, 0)
    until(sim, date(2004, 4, 30))

    hits, resolved = repository.house_report.scoreboard(sim.settings.id)
    assert (hits, resolved) == (0, len(reissued))
    assert block_of(sim, ana).hit_rate == 0


@pytest.mark.usefixtures("room")
def test_the_month_turn_pays_the_commission_of_the_month_that_closed(monkeypatch):
    sim, (ana, bia) = broker_match(monkeypatch, "Bia")
    sim.switch_profession(bia, Profession.BROKER)
    until(sim, date(2004, 4, 20))
    ana_portfolio = repository.portfolio.ids(sim.settings.id)[ana.id]
    repository.event.insert_many(
        [
            equity(
                sim.settings.id,
                ana_portfolio,
                "BANK_A",
                EquityEventType.BUY,
                day=date(2004, 4, 15),
                quantity="1000",
                price="200",
            )
        ]
    )

    until(sim, date(2004, 5, 3))

    block = block_of(sim, ana)
    # 0,05% de R$ 200.000 = R$ 100, dividido entre os 2 Corretores
    assert block.brokers == 2
    assert block.volume >= Decimal(200_000)
    assert block.commission > 0
    assert block.income == block.fixed_income + block.commission


@pytest.mark.usefixtures("room")
def test_the_header_shows_salary_plus_commission(monkeypatch):
    sim, (ana,) = broker_match(monkeypatch)
    sim._profession_book.save_state(
        ana.id, BrokerState(volume=Decimal(2_000_000), brokers=4)
    )

    header = sim.get_profession_page(ana.client_id).header

    assert header.mechanic_income == Decimal(250)


# --- O bot


def test_the_bot_buys_each_buy_recommendation_with_an_equal_share_of_twenty_percent():
    assert bot_budget_each(Decimal(100_000), Decimal(50_000), 4) == Decimal(5000)
    assert bot_budget_each(Decimal(100_000), Decimal(50_000), 0) == 0


def test_the_bot_budget_is_capped_by_the_free_cash():
    assert bot_budget_each(Decimal(100_000), Decimal(8000), 4) == Decimal(2000)


def test_the_bot_without_cash_does_not_buy():
    assert bot_budget_each(Decimal(100_000), Decimal(0), 4) == 0


def test_the_bot_ignores_the_sell_recommendations():
    items = [
        recommendation(OrderAction.BUY, "110", date(2004, 5, 31), "AAAA3"),
        recommendation(OrderAction.SELL, "90", date(2004, 5, 31), "BBBB3"),
    ]

    assert [i.ticker for i in bot_buys(items)] == ["AAAA3"]


@pytest.mark.usefixtures("room")
def test_the_bot_buys_on_the_report_day_and_sells_at_the_deadline(monkeypatch):
    person("Ana")
    bot = UserManager.add_bot(
        "Robo", resolve_bot("moving_average_cross", {}, profession=Profession.BROKER)
    )
    sim = match(monkeypatch)
    deadline = date(2004, 4, 30)
    # O relatório do dia: uma compra e uma venda, com o alvo fora de alcance
    monkeypatch.setattr(
        "backend.features.simulation.simulation.draw_report",
        lambda *args, **kwargs: [
            Draft("POWER", OrderAction.BUY, Decimal(29), Decimal(10**6), deadline),
            Draft("BANK_A", OrderAction.SELL, Decimal(12), Decimal(1), deadline),
        ],
    )

    until(sim, date(2004, 4, 7))

    state = sim.get_profession_state(bot.client_id).state
    assert isinstance(state, BrokerState)
    items = {
        i.ticker: i
        for i in repository.house_report.of_month(sim.settings.id, date(2004, 4, 1))
    }
    # Só a compra entra; cada uma recebe 20% do patrimônio dividido pelas compras
    assert list(state.bought) == [str(items["POWER"].id)]
    bought = state.bought[str(items["POWER"].id)]
    free = sim._engine.broker.get_available_position(bot.client_id, "POWER")
    assert free >= bought > 0
    assert sim._engine.broker.get_available_position(bot.client_id, "BANK_A") == 0

    until(sim, deadline)

    after = sim.get_profession_state(bot.client_id).state
    assert isinstance(after, BrokerState)
    assert after.bought == {}
    assert sim._engine.broker.get_available_position(bot.client_id, "POWER") < free
