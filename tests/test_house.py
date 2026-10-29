"""A casa do Congresso: cadeiras por D'Hondt com barreira, orientação, desobediência sorteada e impeachment."""

from decimal import Decimal

import pytest

from backend.core.enum import VoterGroup, VoterValue
from backend.features.government import house, voters

SEED = 7
HALF = Decimal("0.5")


def bloc(key: int, seats: int) -> house.Bloc:
    mix = {g: voters.WEIGHTS[g] for g in VoterGroup}
    return house.Bloc(
        key, key, f"P{key}", f"Partido {key}", None, False, Decimal(0), seats, mix
    )


def chamber(*seats: int) -> house.House:
    return house.House(tuple(bloc(i + 1, n) for i, n in enumerate(seats)))


# Cadeiras


def test_dhondt_gives_every_seat_and_favours_the_larger_party():
    cut = house.distribute({1: Decimal(30), 2: Decimal(30), 3: Decimal(40)})

    assert sum(cut.seats.values()) == house.SEATS
    assert cut.seats[3] > cut.seats[1]
    # Os dois de 30% empatam ou ficam a uma cadeira de distância
    assert abs(cut.seats[1] - cut.seats[2]) <= 1
    assert cut.below == ()


def test_a_party_under_the_barrier_gets_no_seat_and_its_votes_go_to_the_others():
    cut = house.distribute({1: Decimal(96), 2: Decimal(4)})

    assert cut.below == (2,)
    assert cut.seats == {1: house.SEATS, 2: 0}


def test_a_party_just_above_the_barrier_wins_seats():
    cut = house.distribute({1: Decimal(94), 2: Decimal(6)})

    assert cut.below == ()
    assert 4 <= cut.seats[2] <= 8


def test_the_last_quotient_beats_the_one_left_out():
    cut = house.distribute({1: Decimal(55), 2: Decimal(30), 3: Decimal(15)})

    assert cut.last >= cut.upcoming


def test_history_weighs_more_than_the_campaign_purse():
    radar = voters.initial_radar([VoterValue.STABILITY])
    group = VoterGroup.INVESTORS
    loyalty = house.strength(group, radar, Decimal(3), Decimal(0), Decimal(0))
    campaign = house.strength(group, radar, Decimal(0), Decimal(0), Decimal(6))

    assert loyalty > campaign


def test_rejection_takes_strength_but_never_below_zero():
    radar = voters.initial_radar([VoterValue.STABILITY])

    assert house.strength(
        VoterGroup.INVESTORS, radar, Decimal(0), Decimal(500), Decimal(0)
    ) == Decimal(0)


def test_the_first_house_belongs_to_the_three_computer_parties():
    first = house.initial_house()

    assert all(b.is_computer for b in first.blocs)
    assert sum(b.seats for b in first.blocs) == house.SEATS
    assert {b.key for b in first.blocs} == set(house.COMPUTER_KEYS.values())


def test_an_election_turns_votes_into_a_house_of_101_seats():
    candidates = [
        house.Candidate(i, f"P{i}", f"Partido {i}", None, False, i) for i in (1, 2)
    ]
    radar = voters.initial_radar([VoterValue.FREE_MARKET])
    strengths = {
        1: {
            g: house.strength(g, radar, Decimal(0), Decimal(0), Decimal(0))
            for g in VoterGroup
        },
        2: {
            g: house.strength(g, radar, Decimal(2), Decimal(0), Decimal(0))
            for g in VoterGroup
        },
    }

    elected = house.elect(candidates, strengths)

    assert sum(b.seats for b in elected.blocs) == house.SEATS
    assert elected.bloc(2).seats > elected.bloc(1).seats  # type: ignore[union-attr]
    for each in elected.blocs:
        assert sum(each.mix.values()) == pytest.approx(1)


# Orientação


def test_the_default_guidance_is_yes_on_the_flags_and_no_on_the_rest():
    rules = house.flag_rules([VoterValue.STABILITY, VoterValue.DEVELOPMENT])

    assert rules[VoterValue.STABILITY] is True
    assert rules[VoterValue.DEVELOPMENT] is True
    assert rules[VoterValue.SOCIAL_JUSTICE] is False


def test_the_measure_is_read_by_the_value_it_pulls_the_most():
    effects = {
        VoterValue.STABILITY: Decimal(2),
        VoterValue.FREE_MARKET: Decimal(5),
        VoterValue.SOCIAL_JUSTICE: Decimal(-8),
    }
    rules = house.flag_rules([VoterValue.FREE_MARKET])

    assert house.pulled_value(effects) is VoterValue.FREE_MARKET
    assert house.default_orientation(rules, effects) is True
    assert (
        house.default_orientation(house.flag_rules([VoterValue.STABILITY]), effects)
        is False
    )


def test_a_measure_that_only_retreats_values_is_voted_no():
    effects = {VoterValue.STABILITY: Decimal(-3)}

    assert house.pulled_value(effects) is None
    assert (
        house.default_orientation(house.flag_rules(list(VoterValue)), effects) is False
    )


# Desobediência


def test_defection_grows_with_contrariety_up_to_a_third_of_the_bloc():
    assert house.defection(Decimal(0)) == 0
    assert house.defection(HALF) == house.DISOBEDIENCE_MAX / 2
    assert house.defection(Decimal(1)) == house.DISOBEDIENCE_MAX
    assert house.defection(Decimal(5)) == house.DISOBEDIENCE_MAX


def test_contrariety_is_the_wish_for_the_opposite_vote():
    # Orientada a Sim, a bancada só contraria se os eleitores querem o Não (querer < 0)
    assert house.contrariety(True, Decimal("-0.4")) == Decimal("0.4")
    assert house.contrariety(True, Decimal("0.4")) == 0
    assert house.contrariety(False, Decimal("0.4")) == Decimal("0.4")
    assert house.contrariety(False, Decimal("-0.4")) == 0


def test_a_bloc_whose_voters_agree_votes_as_oriented_to_the_last_deputy():
    current = chamber(60, 41)

    tally = house.count(
        "measure:1", SEED, current, {1: True, 2: False}, {1: Decimal(1), 2: Decimal(-1)}
    )

    assert (tally.yes, tally.no, tally.defected) == (60, 41, 0)


def test_the_draw_is_the_same_for_the_same_seed_and_vote():
    current = chamber(60, 41)
    args = ({1: True, 2: True}, {1: Decimal(-1), 2: Decimal(-1)})

    assert house.count("a", SEED, current, *args) == house.count(
        "a", SEED, current, *args
    )
    assert house.count("a", SEED, current, *args) != house.count(
        "b", SEED + 1, current, *args
    )


def test_contrary_voters_pull_up_to_a_third_of_the_bloc_against_the_orientation():
    current = chamber(90)

    tally = house.count("measure:1", SEED, current, {1: True}, {1: Decimal(-1)})

    # Terço de 90 = 30; o sorteio cai perto disso
    assert 15 <= tally.defected <= 45
    assert tally.yes == 90 - tally.defected
    assert tally.blocs[1].defected == tally.defected


def test_the_forecast_band_holds_most_drawn_results():
    current = chamber(50, 30, 21)
    orientations = {1: True, 2: False, 3: True}
    wanted = {1: Decimal("-0.6"), 2: Decimal("0.3"), 3: Decimal(1)}

    low, high = house.forecast(current, orientations, wanted)

    # A faixa usa o teto esperado de desobedientes; o sorteio deputado a deputado a respeita na média
    results = [
        house.count(f"v{n}", SEED, current, orientations, wanted).yes
        for n in range(200)
    ]
    assert low <= high
    assert low <= sum(results) / len(results) <= high
    assert sum(low <= yes <= high for yes in results) >= 0.8 * len(results)


def test_the_may_defect_ceiling_rounds_up_and_never_passes_the_bloc():
    assert house.may_defect(10, True, Decimal(0)) == 0
    assert house.may_defect(10, True, Decimal(-1)) == 4
    assert house.may_defect(2, True, Decimal(-9)) == 1


def test_the_group_that_most_wants_the_opposite_is_named():
    mix = {g: Decimal(0) for g in VoterGroup}
    mix[VoterGroup.INVESTORS] = Decimal("0.5")
    mix[VoterGroup.WELFARE] = Decimal("0.5")
    by_group = {g: Decimal(0) for g in VoterGroup}
    by_group[VoterGroup.INVESTORS] = Decimal("-0.2")
    by_group[VoterGroup.WELFARE] = Decimal("-0.8")

    assert house.contrary_group(mix, by_group, True) is VoterGroup.WELFARE
    assert house.contrary_group(mix, by_group, False) is None


# Impeachment


def test_the_impeachment_guidance_follows_the_voters_mood():
    mix = {g: voters.WEIGHTS[g] for g in VoterGroup}
    low = {g: Decimal(20) for g in VoterGroup}
    high = {g: Decimal(60) for g in VoterGroup}

    assert house.impeachment_orientation(house.mood(mix, low)) is True
    assert house.impeachment_orientation(house.mood(mix, high)) is False


def test_the_voters_want_the_exit_fully_at_zero_satisfaction_and_not_at_the_floor():
    zero = house.impeachment_reactions({g: Decimal(0) for g in VoterGroup})
    floor = house.impeachment_reactions({g: Decimal(25) for g in VoterGroup})
    happy = house.impeachment_reactions({g: Decimal(75) for g in VoterGroup})

    assert set(zero.values()) == {Decimal(1)}
    assert set(floor.values()) == {Decimal(0)}
    assert all(v < 0 for v in happy.values())


def test_the_impeachment_needs_68_of_101_and_a_measure_51():
    assert house.IMPEACHMENT_VOTES == 68
    assert house.MAJORITY == 51
    assert house.SEATS == 101
