from __future__ import annotations

from datetime import date
from decimal import Decimal
from functools import partial
from types import SimpleNamespace
from typing import cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend import config
from backend.core.dto.events.cashflow import CashflowEventDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import (
    CASH_SIGN,
    CONTRIBUTION_TYPES,
    CashflowEventType,
    GameType,
    IndicatorSeries,
    LifeHistoryCategory,
    LifeHistoryKind,
    LifeHistorySort,
)
from backend.core.indicators import annual_index_rate
from backend.core.life_budget import LifeBudget
from backend.core.periods import MONTHS_PER_YEAR
from backend.core.rates import period_rate
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.economy.growth import NEUTRAL_UNEMPLOYMENT
from backend.features.simulation.life_events import (
    layoff_in,
    overdraft_interest,
    salary_skipped,
    unexpected_on,
)
from backend.features.simulation.life_history import (
    BudgetChange,
    budget_changes,
    build_history,
    history_page,
)
from backend.features.simulation.simulation import Simulation, _overdraft_rate
from backend.features.tax_policy import DEFAULT_TAX_POLICY
from backend.routes.simulation import CreateSimulationRequest, simulation_router
from tests.conftest import SetIndicator
from tests.fakes import client, daily_series, monthly_series, simulation_settings

T = CashflowEventType


def event(
    day: date, type_: CashflowEventType, amount: str, key: str | None = None
) -> CashflowEventDTO:
    return CashflowEventDTO(
        simulation_id=1,
        user_id=1,
        event_date=day,
        event_type=type_,
        amount=Decimal(amount),
        life_event_key=key,
    )


EVENTS = [
    event(date(2012, 6, 1), T.DEPOSIT, "2660"),
    event(date(2012, 6, 8), T.UNEXPECTED_EXPENSE, "5000", "REPAIR"),
    event(date(2012, 6, 11), T.OVERDRAFT_INTEREST, "8.60"),
    event(date(2012, 6, 12), T.OVERDRAFT_INTEREST, "8.63"),
    event(date(2012, 7, 2), T.OVERDRAFT_INTEREST, "8.66"),
    event(date(2012, 7, 2), T.SALARY, "8000"),
    event(date(2012, 7, 9), T.UNEXPECTED_EXPENSE, "0", "LAYOFF"),
]


def test_every_cashflow_type_has_a_sign():
    """Um tipo novo sem sinal valeria zero no saldo, sem erro: o mapa cobre todos."""
    assert set(CASH_SIGN) == set(CashflowEventType)
    assert T.OVERDRAFT_INTEREST not in CONTRIBUTION_TYPES


def test_history_rows_follow_the_rebuilt_cash():
    rows = build_history(EVENTS)

    assert [r.kind for r in rows] == [
        LifeHistoryKind.UNEXPECTED_EXPENSE,
        LifeHistoryKind.OVERDRAFT_STARTED,
        LifeHistoryKind.OVERDRAFT_INTEREST,
        LifeHistoryKind.OVERDRAFT_INTEREST,
        LifeHistoryKind.OVERDRAFT_ENDED,
        LifeHistoryKind.LAYOFF,
    ]
    repair, negative, june_interest, july_interest, positive, layoff = rows
    assert repair.label == "Conserto do carro"
    assert repair.amount == Decimal(-5000)
    assert repair.cash_after == negative.cash_after == Decimal(-2340)
    # O juro de junho é uma linha só, datada do último pregão cobrado
    assert june_interest.amount == Decimal("-17.23")
    assert june_interest.event_date == date(2012, 6, 12)
    assert july_interest.cash_after == Decimal("-2365.89")
    assert positive.event_date == date(2012, 7, 2)
    assert layoff.category is LifeHistoryCategory.LAYOFF
    assert layoff.amount is None


def test_page_is_newest_first_with_counts_per_category():
    page = history_page(build_history(EVENTS), LifeHistoryCategory.OVERDRAFT, 1, 2)

    assert page.total == 4
    assert [r.kind for r in page.items] == [
        LifeHistoryKind.OVERDRAFT_INTEREST,
        LifeHistoryKind.OVERDRAFT_INTEREST,
    ]
    assert (page.counts.all, page.counts.unexpected, page.counts.layoff) == (6, 1, 1)


def test_interest_paid_sums_the_whole_match_whatever_the_filter():
    rows = build_history(EVENTS)

    assert history_page(rows, None, 0, 6).interest_paid == Decimal("25.89")
    assert history_page(
        rows, LifeHistoryCategory.LAYOFF, 0, 6
    ).interest_paid == Decimal("25.89")
    assert history_page([], None, 0, 6).interest_paid == Decimal(0)


def test_amount_sort_is_numeric_global_and_keeps_missing_last():
    rows = build_history(EVENTS)
    ascending = history_page(rows, None, 0, 6, LifeHistorySort.AMOUNT, "asc")
    descending = history_page(rows, None, 0, 6, LifeHistorySort.AMOUNT, "desc")
    assert [r.amount for r in ascending.items] == [
        Decimal(-5000),
        Decimal("-17.23"),
        Decimal("-8.66"),
        None,
        None,
        None,
    ]
    assert [r.amount for r in descending.items] == [
        Decimal("-8.66"),
        Decimal("-17.23"),
        Decimal(-5000),
        None,
        None,
        None,
    ]
    # A segunda página é o recorte da ordem global, não a ordenação de uma página isolada.
    assert (
        history_page(rows, None, 2, 2, LifeHistorySort.AMOUNT, "asc").items
        == ascending.items[2:4]
    )
    assert rows == build_history(EVENTS)


def test_sorting_filter_and_counts_work_together():
    rows = build_history(EVENTS)
    page = history_page(
        rows, LifeHistoryCategory.OVERDRAFT, 0, 10, LifeHistorySort.CASH, "asc"
    )
    assert [r.cash_after for r in page.items] == sorted(
        r.cash_after for r in rows if r.category is LifeHistoryCategory.OVERDRAFT
    )
    assert page.total == 4
    assert page.counts.all == 6
    assert history_page([], None, 0, 6, LifeHistorySort.CASH, "asc").items == []


def test_text_sort_uses_the_labels_displayed_in_the_table():
    rows = build_history(EVENTS)
    by_type = history_page(rows, None, 0, 6, LifeHistorySort.TYPE, "asc")
    assert [r.category for r in by_type.items] == [
        LifeHistoryCategory.OVERDRAFT
    ] * 4 + [LifeHistoryCategory.LAYOFF, LifeHistoryCategory.UNEXPECTED]
    by_description = history_page(rows, None, 0, 6, LifeHistorySort.DESCRIPTION, "asc")
    assert [r.kind for r in by_description.items] == [
        LifeHistoryKind.OVERDRAFT_STARTED,
        LifeHistoryKind.OVERDRAFT_ENDED,
        LifeHistoryKind.UNEXPECTED_EXPENSE,
        LifeHistoryKind.OVERDRAFT_INTEREST,
        LifeHistoryKind.OVERDRAFT_INTEREST,
        LifeHistoryKind.LAYOFF,
    ]


def test_history_route_validates_and_applies_sorting(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(SimulationManager, "has_active_simulation", lambda: True)
    monkeypatch.setattr(
        SimulationManager,
        "get_active_simulation",
        lambda: SimpleNamespace(get_life_history=lambda _client: build_history(EVENTS)),
    )
    app = FastAPI()
    app.include_router(simulation_router)
    api = TestClient(app)
    api.cookies.set("client_id", str(client("Ana")))
    path = "/api/simulation/life-history"
    response = api.get(
        path, params={"sort_by": "amount", "sort_direction": "asc", "limit": 1}
    )
    assert response.status_code == 200
    assert Decimal(response.json()["items"][0]["amount"]) == Decimal(-5000)
    assert api.get(path, params={"sort_by": "invalid"}).status_code == 422
    assert api.get(path, params={"sort_direction": "invalid"}).status_code == 422


def test_layoff_is_known_only_after_the_day_it_happens():
    seed, per_year, start = 3, 6, date(2020, 1, 2)
    month = date(2020, 1, 1)
    while (day := layoff_in(seed, month, per_year, start)) is None:
        month = date(month.year + month.month // 12, month.month % 12 + 1, 1)

    assert layoff_in(seed, day, per_year, start, until=day) == day
    if day.day > 1:
        before = date(day.year, day.month, day.day - 1)
        assert layoff_in(seed, day, per_year, start, until=before) is None


def _life_request(**changes: object) -> CreateSimulationRequest:
    fields: dict[str, object] = {
        "name": "Renda",
        "start_date": date(2020, 1, 1),
        "end_date": date(2030, 12, 31),
        "starting_cash": Decimal(10000),
        "price_impact_k": 0.02,
        "price_impact_decay_days": 20,
        "game_type": GameType.FINANCIAL_INDEPENDENCE,
        "goal_net_worth": Decimal(100000),
        "monthly_salary": Decimal(8000),
        "monthly_expense": Decimal(5000),
        "unexpected_per_year": 3,
    }
    return CreateSimulationRequest.model_validate({**fields, **changes})


def test_life_rules_are_validated():
    assert _life_request().withdrawal_rate == Decimal("0.04")
    with pytest.raises(ValidationError, match="maiores que zero"):
        _life_request(monthly_expense=Decimal(0))
    with pytest.raises(ValidationError):
        _life_request(withdrawal_rate=Decimal("0.2"))
    # 12 x 30 / 4% = R$ 9.000, abaixo do saldo inicial
    with pytest.raises(ValidationError, match="maior que o saldo inicial"):
        _life_request(monthly_expense=Decimal(30))


class _RecordingEngine:
    def __init__(self, cash: Decimal = Decimal(0)) -> None:
        self.calls: list[tuple[str, Decimal]] = []
        self.cash = cash

    def tax_policy_on(self, _day: date):
        return DEFAULT_TAX_POLICY

    def pay_salary(self, _client, amount: Decimal) -> None:
        self.calls.append(("salary", amount))

    def pay_expense(self, _client, amount: Decimal) -> None:
        self.calls.append(("expense", amount))

    def charge_unexpected(self, _client, amount: Decimal, key: str) -> None:
        self.calls.append((key, amount))

    def charge_overdraft_interest(self, _client, amount: Decimal) -> None:
        self.calls.append(("interest", amount))


def _living(
    day: date,
    seed: int,
    engine: _RecordingEngine,
    unemployment: Decimal = NEUTRAL_UNEMPLOYMENT,
):
    settings = simulation_settings().model_copy(
        update={"game_type": GameType.FINANCIAL_INDEPENDENCE, "unexpected_per_year": 6}
    )
    fake = SimpleNamespace(
        _current_date=day,
        settings=settings,
        _random_seed=seed,
        _engine=engine,
        _macro=SimpleNamespace(
            latest=lambda _day: SimpleNamespace(unemployment=unemployment)
        ),
        get_cash=lambda _client: engine.cash,
    )
    living = cast(Simulation, fake)
    fake._layoff_factor = partial(Simulation._layoff_factor, living)
    fake._net_salary = partial(Simulation._net_salary, living)
    return living, LifeBudget.of(settings)


def test_first_trading_day_pays_salary_then_expense_and_draws_the_event(
    captured_events: list,
):
    day = date(2020, 3, 2)
    seed = next(s for s in range(500) if unexpected_on(s, day, 6) is not None)
    engine = _RecordingEngine()
    fake, life = _living(day, seed, engine)
    drawn = unexpected_on(seed, day, 6)
    assert drawn is not None

    Simulation._live(
        fake, life, [UserDTO(id=1, client_id=client("Ana"), nickname="Ana")], True
    )

    skipped = salary_skipped(seed, day, 6, fake.settings.start_date)
    expected = [] if skipped else [("salary", Decimal(8000))]
    expected += [("expense", Decimal(5000)), (drawn.key, drawn.expense_multiple * 5000)]
    assert engine.calls == expected


def test_negative_cash_pays_interest_and_positive_cash_does_not(
    captured_events: list, indicators: SetIndicator
):
    day = date(2020, 3, 2)
    indicators(
        IndicatorSeries.SELIC,
        daily_series(date(2019, 1, 1), date(2021, 1, 1), "0.0551"),
    )
    ana = UserDTO(id=1, client_id=client("Ana"), nickname="Ana")
    negative = _RecordingEngine(Decimal(-1000))
    positive = _RecordingEngine(Decimal(10))

    Simulation._charge_overdraft(_living(day, 1, negative)[0], [ana])
    Simulation._charge_overdraft(_living(day, 1, positive)[0], [ana])

    rate = _overdraft_rate(day)
    assert negative.calls == [("interest", overdraft_interest(Decimal(-1000), rate))]
    assert positive.calls == []


def test_overdraft_rate_is_the_selic_of_the_day_plus_the_fixed_spread(
    indicators: SetIndicator,
):
    day = date(2020, 3, 2)
    indicators(
        IndicatorSeries.SELIC,
        daily_series(date(2019, 1, 1), date(2021, 1, 1), "0.0551"),
    )
    selic_monthly = period_rate(
        annual_index_rate(IndicatorSeries.SELIC, day), Decimal(MONTHS_PER_YEAR)
    )
    spread = Decimal(str(config.toml.simulation.overdraft_monthly_spread))
    assert _overdraft_rate(day) == selic_monthly + spread

    indicators(
        IndicatorSeries.SELIC,
        daily_series(date(2019, 1, 1), date(2021, 1, 1), "0.0300"),
    )
    assert _overdraft_rate(day) < selic_monthly + spread


def _months_without_salary(unemployment: str, seed: int) -> int:
    fake, _life = _living(
        date(2020, 1, 2), seed, _RecordingEngine(), Decimal(unemployment)
    )
    start = fake.settings.start_date
    months = [date(2020 + n // 12, n % 12 + 1, 1) for n in range(1, 240)]
    return sum(
        salary_skipped(
            seed,
            month,
            6,
            start,
            layoff_factor_on=partial(Simulation._layoff_factor, fake),
        )
        for month in months
    )


def test_high_unemployment_skips_more_salaries_than_low_with_the_same_seed():
    assert _months_without_salary("0.16", 11) > _months_without_salary("0.05", 11)


def test_budget_changes_carry_the_origin_of_each_change(indicators: SetIndicator):
    indicators(IndicatorSeries.IPCA, monthly_series(date(2019, 1, 1), 48, "0.4"))
    indicators(
        IndicatorSeries.SELIC,
        daily_series(date(2019, 1, 1), date(2023, 1, 1), "0.0551"),
    )
    settings = simulation_settings().model_copy(
        update={
            "game_type": GameType.FINANCIAL_INDEPENDENCE,
            "inflation_adjusted": True,
        }
    )
    life = LifeBudget.of(settings, lambda _day: Decimal("0.031"))
    until = date(2021, 6, 1)

    changes = budget_changes(life, until, lambda _day: Decimal("0.20"), _overdraft_rate)

    kinds = {c.kind for c in changes}
    assert kinds == {
        LifeHistoryKind.SALARY_READJUSTED,
        LifeHistoryKind.EXPENSE_READJUSTED,
        LifeHistoryKind.SALARY_TAX_CHANGED,
        LifeHistoryKind.OVERDRAFT_RATE_CHANGED,
    }
    salary = next(c for c in changes if c.kind is LifeHistoryKind.SALARY_READJUSTED)
    assert "PIB de 3,1%" in salary.label
    tax = next(c for c in changes if c.kind is LifeHistoryKind.SALARY_TAX_CHANGED)
    assert "IR das pessoas em 20,0% (referência de 15,0%)" in tax.label
    assert [c.day for c in changes] == sorted(c.day for c in changes)


def test_recession_raise_says_there_is_no_real_raise(indicators: SetIndicator):
    indicators(IndicatorSeries.IPCA, monthly_series(date(2019, 1, 1), 48, "0.4"))
    indicators(
        IndicatorSeries.SELIC,
        daily_series(date(2019, 1, 1), date(2023, 1, 1), "0.0551"),
    )
    settings = simulation_settings().model_copy(update={"inflation_adjusted": True})
    life = LifeBudget.of(settings, lambda _day: Decimal("-0.02"))

    changes = budget_changes(
        life, date(2021, 6, 1), lambda _day: Decimal("0.15"), _overdraft_rate
    )

    salary = next(c for c in changes if c.kind is LifeHistoryKind.SALARY_READJUSTED)
    assert "sem reajuste real (PIB de -2,0%)" in salary.label


def test_history_interleaves_budget_changes_by_date_and_cites_unemployment():
    changes = [
        BudgetChange(
            date(2012, 6, 4), LifeHistoryKind.OVERDRAFT_RATE_CHANGED, "Juro a 8,0%"
        ),
        BudgetChange(
            date(2012, 7, 2), LifeHistoryKind.SALARY_READJUSTED, "Salário novo"
        ),
        BudgetChange(
            date(2013, 1, 2), LifeHistoryKind.EXPENSE_READJUSTED, "Despesa nova"
        ),
    ]

    rows = build_history(EVENTS, changes, lambda _day: Decimal("0.123"))

    assert [r.kind for r in rows][:2] == [
        LifeHistoryKind.OVERDRAFT_RATE_CHANGED,
        LifeHistoryKind.UNEXPECTED_EXPENSE,
    ]
    assert rows[0].cash_after == Decimal(2660)
    assert rows[-1].kind is LifeHistoryKind.EXPENSE_READJUSTED
    assert rows[-1].cash_after == rows[-2].cash_after
    layoff = next(r for r in rows if r.kind is LifeHistoryKind.LAYOFF)
    assert layoff.label == "Desemprego de 12,3%"
    page = history_page(rows, LifeHistoryCategory.BUDGET, 0, 10)
    assert page.total == page.counts.budget == 3
