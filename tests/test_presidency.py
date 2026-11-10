"""O legado do presidente: cada mês fechado soma salários pela aprovação acima do piso."""

from datetime import date
from decimal import Decimal

from backend.core.enum import VoterGroup
from backend.features.government import presidency
from backend.features.government.state import ApprovalPoint


def month(rating: int, day: date = date(2022, 1, 31)) -> ApprovalPoint:
    """Um fechamento em que todos os grupos têm a mesma satisfação: a aprovação geral é ela."""
    return ApprovalPoint(day, {group: Decimal(rating) for group in VoterGroup})


def test_no_closed_month_leaves_no_legacy():
    assert presidency.legacy_salaries([]) == 0


def test_each_point_above_the_floor_adds_five_percent_of_a_salary():
    assert presidency.legacy_salaries([month(60)]) == 1
    assert presidency.legacy_salaries([month(80)]) == 2
    assert presidency.legacy_salaries([month(100)]) == 3


def test_approval_at_or_below_the_floor_adds_nothing():
    assert presidency.legacy_salaries([month(40)]) == 0
    assert presidency.legacy_salaries([month(30)]) == 0


def test_months_add_up():
    months = [month(60), month(80), month(30), month(50)]

    assert presidency.legacy_salaries(months) == Decimal("3.5")
    assert presidency.month_salaries(months[-1]) == Decimal("0.5")


def test_average_approval_is_the_mean_of_the_closed_months():
    assert presidency.average_approval([]) == 0
    assert presidency.average_approval([month(60), month(80), month(30)]) == 57
