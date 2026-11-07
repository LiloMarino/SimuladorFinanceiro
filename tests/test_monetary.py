"""A política monetária: calendário do Copom, janela por reunião, defasagem do juro real e credibilidade."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.features.economy.monetary import (
    PRESIDENT_CAP,
    SelicBoard,
    SelicDecision,
    cap_window,
    credibility_premium,
    is_meeting_day,
    lag_weights,
    meeting_days,
    next_credibility,
    next_meeting,
    rate_inflation_points,
    within_cap,
)

TARGET = Decimal("0.0375")
TOLERANCE = Decimal("0.015")


def test_eight_meetings_a_year_on_business_days() -> None:
    days = meeting_days(2021)

    assert len(days) == 8
    assert all(d.weekday() < 5 for d in days)
    assert days[0] == date(2021, 2, 15)
    # O dia 360 (45 vezes 8) de 2021 é 26/12, um domingo: a reunião vai para segunda
    assert days[-1] == date(2021, 12, 27)


def test_next_meeting_crosses_the_year() -> None:
    assert next_meeting(date(2021, 2, 15)) == date(2021, 2, 15)
    assert next_meeting(date(2021, 12, 28)) == meeting_days(2022)[0]
    assert is_meeting_day(date(2021, 2, 15))
    assert not is_meeting_day(date(2021, 2, 16))


def test_the_president_window_is_three_points_each_way() -> None:
    assert Decimal("0.03") == PRESIDENT_CAP
    assert cap_window(Decimal("0.1"), PRESIDENT_CAP) == (
        Decimal("0.07"),
        Decimal("0.13"),
    )
    assert within_cap(Decimal("0.2"), Decimal("0.1"), PRESIDENT_CAP) == Decimal("0.13")
    assert within_cap(Decimal("0"), Decimal("0.1"), PRESIDENT_CAP) == Decimal("0.07")


def test_wanted_rate_stays_within_the_cap_and_the_step() -> None:
    current = Decimal("0.1")
    cap = Decimal("0.0075")

    assert within_cap(Decimal("0.2"), current, cap) == Decimal("0.1075")
    assert within_cap(Decimal("0.05"), current, cap) == Decimal("0.0925")
    assert within_cap(Decimal("0.1012"), current, cap) == Decimal("0.1")
    assert within_cap(Decimal("-0.01"), Decimal("0.0025"), cap) == Decimal(0)


def test_the_window_starts_from_the_effective_rate_off_the_grid() -> None:
    # A efetiva de 23,65% com teto de 0,75 alcança de 23% a 24,25%, nunca 24,50%
    current = Decimal("0.2365")
    cap = Decimal("0.0075")
    assert cap_window(current, cap) == (Decimal("0.23"), Decimal("0.2425"))
    assert within_cap(Decimal("0.30"), current, cap) == Decimal("0.2425")
    assert within_cap(Decimal("0.2365"), current, cap) == Decimal("0.2375")


def test_lag_weights_peak_in_the_middle_quarters() -> None:
    weights = lag_weights(100)

    assert sum(weights) == pytest.approx(1)
    assert weights[3] == weights[6] > weights[0] == weights[9]


def test_low_credibility_moves_the_weight_forward() -> None:
    assert lag_weights(0)[0] > lag_weights(100)[0]
    assert sum(lag_weights(0)) == pytest.approx(1)


def test_a_full_year_one_point_below_adds_three_tenths() -> None:
    gaps = [Decimal("-0.01")] * 12

    assert rate_inflation_points(gaps, 100) == pytest.approx(0.3)


def test_the_newest_month_weighs_as_the_first_lag() -> None:
    gaps = [Decimal(0)] * 11 + [Decimal("-0.01")]

    assert rate_inflation_points(gaps, 100) == pytest.approx(0.3 * 0.05)


def test_higher_real_rate_pulls_inflation_down() -> None:
    assert rate_inflation_points([Decimal("0.02")] * 12, 100) == pytest.approx(-0.6)


def test_no_credibility_doubles_the_effect() -> None:
    gaps = [Decimal("-0.01")] * 12

    assert rate_inflation_points(gaps, 0) == pytest.approx(0.6)


# Meta de 3,75% com tolerância de 1,5: o teto é 5,25%
HISTORY_REAL = Decimal("0.05")


def test_cutting_below_the_history_with_inflation_above_the_band_loses_credibility() -> (
    None
):
    # Juro real de 3,5% contra 5% da história: 1,5 ponto abaixo perde 6
    after = next_credibility(
        100,
        Decimal("0.035"),
        HISTORY_REAL,
        Decimal("0.06"),
        TARGET,
        TOLERANCE,
        raised=False,
    )

    assert after == 94


def test_the_loss_per_meeting_has_a_ceiling() -> None:
    after = next_credibility(
        50,
        Decimal("-0.05"),
        HISTORY_REAL,
        Decimal("0.1"),
        TARGET,
        TOLERANCE,
        raised=False,
    )

    assert after == 30


def test_inflation_inside_the_tolerance_costs_nothing() -> None:
    # 4,31% contra a meta de 3,75% mais 1,5: dentro da faixa, mesmo com o juro real abaixo
    after = next_credibility(
        70,
        Decimal("0.01"),
        HISTORY_REAL,
        Decimal("0.0431"),
        TARGET,
        TOLERANCE,
        raised=False,
    )

    assert after == 70


def test_raising_the_selic_recovers_slowly() -> None:
    after = next_credibility(
        50,
        Decimal("0.01"),
        HISTORY_REAL,
        Decimal("0.1"),
        TARGET,
        TOLERANCE,
        raised=True,
    )

    assert after == 53


def test_matching_or_beating_the_history_rebuilds_credibility() -> None:
    # Sem subir a SELIC, juro real igual ou acima do da história devolve 3, mesmo com a inflação alta
    for real_rate in (HISTORY_REAL, Decimal("0.07")):
        after = next_credibility(
            50,
            real_rate,
            HISTORY_REAL,
            Decimal("0.1"),
            TARGET,
            TOLERANCE,
            raised=False,
        )

        assert after == 53


def test_half_a_step_below_the_history_is_still_the_history() -> None:
    # A SELIC decide em passos de 0,25: 0,125 ponto abaixo é o arredondamento, não desvio
    after = next_credibility(
        50,
        HISTORY_REAL - Decimal("0.00125"),
        HISTORY_REAL,
        Decimal("0.1"),
        TARGET,
        TOLERANCE,
        raised=False,
    )

    assert after == 53


def test_credibility_never_passes_the_full_mark() -> None:
    after = next_credibility(
        99,
        HISTORY_REAL,
        HISTORY_REAL,
        Decimal("0.03"),
        TARGET,
        TOLERANCE,
        raised=False,
    )

    assert after == 100


def test_credibility_premium_is_two_points_at_zero() -> None:
    assert credibility_premium(100) == 0
    assert credibility_premium(0) == Decimal("0.02")
    assert credibility_premium(50) == Decimal("0.01")


def test_board_decisions_hold_from_the_next_day() -> None:
    board = SelicBoard()
    board.record(SelicDecision(date(2021, 2, 15), Decimal("0.03"), 90))

    assert board.selic_on(date(2021, 2, 15)) is None
    assert board.credibility_on(date(2021, 2, 15)) == 100
    assert board.selic_on(date(2021, 2, 16)) == Decimal("0.03")
    assert board.credibility_on(date(2021, 2, 16)) == 90


def ipca_12m_path(gaps: list[Decimal], credibility: float) -> list[float]:
    """
    O IPCA em 12 meses a mais, mês a mês, de um juro real dado: o fechamento do mês n
    vale no mês seguinte, e cada mês soma um doze avos dos pontos ao IPCA mensal.
    """
    monthly = [0.0] + [
        rate_inflation_points(gaps[: n + 1], credibility) / 12
        for n in range(len(gaps) - 1)
    ]
    return [sum(monthly[max(0, m - 11) : m + 1]) for m in range(len(monthly))]


def test_a_year_three_points_below_raises_inflation_the_year_after() -> None:
    gaps = [Decimal("-0.03")] * 12 + [Decimal(0)] * 24

    path = ipca_12m_path(gaps, 100)

    assert path[11] < 0.6
    assert 0.6 <= max(path[12:24]) <= 1.2
    assert path[-1] == pytest.approx(0, abs=1e-9)


def test_low_credibility_raises_inflation_more_and_sooner() -> None:
    gaps = [Decimal("-0.03")] * 12 + [Decimal(0)] * 24

    calm = ipca_12m_path(gaps, 100)
    doubted = ipca_12m_path(gaps, 0)

    assert max(doubted) > max(calm)
    assert doubted.index(max(doubted)) < calm.index(max(calm))
