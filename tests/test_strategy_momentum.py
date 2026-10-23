"""Momentum de 12 meses: a troca do primeiro pregão do mês e o ranking que a página mostra."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from backend.core.dto.strategy import RankingViewDTO
from backend.core.enum import StrategyAction
from backend.features.strategy.context import Holding
from backend.features.strategy.momentum import TwelveMonthMomentum
from tests.strategy_helpers import closes, context

PARAMS = {"top": 2, "tickers": ["AAA", "BBB", "CCC", "DDD"]}
DAYS = 253


def ramp(start: float, end: float, days: int = DAYS) -> list[float]:
    """Preços em linha reta do primeiro ao último dia."""
    step = (end - start) / (days - 1)
    return [start + step * i for i in range(days)]


def frames(**ends: float | list[float]):
    return {
        ticker: closes(end if isinstance(end, list) else ramp(100.0, end))
        for ticker, end in ends.items()
    }


# AAA +100%, BBB +50%, CCC +20% e DDD -20% em 12 meses
HISTORY = frames(AAA=200.0, BBB=150.0, CCC=120.0, DDD=80.0)


def run(params=PARAMS, **kwargs):
    ctx = context(history=HISTORY, **kwargs)
    TwelveMonthMomentum().next(ctx, params)
    return ctx


def test_sells_what_left_the_ranking_and_buys_the_ones_that_entered_in_equal_parts():
    ctx = run(
        cash="10000",
        holdings={"CCC": Holding("CCC", Decimal(100), Decimal(0), Decimal(100))},
    )

    sell, buy_a, buy_b = ctx.intents
    assert (sell.action, sell.ticker, sell.quantity) == (
        StrategyAction.SELL,
        "CCC",
        100,
    )
    # (R$ 10.000 de caixa + R$ 12.000 em CCC) / 2 ações = R$ 11.000 para cada
    assert (buy_a.ticker, buy_a.quantity) == ("AAA", 55)
    assert (buy_b.ticker, buy_b.quantity) == ("BBB", 73)
    assert "ranking" in buy_a.reason


def test_does_not_sell_the_part_held_by_open_orders():
    ctx = run(
        cash="0",
        holdings={"CCC": Holding("CCC", Decimal(100), Decimal(40), Decimal(100))},
    )

    [sell, *_] = ctx.intents
    assert sell.quantity == 60


def test_keeps_what_is_still_in_the_ranking_and_only_buys_the_shortfall():
    ctx = run(
        cash="1000",
        holdings={"AAA": Holding("AAA", Decimal(50), Decimal(0), Decimal(100))},
    )

    # AAA vale R$ 10.000 e a parte de cada uma é R$ 5.500: não compra mais AAA
    assert [(i.ticker, i.action) for i in ctx.intents] == [("BBB", StrategyAction.BUY)]


def test_a_stock_with_a_negative_return_stays_out_and_its_share_stays_in_cash():
    ctx = run({**PARAMS, "top": 4}, cash="10000")

    assert [i.ticker for i in ctx.intents] == ["AAA", "BBB", "CCC"]
    # R$ 10.000 / 4 ações: a parte de DDD fica em caixa
    assert ctx.intents[0].quantity == 12


def test_does_nothing_outside_the_first_session_of_the_month():
    # O pregão anterior é do mesmo mês de hoje
    ctx = context(history=HISTORY)
    ctx = replace(ctx, date=date(2004, 5, 31))
    TwelveMonthMomentum().next(ctx, PARAMS)
    assert ctx.intents == []


def test_a_stock_without_a_year_of_history_stays_out_of_the_ranking():
    history = {**HISTORY, "AAA": closes(ramp(100.0, 500.0, 100))}
    ctx = context(history=history)

    TwelveMonthMomentum().next(ctx, PARAMS)

    assert [i.ticker for i in ctx.intents] == ["BBB", "CCC"]


def test_the_view_ranks_by_the_return_and_marks_the_ones_it_keeps():
    ctx = context(history=HISTORY)

    view = TwelveMonthMomentum().view(ctx, PARAMS)

    assert isinstance(view, RankingViewDTO)
    assert [(r.ticker, r.selected) for r in view.rows] == [
        ("AAA", True),
        ("BBB", True),
        ("CCC", False),
        ("DDD", False),
    ]
    assert [r.return_12m for r in view.rows] == [
        Decimal("1.0000"),
        Decimal("0.5000"),
        Decimal("0.2000"),
        Decimal("-0.2000"),
    ]
    assert view.next_switch == date(2004, 7, 1)
    assert view.needed_days == 253


def test_the_view_puts_the_stocks_without_history_last():
    history = {**HISTORY, "AAA": closes(ramp(100.0, 500.0, 100))}
    view = TwelveMonthMomentum().view(context(history=history), PARAMS)

    assert isinstance(view, RankingViewDTO)
    assert view.rows[-1].ticker == "AAA"
    assert view.rows[-1].return_12m is None
    assert not view.rows[-1].selected


def test_the_view_has_no_selection_when_nothing_rose():
    history = frames(AAA=80.0, BBB=90.0, CCC=70.0, DDD=60.0)
    view = TwelveMonthMomentum().view(context(history=history), PARAMS)

    assert isinstance(view, RankingViewDTO)
    assert not any(row.selected for row in view.rows)


def test_needs_a_year_of_sessions_plus_today():
    assert TwelveMonthMomentum.needed_days(PARAMS) == 253


@pytest.mark.parametrize(
    ("params", "field"),
    [
        ({**PARAMS, "top": 0}, "top"),
        ({**PARAMS, "top": 11}, "top"),
        ({**PARAMS, "tickers": []}, "tickers"),
        ({**PARAMS, "tickers": ["ZZZ"]}, "tickers"),
    ],
)
def test_validate_reports_the_field_that_is_out_of_range(params, field):
    assert TwelveMonthMomentum.validate(params, {"AAA", "BBB"})[field]


def test_validate_accepts_the_defaults():
    known = {"AAA", "BBB", "CCC", "DDD"}
    assert TwelveMonthMomentum.validate(PARAMS, known) == {}
