"""Contas puras das estatais: pontos de IPCA, teto, represa, payout e valor justo."""

from __future__ import annotations

from decimal import Decimal

import pytest

from backend.core.enum import DividendPolicy, StateControl, StateLever
from backend.features.state_companies import fair_value, levers, payout

D = Decimal


@pytest.mark.parametrize(
    ("lever", "control", "expected"),
    [
        (StateLever.FUEL, StateControl.P20, D("1.0")),
        (StateLever.FUEL, StateControl.P5, D("0.25")),
        (StateLever.ENERGY, StateControl.P20, D("0.8")),
        (StateLever.ENERGY, StateControl.P10, D("0.4")),
        (StateLever.BANK, StateControl.P20, D("0")),
        (StateLever.FUEL, StateControl.NONE, D("0")),
    ],
)
def test_held_points_are_percent_times_lever_weight(
    lever: StateLever, control: StateControl, expected: Decimal
) -> None:
    assert levers.held_points(lever, control) == expected


def test_bank_never_holds_ipca_points() -> None:
    assert all(
        levers.held_points(StateLever.BANK, control) == 0 for control in StateControl
    )


def test_total_sums_the_orders_of_every_company() -> None:
    orders = [
        (StateLever.FUEL, StateControl.P15),
        (StateLever.ENERGY, StateControl.P10),
        (StateLever.BANK, StateControl.P20),
    ]
    assert levers.total_held_points(orders) == D("0.75") + D("0.4")


def test_steps_over_the_cap_are_blocked_with_a_reason() -> None:
    steps = {s.control: s for s in levers.step_availability(StateLever.FUEL, D("0.8"))}

    # Com 0,8 em uso cabem até 0,7 ponto: P10 segura 0,5 e P15 segura 0,75
    assert not steps[StateControl.P10].blocked
    assert steps[StateControl.P15].blocked
    assert steps[StateControl.P20].blocked
    assert "teto" in (steps[StateControl.P20].blocked_reason or "")
    assert steps[StateControl.NONE].blocked_reason is None


def test_step_exactly_at_the_cap_is_allowed() -> None:
    steps = {s.control: s for s in levers.step_availability(StateLever.FUEL, D("0.5"))}

    assert steps[StateControl.P20].points + D("0.5") == levers.IPCA_CAP_POINTS
    assert not steps[StateControl.P20].blocked


def test_bank_is_never_blocked_by_the_cap() -> None:
    steps = levers.step_availability(StateLever.BANK, levers.IPCA_CAP_POINTS)

    assert not any(step.blocked for step in steps)


def test_release_returns_the_whole_backlog_at_once() -> None:
    held = [D("1.0"), D("1.0"), D("0.5"), D("0"), D("0")]

    path = levers.inflation_path(held)

    assert path == [D("-1.0"), D("-1.0"), D("-0.5"), D("2.5"), D("0")]
    # Segurar e soltar fecha em zero: a inflação volta inteira
    assert sum(path) == 0


def test_partial_relief_keeps_the_backlog_until_control_is_lifted() -> None:
    held = [D("1.0"), D("0.5"), D("0")]

    assert levers.backlog_points(held[:2]) == D("1.5") / 12
    assert levers.backlog_points(held) == 0
    assert levers.inflation_path(held)[-1] == D("1.5")


def test_holding_1_4_points_for_a_year_leaves_1_4_points_of_price_level() -> None:
    held = [D("1.4")] * 12

    # A represa mostra o nível de preços; o IPCA do mês da soltura soma os 12 meses
    assert levers.backlog_points(held) == D("1.4")
    assert levers.inflation_path([*held, D("0")])[-1] == D("16.8")


def test_without_orders_the_path_is_flat() -> None:
    assert levers.inflation_path([D("0")] * 4) == [D("0")] * 4
    assert levers.backlog_points([D("0")] * 4) == 0


def test_a_new_control_after_release_starts_a_fresh_backlog() -> None:
    held = [D("1.0"), D("0"), D("0.4"), D("0.4"), D("0")]

    assert levers.inflation_path(held) == [
        D("-1.0"),
        D("1.0"),
        D("-0.4"),
        D("-0.4"),
        D("0.8"),
    ]


@pytest.mark.parametrize(
    ("policy", "ratio"),
    [
        (DividendPolicy.REINVEST, D("0.25")),
        (DividendPolicy.NORMAL, D("0.50")),
        (DividendPolicy.SQUEEZE, D("0.80")),
    ],
)
def test_payout_ratio_by_policy(policy: DividendPolicy, ratio: Decimal) -> None:
    assert payout.payout_ratio(policy) == ratio


def test_control_cuts_the_profit_in_proportion_to_the_step() -> None:
    cuts = [payout.profit_cut(control) for control in StateControl]

    assert cuts[0] == 0
    assert cuts == sorted(cuts)
    assert payout.profit_after_control(D("100"), StateControl.P20) == D("70")


def test_dividend_of_a_founded_company_is_payout_over_the_remaining_profit() -> None:
    assert payout.dividend(D("100"), DividendPolicy.NORMAL, StateControl.NONE) == D(
        "50"
    )
    assert payout.dividend(D("100"), DividendPolicy.SQUEEZE, StateControl.P20) == D(
        "56"
    )


def test_dividend_factor_is_one_for_normal_without_control() -> None:
    assert payout.dividend_factor(DividendPolicy.NORMAL, StateControl.NONE) == 1


def test_dividend_factor_scales_history_by_policy_and_control() -> None:
    squeeze = payout.dividend_factor(DividendPolicy.SQUEEZE, StateControl.NONE)
    reinvest = payout.dividend_factor(DividendPolicy.REINVEST, StateControl.NONE)

    assert squeeze == D("1.6")
    assert reinvest == D("0.5")
    assert payout.dividend_factor(DividendPolicy.NORMAL, StateControl.P20) == D("0.7")


def test_mean_return_stays_below_the_historical_real_interest() -> None:
    for real_interest in (D("0.06"), D("0.0"), D("-0.02")):
        assert fair_value.mean_annual_return(real_interest) < real_interest


def test_annual_return_is_deterministic_by_seed_and_year() -> None:
    mean = D("0.05")

    assert fair_value.annual_return(7, 0, mean) == fair_value.annual_return(7, 0, mean)
    assert fair_value.annual_return(7, 0, mean) != fair_value.annual_return(7, 1, mean)
    assert fair_value.annual_return(7, 0, mean) != fair_value.annual_return(8, 0, mean)


def test_annual_return_stays_inside_its_limits() -> None:
    draws = [fair_value.annual_return(seed, 0, D("0.05")) for seed in range(200)]

    assert min(draws) >= fair_value.MIN_ANNUAL_RETURN
    assert max(draws) <= fair_value.MAX_ANNUAL_RETURN


def test_annual_returns_center_on_the_mean() -> None:
    draws = [fair_value.annual_return(seed, 0, D("0.05")) for seed in range(2000)]

    assert sum(draws) / len(draws) == pytest.approx(0.05, abs=0.01)


def test_fair_value_starts_at_the_invested_amount() -> None:
    assert fair_value.fair_value(D("1000"), 3, D("0.05"), 0) == D("1000")


def test_fair_value_after_a_year_applies_that_years_return() -> None:
    mean = D("0.05")
    expected = 1000 * (1 + fair_value.annual_return(3, 0, mean))

    value = fair_value.fair_value(D("1000"), 3, mean, 12)

    assert float(value) == pytest.approx(expected, rel=1e-9)


def test_fair_value_replays_the_same_for_the_same_seed() -> None:
    first = fair_value.fair_value(D("1000"), 3, D("0.05"), 30)

    assert first == fair_value.fair_value(D("1000"), 3, D("0.05"), 30)
    assert first != fair_value.fair_value(D("1000"), 4, D("0.05"), 30)
