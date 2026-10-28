"""Regras das ações de campanha: faixas do d20, ganho de cada ação, retorno decrescente e queda do apoio."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core.enum import CampaignActionKind as K
from backend.core.enum import DiceBand as B
from backend.features.government import campaign

ZERO = Decimal(0)
NO_REPAIR = (ZERO, ZERO)


@pytest.mark.parametrize("kind", list(K))
def test_band_chances_add_up_to_one(kind: K):
    bands = campaign.table(kind, 0, campaign.EVENT_REPAIR_LIMIT, Decimal(10))

    assert sum(b.chance for b in bands) == 1
    assert [(b.first_roll, b.last_roll) for b in bands] == [
        (1, 1),
        (2, 6),
        (7, 14),
        (15, 19),
        (20, 20),
    ]


def test_a_single_die_gives_five_forty_and_twenty_five_percent_bands():
    bands = {b.band: b.chance for b in campaign.table(K.EVENT, 0, ZERO, ZERO)}

    assert bands == {
        B.DISASTER: Decimal("0.05"),
        B.WEAK: Decimal("0.25"),
        B.NORMAL: Decimal("0.4"),
        B.GOOD: Decimal("0.25"),
        B.VIRAL: Decimal("0.05"),
    }


def test_tv_rolls_two_dice_and_keeps_the_higher():
    bands = {b.band: b.chance for b in campaign.table(K.TV, 0, ZERO, ZERO)}

    # O desastre só sai com dois 1: 1 em 400
    assert bands[B.DISASTER] == Decimal(1) / 400
    assert bands[B.VIRAL] == Decimal(39) / 400
    assert campaign.chosen_roll(K.TV, (6, 16)) == 16
    assert campaign.chosen_roll(K.EVENT, (6,)) == 6


def test_event_gain_follows_the_band_multipliers():
    gain = campaign.NORMAL_GAIN[K.EVENT]
    by_band = {b.band: b.support for b in campaign.table(K.EVENT, 0, ZERO, ZERO)}

    assert by_band == {
        B.DISASTER: -2 * gain,
        B.WEAK: gain / 2,
        B.NORMAL: gain,
        B.GOOD: gain * Decimal("1.5"),
        B.VIRAL: gain * 3,
    }


def test_rally_doubles_only_the_extremes():
    gain = campaign.NORMAL_GAIN[K.RALLY]
    by_band = {b.band: b.support for b in campaign.table(K.RALLY, 0, ZERO, ZERO)}

    assert by_band[B.DISASTER] == -4 * gain
    assert by_band[B.VIRAL] == 6 * gain
    assert by_band[B.NORMAL] == gain
    assert by_band[B.WEAK] == gain / 2


def test_attack_takes_from_the_rival_and_a_disaster_backfires_as_rejection():
    gain = campaign.NORMAL_GAIN[K.ATTACK]
    bands = {b.band: b for b in campaign.table(K.ATTACK, 0, ZERO, ZERO)}

    assert bands[B.NORMAL].support == -gain
    assert bands[B.VIRAL].support == -3 * gain
    assert bands[B.DISASTER].support == 0
    # O tiro sai pela culatra: o grupo passa a rejeitar quem atacou, em 2 vezes o ganho
    assert bands[B.DISASTER].rejection == 2 * gain


def test_event_repairs_rejection_except_on_a_disaster():
    bands = {
        b.band: b.rejection
        for b in campaign.table(K.EVENT, 0, campaign.EVENT_REPAIR_LIMIT, Decimal(10))
    }

    assert bands[B.DISASTER] == 0
    assert all(
        bands[band] == -campaign.EVENT_REPAIR
        for band in (B.WEAK, B.NORMAL, B.GOOD, B.VIRAL)
    )


def test_event_repair_stops_at_the_campaign_limit_and_at_zero_rejection():
    at_limit = campaign.outcome(K.EVENT, (10,), 0, ZERO, Decimal(10))
    no_rejection = campaign.outcome(K.EVENT, (10,), 0, Decimal(6), ZERO)
    half_point = campaign.outcome(K.EVENT, (10,), 0, Decimal(6), Decimal("0.4"))

    assert at_limit.rejection == 0
    assert no_rejection.rejection == 0
    assert half_point.rejection == Decimal("-0.4")
    # Sem reparar, o apoio rende igual
    assert at_limit.support == campaign.NORMAL_GAIN[K.EVENT]


def test_repeating_the_same_action_halves_the_return_each_time():
    first = campaign.outcome(K.EVENT, (10,), 0, ZERO, ZERO)
    second = campaign.outcome(K.EVENT, (10,), 1, ZERO, ZERO)
    third = campaign.outcome(K.EVENT, (10,), 2, ZERO, ZERO)

    assert second.support == first.support / 2
    assert third.support == first.support / 4
    assert [first.rate, second.rate, third.rate] == [1, Decimal("0.5"), Decimal("0.25")]


def test_the_dice_come_from_the_game_seed_and_are_stable():
    first = campaign.roll_dice(7, 3, K.EVENT)

    assert first == campaign.roll_dice(7, 3, K.EVENT)
    assert len(first) == 1
    assert len(campaign.roll_dice(7, 3, K.TV)) == 2
    assert all(1 <= roll <= 20 for roll in campaign.roll_dice(7, 4, K.TV))
    # Trocar só a semente muda os dados
    assert any(campaign.roll_dice(seed, 3, K.EVENT) != first for seed in range(8, 20))


def test_support_halves_in_three_months():
    assert campaign.decay_factor(0) == 1
    assert campaign.decay_factor(91) == pytest.approx(Decimal("0.5"))
    assert campaign.decay_factor(182) == pytest.approx(Decimal("0.25"))
    assert campaign.decay_factor(1) > campaign.decay_factor(2)


def test_prices_stay_fixed_without_inflation_adjustment():
    price = campaign.price(K.TV, date(2020, 1, 1), date(2024, 5, 1), False)

    assert price == campaign.PRICES[K.TV]
