"""Grupos de eleitores: bandeiras, afinidade, apoio, rejeição, voto por grupo e a pesquisa com margem."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core.enum import MeasureKind, VoterGroup, VoterValue
from backend.features.government import voters

G = VoterGroup
V = VoterValue

MARKET_PARTY = (V.FREE_MARKET, V.STABILITY, V.SAVER_PROTECTION)
SOCIAL_PARTY = (V.SOCIAL_JUSTICE, V.STABILITY, V.PUBLIC_SERVICE)


def test_group_weights_add_up_to_the_whole_electorate():
    assert sum(voters.WEIGHTS.values()) == 1


@pytest.mark.parametrize(
    ("flags", "valid"),
    [
        (MARKET_PARTY, True),
        ((V.FREE_MARKET, V.STABILITY), False),
        ((V.FREE_MARKET, V.FREE_MARKET, V.STABILITY), False),
        ((V.FREE_MARKET, V.SOCIAL_JUSTICE, V.STABILITY), False),
        ((V.FREE_MARKET, V.STABILITY, V.DEVELOPMENT, V.PUBLIC_SERVICE), False),
    ],
)
def test_a_party_has_three_different_flags_and_never_both_extremes(
    flags: tuple[VoterValue, ...], valid: bool
):
    assert voters.is_valid_flags(flags) is valid


def test_flags_start_high_on_the_profile_and_the_rest_neutral():
    radar = voters.initial_radar(MARKET_PARTY)

    assert radar[V.FREE_MARKET] == voters.RADAR_FLAG
    assert radar[V.PUBLIC_SERVICE] == voters.RADAR_NEUTRAL
    assert set(voters.initial_radar(None).values()) == {voters.RADAR_NEUTRAL}


def test_affinity_adds_twelve_points_per_full_position_on_each_flag():
    radar = voters.initial_radar(MARKET_PARTY)

    # Investidores: Mercado livre +1, Estabilidade +0,5 e Proteção ao poupador +0,5
    assert voters.affinity(G.INVESTORS, radar) == Decimal(44)
    # Assistidos: -0,8 + 0,5 - 0,3 = -0,6 bandeira
    assert voters.affinity(G.WELFARE, radar) == Decimal("12.8")


def test_party_without_flags_starts_at_the_base_affinity_everywhere():
    radar = voters.initial_radar(None)

    assert {voters.affinity(g, radar) for g in G} == {voters.AFFINITY_BASE}


def test_affinity_never_goes_below_zero():
    radar = voters.initial_radar(None) | {
        V.SOCIAL_JUSTICE: Decimal(100),
        V.PUBLIC_SERVICE: Decimal(100),
        V.FREE_MARKET: Decimal(0),
    }

    assert voters.affinity(G.INVESTORS, radar) == 0


def test_campaign_support_grows_with_the_square_root_of_the_spending():
    assert voters.campaign_points(Decimal(8000)).quantize(Decimal("0.1")) == Decimal(
        "1.4"
    )
    assert voters.campaign_points(Decimal(32000)) == 2 * voters.campaign_points(
        Decimal(8000)
    )
    assert voters.campaign_points(Decimal(0)) == 0


def test_support_is_affinity_plus_campaign_and_the_balance_subtracts_rejection():
    radar = voters.initial_radar(MARKET_PARTY)

    standing = voters.standing(G.INVESTORS, radar, Decimal(6), Decimal(10))

    assert standing.support == Decimal(50)
    assert standing.rejection == Decimal(10)
    assert standing.balance == Decimal(40)


def test_support_stops_at_one_hundred():
    radar = voters.initial_radar(MARKET_PARTY)

    assert voters.standing(G.INVESTORS, radar, Decimal(90), Decimal(0)).support == 100


def test_rejection_only_falls_by_repair_and_stays_between_zero_and_one_hundred():
    assert voters.add_rejection(Decimal(95), Decimal(10)) == 100
    assert voters.repair_rejection(Decimal(5), Decimal(10)) == 0
    assert voters.repair_rejection(Decimal(30), Decimal(10)) == 20


def test_the_undecided_enter_each_group_as_a_fixed_balance():
    result = voters.group_vote({1: Decimal(30), 2: Decimal(25)})

    # 15 ÷ (30 + 25 + 15) = 21% indecisos
    assert result.undecided.quantize(Decimal("0.1")) == Decimal("21.4")
    assert result.shares[1].quantize(Decimal("0.1")) == Decimal("42.9")
    assert sum(result.shares.values()) + result.undecided == 100


def test_a_party_rejected_more_than_supported_gets_no_votes_in_the_group():
    result = voters.group_vote({1: Decimal(-10), 2: Decimal(15)})

    assert result.shares[1] == 0
    assert result.shares[2] == Decimal(50)


def test_the_total_vote_weighs_each_group_by_its_size():
    market = {g: voters.Standing(Decimal(30), Decimal(0)) for g in G}
    social = {g: voters.Standing(Decimal(0), Decimal(0)) for g in G}
    market[G.FORMAL_WORKERS] = voters.Standing(Decimal(0), Decimal(0))
    social[G.FORMAL_WORKERS] = voters.Standing(Decimal(85), Decimal(0))

    result = voters.vote({1: market, 2: social})

    workers = result.groups[G.FORMAL_WORKERS]
    assert workers.shares[2] == Decimal(85)
    assert result.total[2] == voters.WEIGHTS[G.FORMAL_WORKERS] * 85
    assert sum(result.total.values()) + result.undecided == 100


def test_runoff_splits_the_eliminated_voters_like_the_finalists_and_undecided():
    first = voters.combine(
        {
            g: voters.GroupVote(
                {1: Decimal(40), 2: Decimal(20), 3: Decimal(20)}, Decimal(20)
            )
            for g in G
        }
    )

    second = voters.restrict(first, [1, 2])

    # Os 20 do partido 3 se dividem 40 : 20 : 20 entre 1, 2 e os indecisos
    assert second.total[1] == Decimal(50)
    assert second.total[2] == Decimal(25)
    assert second.undecided == Decimal(25)
    assert 3 not in second.total


def test_published_poll_stays_inside_the_margin_and_repeats_for_the_same_seed():
    numbers = [
        voters.published(Decimal(30), 5, seed, date(2021, 3, 1), "INVESTORS", 1)
        for seed in range(200)
    ]

    assert all(Decimal(25) <= n <= Decimal(35) for n in numbers)
    assert len(set(numbers)) > 1
    assert numbers[7] == voters.published(
        Decimal(30), 5, 7, date(2021, 3, 1), "INVESTORS", 1
    )


@pytest.mark.parametrize(
    ("kind", "value", "before", "moves"),
    [
        # Cortar o day trade de 20% para 10%: um passo de referência
        (
            MeasureKind.DAY_TRADE_RATE,
            "0.10",
            "0.20",
            {V.FREE_MARKET: 6, V.SOCIAL_JUSTICE: -3},
        ),
        # Subir o day trade é o inverso
        (
            MeasureKind.DAY_TRADE_RATE,
            "0.30",
            "0.20",
            {V.FREE_MARKET: -6, V.SOCIAL_JUSTICE: 3},
        ),
        # Isenção de R$ 20 mil a mais
        (
            MeasureKind.STOCK_EXEMPTION,
            "40000",
            "20000",
            {V.FREE_MARKET: 3, V.SOCIAL_JUSTICE: -3, V.SAVER_PROTECTION: 3},
        ),
        # Taxar um setor em 5% é o inverso de isentá-lo
        (
            MeasureKind.SECTOR_TAX,
            "0.05",
            None,
            {V.FREE_MARKET: -2, V.SOCIAL_JUSTICE: 3, V.DEVELOPMENT: -6},
        ),
        (
            MeasureKind.SECTOR_EXEMPT,
            None,
            None,
            {V.FREE_MARKET: 2, V.SOCIAL_JUSTICE: -3, V.DEVELOPMENT: 6},
        ),
    ],
)
def test_approved_measure_moves_the_profile_by_its_effect(
    kind: MeasureKind, value: str | None, before: str | None, moves: dict
):
    result = voters.radar_moves(
        kind,
        Decimal(value) if value is not None else None,
        Decimal(before) if before is not None else None,
    )

    assert result == {v: Decimal(points) for v, points in moves.items()}
