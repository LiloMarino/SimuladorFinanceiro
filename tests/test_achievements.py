from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.simulation import SimulationDTO
from backend.core.dto.snapshot import SnapshotDTO
from backend.core.enum import (
    AchievementCategory,
    AchievementIcon,
    GameType,
    IndicatorSeries,
    PlayerGrouping,
)
from backend.core.runtime.event_manager import EventManager
from backend.core.utils import next_business_day
from backend.features.achievements import metrics, service
from backend.features.achievements.catalog import BY_CODE, CATALOG
from backend.features.achievements.evaluator import AchievementEvaluator
from backend.features.achievements.metrics import (
    METRICS,
    Context,
    MatchResult,
    Sources,
    Trigger,
)
from backend.features.variable_income.income_tax import MonthlyTax
from tests.conftest import SetIndicator
from tests.fakes import simulation_settings

SETTINGS = SimulationDTO(id=1, **simulation_settings().model_dump())
START = date(2020, 1, 2)


def snapshot(
    networth: str = "10000",
    *,
    cash: str | None = None,
    equity: str = "0",
    contribution: str = "0",
    day: date = START,
) -> SnapshotDTO:
    return SnapshotDTO(
        user_id=1,
        snapshot_date=day,
        total_equity=Decimal(equity),
        total_fixed=Decimal(0),
        total_debt=Decimal(0),
        total_cash=Decimal(cash if cash is not None else networth),
        total_contribution=Decimal(contribution),
        total_networth=Decimal(networth),
        created_at=datetime(2020, 1, 2, tzinfo=UTC),
    )


def context(
    snap: SnapshotDTO,
    match: MatchResult = metrics.NO_MATCH,
    settings: SimulationDTO = SETTINGS,
    sources: Sources = metrics.NO_SOURCES,
) -> Context:
    return Context(1, settings, snap, match, sources)


def settings_with(**rules: object) -> SimulationDTO:
    return SimulationDTO(id=1, **{**simulation_settings().model_dump(), **rules})


# --------------------------------------------------
# O catálogo
# --------------------------------------------------


def test_codes_are_unique():
    assert len(BY_CODE) == len(CATALOG)


@pytest.mark.parametrize("achievement", CATALOG, ids=lambda a: a.code)
def test_every_achievement_points_to_a_registered_metric(achievement):
    assert achievement.metric in METRICS
    assert achievement.goal > 0
    assert isinstance(achievement.icon, AchievementIcon)
    assert isinstance(achievement.category, AchievementCategory)


@pytest.mark.parametrize("achievement", CATALOG, ids=lambda a: a.code)
def test_secret_achievements_belong_to_the_secret_category(achievement):
    assert achievement.secret == (achievement.category is AchievementCategory.SECRET)


class FakeAchievements:
    """O repositório em memória: só o que o avaliador e a listagem usam."""

    def __init__(self):
        self.unlocked: dict[str, int] = {}
        self.progress: dict[str, Decimal] = {}
        self.order_count = 0

    def unlocked_codes(self, user_id):
        return set(self.unlocked)

    def unlock(self, user_id, codes, simulation_id, game_date):
        new = [c for c in codes if c not in self.unlocked]
        self.unlocked.update({c: simulation_id for c in new})
        return new

    def save_progress(self, user_id, values):
        for code, value in values.items():
            self.progress[code] = max(self.progress.get(code, Decimal(0)), value)

    def best_progress(self, user_id):
        return self.progress

    def unlocks(self, user_id):
        return []

    def equity_orders(self, simulation_id, user_id, event_type):
        return self.order_count

    def fixed_income_buys(self, simulation_id, user_id):
        return 0

    def held_assets(self, simulation_id, user_id):
        return 0

    def equity_order_dates(self, simulation_id, user_id, event_type):
        return []

    def held_sectors(self, simulation_id, user_id):
        return 0

    def day_traded_assets(self, simulation_id, user_id):
        return 0

    def equity_flows(self, simulation_id, user_id, since):
        return []

    def real_market_end(self, simulation_id):
        return None


@pytest.fixture
def fake(monkeypatch: pytest.MonkeyPatch) -> FakeAchievements:
    fake = FakeAchievements()
    monkeypatch.setattr(repository, "achievements", fake)
    monkeypatch.setattr(repository.portfolio, "get_patrimonial_history", lambda _: [])
    monkeypatch.setattr(repository.candle_challenge, "total_hits", lambda _: 0)
    monkeypatch.setattr(EventManager, "pop_touched_users", lambda: set())
    return fake


def test_secret_locked_achievement_hides_name_and_description(fake: FakeAchievements):
    listed = {a.code: a for a in service.list_achievements(1)}

    secret = listed["monk_patience"]
    assert secret.name is None and secret.description is None
    assert secret.progress is None
    assert secret.icon is BY_CODE["monk_patience"].icon
    assert listed["first_buy"].name == "Primeira compra"


def test_locked_goal_achievement_shows_best_progress_capped_at_the_goal(
    fake: FakeAchievements,
):
    fake.progress["networth_1m"] = Decimal(642_000)
    fake.progress["hands_on"] = Decimal(500)

    listed = {a.code: a for a in service.list_achievements(1)}

    assert listed["networth_1m"].progress is not None
    assert listed["networth_1m"].progress.current == Decimal(642_000)
    assert listed["hands_on"].progress is not None
    assert listed["hands_on"].progress.current == Decimal(100)
    # Sem meta numérica não há barra
    assert listed["first_buy"].progress is None


# --------------------------------------------------
# O avaliador
# --------------------------------------------------


def test_tick_unlocks_by_snapshot_metrics_and_only_once(fake: FakeAchievements):
    evaluator = AchievementEvaluator(SETTINGS)
    rich = {1: snapshot("150000", contribution="0")}

    first = evaluator.on_tick(rich, month_changed=False)
    again = evaluator.on_tick(rich, month_changed=False)

    assert {a.code for a in first[1]} == {"networth_100k", "doubled_capital"}
    assert again == {}


def test_order_metrics_wait_for_the_player_to_have_new_events(
    monkeypatch: pytest.MonkeyPatch, fake: FakeAchievements
):
    fake.order_count = 1
    evaluator = AchievementEvaluator(SETTINGS)

    quiet = evaluator.on_tick({1: snapshot()}, month_changed=False)
    monkeypatch.setattr(EventManager, "pop_touched_users", lambda: {1})
    busy = evaluator.on_tick({1: snapshot()}, month_changed=False)

    assert quiet == {}
    assert {a.code for a in busy[1]} == {"first_buy", "first_sale"}


def test_progress_is_saved_on_month_change_and_keeps_the_best(fake: FakeAchievements):
    evaluator = AchievementEvaluator(SETTINGS)

    evaluator.on_tick({1: snapshot("60000", cash="60000")}, month_changed=True)
    evaluator.on_tick({1: snapshot("20000", cash="20000")}, month_changed=True)

    assert fake.progress["networth_1m"] == Decimal(60000)


def test_match_end_unlocks_the_ones_that_need_the_result(fake: FakeAchievements):
    evaluator = AchievementEvaluator(SETTINGS)
    result = MatchResult(frozenset({1}), players_count=8, ended_by_goal=False)

    unlocked = evaluator.on_match_end({1: snapshot()}, result)

    assert {"first_win", "full_room", "finished_match"} <= {a.code for a in unlocked[1]}


def test_loser_does_not_win_anything_at_match_end(fake: FakeAchievements):
    evaluator = AchievementEvaluator(SETTINGS)
    result = MatchResult(frozenset({2}), players_count=8, ended_by_goal=False)

    unlocked = evaluator.on_match_end({1: snapshot()}, result)

    codes = {a.code for a in unlocked.get(1, [])}
    assert "first_win" not in codes and "full_room" not in codes
    assert "finished_match" in codes


# --------------------------------------------------
# As métricas
# --------------------------------------------------


def test_capital_multiple_counts_contributions_as_capital():
    snap = snapshot("30000", contribution="10000")

    assert context(snap).value("capital_multiple") == Decimal("1.5")


def test_fully_invested_needs_almost_no_cash():
    assert context(snapshot("1000", cash="5", equity="995")).value(
        "fully_invested"
    ) == Decimal(1)
    assert context(snapshot("1000", cash="500", equity="500")).value(
        "fully_invested"
    ) == Decimal(0)
    assert context(snapshot("1000")).value("fully_invested") == Decimal(0)


def test_days_without_selling_counts_from_the_last_sale(
    monkeypatch: pytest.MonkeyPatch,
):
    dates = {"BUY": [date(2020, 1, 2)], "SELL": [date(2020, 2, 1)]}
    monkeypatch.setattr(
        repository.achievements,
        "equity_order_dates",
        lambda _sim, _user, kind: dates[kind],
    )
    snap = snapshot(day=date(2020, 3, 2))

    assert context(snap).value("days_without_selling") == Decimal(30)


def test_days_without_selling_is_zero_without_a_purchase(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(
        repository.achievements, "equity_order_dates", lambda *_args: []
    )

    assert context(snapshot()).value("days_without_selling") == Decimal(0)


def test_bought_on_first_day(monkeypatch: pytest.MonkeyPatch):
    first_day = next_business_day(SETTINGS.start_date - timedelta(days=1))
    for buys, expected in [([first_day], 1), ([first_day + timedelta(days=7)], 0)]:
        monkeypatch.setattr(
            repository.achievements, "equity_order_dates", lambda *_a, b=buys: b
        )
        assert context(snapshot()).value("bought_on_first_day") == Decimal(expected)


def test_ibov_downturns_find_the_drop_from_each_peak(indicators: SetIndicator):
    days = [date(2020, 1, d) for d in (2, 3, 6, 7, 8, 9)]
    levels = ["100", "90", "70", "80", "100", "120"]
    indicators(
        IndicatorSeries.IBOV, {d: Decimal(v) for d, v in zip(days, levels, strict=True)}
    )

    [drop] = metrics.ibov_downturns(days, Decimal("0.20"))

    assert (drop.peak, drop.reached, drop.trough) == (days[0], days[2], days[2])
    assert drop.depth == Decimal("0.3")
    assert metrics.ibov_downturns(days, Decimal("0.50")) == []


def test_ibov_downturns_without_index_data_are_empty(indicators: SetIndicator):
    assert metrics.ibov_downturns([START], Decimal("0.20")) == []


def test_months_above_cdi_counts_the_streak_up_to_the_last_closed_month(
    monkeypatch: pytest.MonkeyPatch,
):
    months = [
        risk_month(date(2020, 1, 1), "0.02", "0.01"),
        risk_month(date(2020, 2, 1), "0.00", "0.01"),
        risk_month(date(2020, 3, 1), "0.02", "0.01"),
        risk_month(date(2020, 4, 1), "0.02", "0.01"),
        # O mês em curso não conta
        risk_month(date(2020, 5, 1), "0.02", "0.01"),
    ]
    monkeypatch.setattr(metrics.risk, "monthly_returns", lambda _days: months)
    ctx = context(snapshot(day=date(2020, 5, 4)))
    ctx.__dict__["days"] = []

    assert ctx.value("months_above_cdi") == Decimal(2)


def risk_month(month: date, value: str, cdi: str):
    return metrics.risk.MonthlyReturn(month, Decimal(value), Decimal(cdi))


def test_history_metrics_read_the_history_once(monkeypatch: pytest.MonkeyPatch):
    reads = []

    def history(_user_id: int) -> list[PatrimonialHistoryDTO]:
        reads.append(1)
        return []

    monkeypatch.setattr(repository.portfolio, "get_patrimonial_history", history)
    monkeypatch.setattr(repository.achievements, "equity_order_dates", lambda *_a: [])
    ctx = context(snapshot())

    ctx.value("months_above_cdi")
    ctx.value("beat_ibov_year")

    assert len(reads) == 1


def test_metric_triggers_are_known():
    assert {m.when for m in METRICS.values()} <= set(Trigger)


# --------------------------------------------------
# As métricas da leva de conquistas sobre as features recentes
# --------------------------------------------------


def month_tax(year: int, month: int, *, exempt: str, tax: str = "0") -> MonthlyTax:
    return MonthlyTax(
        year=year,
        month=month,
        stock_sales=Decimal(0),
        crypto_sales=Decimal(0),
        exempt_profit=Decimal(exempt),
        stock_exempt_profit=Decimal(exempt),
        pools={},
        tax=Decimal(tax),
        darf_amount=None,
        due_date=None,
    )


def test_exempt_month_needs_a_closed_month_with_exempt_stock_profit_and_no_tax():
    today = snapshot(day=date(2020, 3, 2))
    cases = [
        ([month_tax(2020, 2, exempt="500")], 1),
        # O mês em curso ainda pode virar imposto
        ([month_tax(2020, 3, exempt="500")], 0),
        ([month_tax(2020, 2, exempt="0")], 0),
        ([month_tax(2020, 2, exempt="500", tax="30")], 0),
        ([], 0),
    ]
    for months, expected in cases:
        sources = Sources(income_tax=lambda _user_id, m=months: m)

        ctx = context(today, sources=sources)

        assert ctx.value("exempt_month") == Decimal(expected)


def test_beyond_horizon_starts_the_day_after_the_last_real_one():
    sources = Sources(market_real_end=lambda: date(2020, 1, 10))

    for day, expected in [(date(2020, 1, 10), 0), (date(2020, 1, 13), 1)]:
        ctx = context(snapshot(day=day), sources=sources)
        assert ctx.value("beyond_horizon") == Decimal(expected)
    # Sem mercado real não há horizonte
    assert context(snapshot()).value("beyond_horizon") == Decimal(0)


def test_overall_score_is_the_total_and_zero_before_there_is_one(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(repository.portfolio, "get_patrimonial_history", lambda _: [])
    assert context(snapshot()).value("overall_score") == Decimal(0)

    monkeypatch.setattr(
        metrics.score, "player_score", lambda _h: type("S", (), {"total": Decimal(212)})
    )
    assert context(snapshot()).value("overall_score") == Decimal(212)


def test_moved_market_needs_the_price_impact_and_an_order_big_enough(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(
        repository.stock, "get_average_volume", lambda *_a, **_k: 1000.0
    )
    on = settings_with(price_impact_enabled=True)

    # k = 0,02: 100 sobre 1.000 de volume médio desloca 0,63%; 10 desloca 0,2%
    for quantity, expected in [("100", 1), ("-100", 1), ("10", 0)]:
        monkeypatch.setattr(
            repository.achievements,
            "equity_flows",
            lambda *_a, q=quantity: [("AAA", START, Decimal(q))],
        )
        ctx = context(snapshot(), settings=on)
        assert ctx.value("moved_market") == Decimal(expected)

    monkeypatch.setattr(
        repository.achievements,
        "equity_flows",
        lambda *_a: [("AAA", START, Decimal(100))],
    )
    assert context(snapshot()).value("moved_market") == Decimal(0)


def test_expert_mode_is_every_assistance_hidden():
    hidden = {
        "show_equivalent_rate": False,
        "show_maturity_projection": False,
        "show_chart_hints": False,
    }

    assert settings_with(**hidden).expert_mode
    assert not settings_with(**{**hidden, "show_chart_hints": True}).expert_mode
    assert not SETTINGS.expert_mode


def test_match_end_metrics_for_expert_mode_and_teams():
    won = MatchResult(frozenset({1}), players_count=3, ended_by_goal=False)
    alone = MatchResult(frozenset({1}), players_count=1, ended_by_goal=False)
    lost = MatchResult(frozenset({2}), players_count=3, ended_by_goal=False)
    expert = settings_with(
        show_equivalent_rate=False,
        show_maturity_projection=False,
        show_chart_hints=False,
    )
    teams = settings_with(player_grouping=PlayerGrouping.TEAMS)

    def value(name: str, settings: SimulationDTO, match: MatchResult) -> Decimal:
        return context(snapshot(), match, settings).value(name)

    assert value("won_expert_mode", expert, won) == Decimal(1)
    assert value("won_expert_mode", SETTINGS, won) == Decimal(0)
    assert value("won_expert_mode", expert, lost) == Decimal(0)
    assert value("won_expert_mode", expert, alone) == Decimal(0)
    assert value("won_as_team", teams, won) == Decimal(1)
    assert value("won_as_team", SETTINGS, won) == Decimal(0)
    assert value("won_as_team", teams, lost) == Decimal(0)


def test_goal_race_win_requires_the_goal_to_end_the_match():
    by_goal = MatchResult(frozenset({1}), players_count=3, ended_by_goal=True)
    by_date = MatchResult(frozenset({1}), players_count=3, ended_by_goal=False)
    lost = MatchResult(frozenset({2}), players_count=3, ended_by_goal=True)
    race = settings_with(game_type=GameType.GOAL_RACE)
    classic = settings_with(game_type=GameType.CLASSIC)

    def value(name: str, settings: SimulationDTO, match: MatchResult) -> Decimal:
        return context(snapshot(), match, settings).value(name)

    assert value("won_goal_race", race, by_goal) == Decimal(1)
    assert value("won_goal_race", race, by_date) == Decimal(0)
    assert value("won_goal_race", race, lost) == Decimal(0)
    assert value("won_goal_race", classic, by_goal) == Decimal(0)
    assert value("finished_to_end", race, by_date) == Decimal(1)
    assert value("finished_to_end", race, by_goal) == Decimal(0)
