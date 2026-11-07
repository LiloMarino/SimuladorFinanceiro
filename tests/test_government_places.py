from datetime import date
from decimal import Decimal

import pytest

from backend.core.enum import BrazilState, Region, VoterGroup
from backend.features.government import places, poll_panel, voters
from backend.features.government.voters import GroupVote, Vote

# As fatias das regiões no eleitorado dos 27 estados (TSE 2022), em pontos percentuais
REGION_SHARES = {
    Region.NORTH: 8.06,
    Region.NORTHEAST: 27.22,
    Region.MIDWEST: 7.41,
    Region.SOUTHEAST: 42.83,
    Region.SOUTH: 14.48,
}
SEED = 7
DAY = date(2021, 6, 30)


def national_vote() -> Vote:
    """Um país em que cada grupo vota de um jeito: o partido 1 puxa os pobres, o 2 os ricos."""
    groups = {
        VoterGroup.WELFARE: {1: Decimal(70), 2: Decimal(10)},
        VoterGroup.RETIREES: {1: Decimal(45), 2: Decimal(35)},
        VoterGroup.FORMAL_WORKERS: {1: Decimal(40), 2: Decimal(40)},
        VoterGroup.PUBLIC_SERVANTS: {1: Decimal(35), 2: Decimal(45)},
        VoterGroup.ENTREPRENEURS: {1: Decimal(20), 2: Decimal(65)},
        VoterGroup.INVESTORS: {1: Decimal(10), 2: Decimal(80)},
    }
    return voters.combine(
        {
            g: GroupVote(shares=t, undecided=Decimal(100) - sum(t.values()))
            for g, t in groups.items()
        }
    )


def test_every_state_mixture_adds_up_to_one():
    for state in BrazilState:
        assert float(sum(places.MIXTURES[state].values())) == pytest.approx(
            1, abs=1e-12
        )


def test_weighted_mixtures_close_the_national_weights():
    for group in VoterGroup:
        total = sum(places.share(s) * places.MIXTURES[s][group] for s in BrazilState)
        assert float(total) == pytest.approx(float(voters.WEIGHTS[group]), abs=1e-9)


def test_region_shares_follow_the_electorate():
    for region, expected in REGION_SHARES.items():
        assert float(places.share(region)) * 100 == pytest.approx(expected, abs=0.01)
    assert float(sum(places.share(r) for r in Region)) == pytest.approx(1)


def test_region_mixture_is_the_electorate_weighted_average_of_its_states():
    region = Region.NORTHEAST
    mixture = places.mixture(region)
    assert float(sum(mixture.values())) == pytest.approx(1, abs=1e-12)
    low = min(places.MIXTURES[s][VoterGroup.WELFARE] for s in places.states_of(region))
    high = max(places.MIXTURES[s][VoterGroup.WELFARE] for s in places.states_of(region))
    assert low <= mixture[VoterGroup.WELFARE] <= high


def test_poorer_states_hold_more_welfare_than_richer_ones():
    welfare = {s: places.MIXTURES[s][VoterGroup.WELFARE] for s in BrazilState}
    assert welfare[BrazilState.PI] > welfare[BrazilState.SP]
    assert welfare[BrazilState.BA] > welfare[BrazilState.SC]


def test_margin_follows_the_size_of_the_state():
    assert places.margin(BrazilState.SP) == 3
    assert places.margin(BrazilState.BA) == 5
    assert places.margin(BrazilState.AC) == 12
    assert places.margin(Region.SOUTH) == 4
    assert places.margin(Region.NORTH) == 5
    assert places.margin(Region.MIDWEST) == 5


def test_tab_order_runs_from_the_biggest_electorate_to_the_smallest():
    assert places.TAB_ORDER[0] is BrazilState.SP
    assert len(places.TAB_ORDER) == len(BrazilState)
    sizes = [places.ELECTORATE[s] for s in places.TAB_ORDER]
    assert sizes == sorted(sizes, reverse=True)


def test_every_state_belongs_to_one_region():
    assert set(places.REGION_OF) == set(BrazilState)
    assert sum(len(places.states_of(r)) for r in Region) == len(BrazilState)


def test_place_vote_is_deterministic_and_inside_the_margin():
    exact = national_vote()
    for place in places.all_places():
        first = poll_panel.place_vote(exact, place, DAY, SEED, True)
        again = poll_panel.place_vote(exact, place, DAY, SEED, True)
        truth = poll_panel.place_vote(exact, place, DAY, SEED, False)
        assert first.total == again.total
        if isinstance(place, BrazilState):
            for pid, value in first.total.items():
                assert abs(value - truth.total[pid]) <= places.margin(place)


def test_place_vote_without_margin_is_the_exact_mixture():
    exact = national_vote()
    local = poll_panel.place_vote(exact, BrazilState.PI, DAY, SEED, False)
    assert (
        local.total
        == voters.combine(exact.groups, weights=places.MIXTURES[BrazilState.PI]).total
    )


def test_poorer_state_leans_to_the_party_of_the_poor():
    exact = national_vote()
    poor = poll_panel.place_vote(exact, BrazilState.PI, DAY, SEED, False)
    rich = poll_panel.place_vote(exact, BrazilState.SP, DAY, SEED, False)
    assert poor.total[1] > rich.total[1]
    assert poor.total[2] < rich.total[2]
