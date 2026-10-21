from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import cast

import pytest
from pydantic import ValidationError

from backend.core.dto.events.cashflow import CashflowEventDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import (
    CASH_SIGN,
    CONTRIBUTION_TYPES,
    CashflowEventType,
    GameType,
    LifeHistoryCategory,
    LifeHistoryKind,
)
from backend.core.life_budget import LifeBudget
from backend.features.simulation.life_events import (
    layoff_in,
    salary_skipped,
    unexpected_on,
)
from backend.features.simulation.life_history import build_history, history_page
from backend.features.simulation.simulation import Simulation
from backend.routes.simulation import CreateSimulationRequest
from tests.fakes import client, simulation_settings

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

    def pay_salary(self, _client, amount: Decimal) -> None:
        self.calls.append(("salary", amount))

    def pay_expense(self, _client, amount: Decimal) -> None:
        self.calls.append(("expense", amount))

    def charge_unexpected(self, _client, amount: Decimal, key: str) -> None:
        self.calls.append((key, amount))

    def charge_overdraft_interest(self, _client, amount: Decimal) -> None:
        self.calls.append(("interest", amount))


def _living(day: date, seed: int, engine: _RecordingEngine):
    settings = simulation_settings().model_copy(
        update={"game_type": GameType.FINANCIAL_INDEPENDENCE, "unexpected_per_year": 6}
    )
    return cast(
        Simulation,
        SimpleNamespace(
            _current_date=day,
            settings=settings,
            _random_seed=seed,
            _engine=engine,
            get_cash=lambda _client: engine.cash,
        ),
    ), LifeBudget.of(settings)


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


def test_negative_cash_pays_interest_and_positive_cash_does_not(captured_events: list):
    ana = UserDTO(id=1, client_id=client("Ana"), nickname="Ana")
    negative = _RecordingEngine(Decimal(-1000))
    positive = _RecordingEngine(Decimal(10))

    Simulation._charge_overdraft(_living(date(2020, 3, 2), 1, negative)[0], [ana])
    Simulation._charge_overdraft(_living(date(2020, 3, 2), 1, positive)[0], [ana])

    assert negative.calls == [("interest", Decimal("3.67"))]
    assert positive.calls == []
