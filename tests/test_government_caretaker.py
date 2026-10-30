"""O governo do computador depois do impeachment sem vice: quem assume e o que ele propõe."""

from decimal import Decimal

from backend.core.enum import MeasureKind, VoterGroup
from backend.core.utils import required
from backend.features.government import caretaker, house, voters

BASELINES = {
    MeasureKind.STOCK_PROFIT_RATE: Decimal("0.15"),
    MeasureKind.DAY_TRADE_RATE: Decimal("0.20"),
    MeasureKind.STOCK_EXEMPTION: Decimal(20000),
    MeasureKind.FIXED_INCOME_TABLE: Decimal("0.15"),
    MeasureKind.LCI_LCA_RATE: Decimal(0),
    MeasureKind.WELFARE_SPENDING: Decimal("0.015"),
    MeasureKind.PUBLIC_WORKS: Decimal("0.007"),
    MeasureKind.SERVANT_RAISE: Decimal(0),
    MeasureKind.RETIREE_RAISE: Decimal(0),
}
RETIREES = {group: Decimal(0) for group in VoterGroup} | {
    VoterGroup.RETIREES: Decimal(1)
}


def bloc(key: int, seats: int, party_id: int | None, computer: bool = True):
    return house.Bloc(
        key=key,
        party_id=party_id,
        abbr=f"P{abs(key)}",
        name=f"Partido {abs(key)}",
        color=None,
        is_computer=computer,
        votes=Decimal(seats),
        seats=seats,
        mix=RETIREES,
    )


def test_the_computer_bloc_with_most_seats_takes_office():
    current = house.House(
        (bloc(-1, 20, 10), bloc(-2, 31, 11), bloc(-3, 15, 12), bloc(5, 35, 5, False))
    )

    heir = required(caretaker.successor(current, {10, 11, 12}))

    # A bancada de jogador, maior, não entra: assume o computador de mais cadeiras
    assert heir.key == -2


def test_a_tie_goes_to_the_first_computer_party_and_a_bloc_without_party_is_skipped():
    tied = house.House((bloc(-3, 30, 12), bloc(-1, 30, 10), bloc(-2, 41, None)))

    heir = required(caretaker.successor(tied, {10, 12}))

    assert heir.key == -1


def test_without_a_computer_party_in_the_game_nobody_takes_office():
    current = house.House((bloc(-1, 50, None), bloc(5, 51, 5, False)))

    assert caretaker.successor(current, set()) is None


def test_the_pick_is_the_step_the_bloc_voters_want_most():
    choice = required(caretaker.pick(RETIREES, BASELINES, set()))

    assert choice.score == caretaker.wanted(
        RETIREES, choice.kind, choice.value, choice.before
    )
    # Os aposentados querem o reajuste deles: o computador sobe um passo
    assert (choice.kind, choice.value) == (MeasureKind.RETIREE_RAISE, Decimal("0.03"))


def test_each_kind_is_tried_once_and_the_list_runs_out():
    tried: set[MeasureKind] = set()
    while choice := caretaker.pick(RETIREES, BASELINES, tried):
        assert choice.kind not in tried
        assert choice.value >= 0
        assert abs(choice.value - choice.before) == voters.EFFECT_STEPS[choice.kind]
        tried.add(choice.kind)

    assert 0 < len(tried) <= len(BASELINES)
    assert caretaker.pick(RETIREES, BASELINES, set(BASELINES)) is None
