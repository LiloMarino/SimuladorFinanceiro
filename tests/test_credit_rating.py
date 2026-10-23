from datetime import date
from decimal import Decimal

import pytest

from backend.core.enum import CreditGrade
from backend.features.credit.rating import (
    count_recent_late,
    leverage,
    payoff_to_next_grade,
    score,
    volatility_to_next_grade,
)
from backend.features.credit.rules import grade_for_points, next_tier, tier_of

D = Decimal


@pytest.mark.parametrize(
    ("points", "grade"),
    [
        (100, CreditGrade.AAA),
        (90, CreditGrade.AAA),
        (88, CreditGrade.AA),
        (78, CreditGrade.A),
        (72, CreditGrade.A),
        (68, CreditGrade.BBB),
        (50, CreditGrade.BB),
        (40, CreditGrade.B),
        (30, CreditGrade.CCC),
        (24, CreditGrade.D),
        (0, CreditGrade.D),
    ],
)
def test_grade_cuts(points, grade):
    assert grade_for_points(points) is grade


def test_ladder_neighbours():
    assert next_tier(CreditGrade.AAA) is None
    above = next_tier(CreditGrade.A)
    assert above is not None
    assert above.grade is CreditGrade.AA
    assert tier_of(CreditGrade.D).spread is None


def test_score_matches_board():
    # Dívida 99.915,58 sobre patrimônio 386.284,42, volatilidade 18%, sem atrasos
    result = score(D("99915.58"), D("386284.42"), D("0.18"), 63, 0)
    assert result.points == 78
    assert result.grade is CreditGrade.A
    assert round(result.volatility_points) == 18
    assert result.payment_points == 30


def test_score_after_new_loan_matches_board():
    result = score(D("149915.58"), D("386284.42"), D("0.18"), 63, 0)
    assert result.points == 72
    assert result.grade is CreditGrade.A


def test_no_debt_has_full_leverage_points():
    assert score(D(0), D(100000), D("0.10"), 63, 0).leverage_points == 40


def test_negative_networth_zeroes_leverage_points():
    assert leverage(D(1000), D(-5)) > 1000
    assert score(D(1000), D(-5), D("0.10"), 63, 0).leverage_points == 0


def test_short_history_counts_zero_volatility():
    assert score(D(0), D(100000), D("0.90"), 10, 0).volatility_points == 30


def test_volatility_ceiling_zeroes_points():
    assert score(D(0), D(100000), D("0.45"), 63, 0).volatility_points == 0
    assert score(D(0), D(100000), D("0.80"), 63, 0).volatility_points == 0


def test_late_installments_cost_ten_points_each():
    assert score(D(0), D(1), D("0.1"), 63, 1).payment_points == 20
    assert score(D(0), D(1), D("0.1"), 63, 5).payment_points == 0


def test_recent_late_window_is_twelve_months():
    today = date(2020, 4, 11)
    late = [date(2019, 4, 11), date(2019, 4, 12), date(2020, 4, 5)]
    assert count_recent_late(late, today) == 2


def test_payoff_to_next_grade_matches_board():
    current = score(D("99915.58"), D("386284.42"), D("0.18"), 63, 0)
    needed = payoff_to_next_grade(current, D("99915.58"), D("386284.42"))
    assert needed is not None
    assert round(needed, -2) == D(22700)


def test_volatility_to_next_grade_reaches_the_next_grade():
    current = score(D("99915.58"), D("386284.42"), D("0.18"), 63, 0)
    ceiling = volatility_to_next_grade(current)
    assert ceiling is not None and ceiling < D("0.18")
    assert score(D("99915.58"), D("386284.42"), ceiling, 63, 0).grade is CreditGrade.AA


def test_no_suggestion_when_leverage_alone_cannot_help():
    # Sem volatilidade nem pagamentos, só a alavancagem (40 pontos) não chega a BB
    current = score(D(0), D(1000), D("0.90"), 63, 3)
    assert current.grade is CreditGrade.B
    assert payoff_to_next_grade(current, D(0), D(1000)) is None
