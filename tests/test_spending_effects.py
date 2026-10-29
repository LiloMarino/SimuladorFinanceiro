"""Efeito das medidas de gasto na economia: forma no tempo, soma, SELIC, bolsa, beta e leitura das séries."""

from __future__ import annotations

import math
from datetime import date, timedelta
from decimal import Decimal

import pytest

from backend.core.enum import EffectPhase, IndicatorSeries, MeasureKind, MeasureStatus
from backend.core.indicators import annualize_daily
from backend.core.repository.economic import IndicatorHistory
from backend.features.government import spending
from backend.features.government import spending_effects as fx
from backend.features.government.spending import SpendingTimeline
from backend.features.government.state import Measure
from tests.fakes import daily_series, monthly_series

AUX = MeasureKind.WELFARE_SPENDING
SERVANTS = MeasureKind.SERVANT_RAISE
WORKS = MeasureKind.PUBLIC_WORKS
START = date(2020, 1, 1)
EFFECTIVE = date(2021, 1, 4)


def measure(
    kind: MeasureKind,
    value: str,
    before: str,
    *,
    id: int = 1,
    effective: date | None = EFFECTIVE,
    status: MeasureStatus = MeasureStatus.APPROVED,
) -> Measure:
    return Measure(
        id=id,
        kind=kind,
        value=Decimal(value),
        before=Decimal(before),
        sector=None,
        segment=None,
        proposer_id=1,
        term_start=START,
        proposed=START,
        status=status,
        effective=effective,
    )


def after_months(months: float, start: date = EFFECTIVE) -> date:
    return start + timedelta(days=round(fx.DAYS_PER_MONTH * months))


def one_step_up(kind: MeasureKind = AUX) -> fx.Effect:
    value = spending.DEFAULTS[kind] + spending.STEPS[kind]
    return fx.effects_of([measure(kind, str(value), str(spending.DEFAULTS[kind]))])[0]


# A forma do efeito


def test_shape_rises_in_a_line_then_halves_every_year():
    assert fx.shape(-1) == 0
    assert fx.shape(3) == pytest.approx(0.5)
    assert fx.shape(6) == pytest.approx(1)
    assert fx.shape(18) == pytest.approx(0.5)
    assert fx.shape(30) == pytest.approx(0.25, rel=5e-3)


def test_only_approved_spending_measures_make_an_effect():
    measures = [
        measure(AUX, "0.02", "0.015", id=1),
        measure(
            AUX, "0.025", "0.02", id=2, status=MeasureStatus.QUEUED, effective=None
        ),
        measure(
            AUX, "0.025", "0.02", id=3, status=MeasureStatus.REJECTED, effective=None
        ),
        measure(MeasureKind.STOCK_PROFIT_RATE, "0.2", "0.15", id=4),
    ]

    assert [e.measure_id for e in fx.effects_of(measures)] == [1]


def test_a_step_adds_the_points_of_its_measure_when_the_effect_is_full():
    full = after_months(6)

    assert fx.inflation_points([one_step_up(AUX)], full) == pytest.approx(
        0.25, rel=5e-3
    )
    assert fx.inflation_points([one_step_up(SERVANTS)], full) == pytest.approx(
        0.20, rel=5e-3
    )
    assert fx.inflation_points([one_step_up(WORKS)], full) == pytest.approx(
        0.15, rel=5e-3
    )


def test_the_effect_starts_when_the_measure_takes_force_and_not_before():
    effect = one_step_up()

    assert fx.inflation_points([effect], EFFECTIVE - timedelta(days=30)) == 0
    assert fx.inflation_points([effect], EFFECTIVE) == 0
    assert fx.inflation_points([effect], after_months(3)) == pytest.approx(
        0.125, rel=5e-3
    )


def test_a_cut_flips_the_sign_with_the_same_delay_and_fall():
    cut = fx.effects_of([measure(AUX, "0.01", "0.015")])
    raise_ = fx.effects_of([measure(AUX, "0.02", "0.015")])

    for months in (3, 6, 18, 30):
        day = after_months(months)
        assert fx.inflation_points(cut, day) == pytest.approx(
            -fx.inflation_points(raise_, day)
        )


def test_two_measures_add_up():
    both = fx.effects_of(
        [
            measure(AUX, "0.02", "0.015", id=1),
            measure(SERVANTS, "0.03", "0", id=2),
        ]
    )

    assert fx.inflation_points(both, after_months(6)) == pytest.approx(
        0.25 + 0.20, rel=5e-3
    )


def test_works_also_add_to_growth_and_the_others_do_not():
    full = after_months(6)

    assert fx.growth_points([one_step_up(WORKS)], full) == pytest.approx(0.6, rel=5e-3)
    assert fx.growth_points([one_step_up(AUX)], full) == 0


def test_the_phase_goes_from_waiting_to_faded():
    effect = one_step_up()

    assert fx.phase_of(effect, EFFECTIVE - timedelta(days=1)) is EffectPhase.WAITING
    assert fx.phase_of(effect, after_months(3)) is EffectPhase.RISING
    assert fx.phase_of(effect, after_months(10)) is EffectPhase.FALLING
    assert fx.phase_of(effect, after_months(70)) is EffectPhase.FADED
    assert fx.faded_on(effect) < after_months(70)
    assert fx.peak_on(effect) == after_months(6)


# A reação da SELIC e da bolsa


def test_selic_reacts_one_and_a_half_times_the_inflation():
    effect = one_step_up()
    day = after_months(6)

    assert fx.selic_points([effect], day) == pytest.approx(
        1.5 * fx.inflation_points([effect], day)
    )


def test_stocks_fall_2_9_percent_per_selic_point_averaged_over_the_quarter():
    effect = fx.Effect(1, AUX, EFFECTIVE, steps=2.0)
    day = after_months(12)
    moves = [
        fx.selic_points([effect], day - timedelta(days=round(fx.DAYS_PER_MONTH * back)))
        for back in range(3)
    ]

    assert fx.stocks_level([effect], day) == pytest.approx(
        math.exp(-0.029 * sum(moves) / 3)
    )
    assert fx.stocks_level([effect], day) < 1


def test_a_cut_lifts_the_stocks():
    cut = fx.effects_of([measure(AUX, "0.01", "0.015")])

    assert fx.stocks_level(cut, after_months(12)) > 1


def test_stocks_do_not_move_without_effects():
    assert fx.stocks_level([], after_months(12)) == 1


def test_the_preview_peak_of_the_stocks_is_the_deepest_point():
    peak = fx.peak_stocks(AUX, 2.0)

    assert peak < 0
    assert peak == pytest.approx(min(fx.peak_stocks(AUX, 2.0), peak))
    assert fx.peak_stocks(AUX, -2.0) > 0


# O beta de cada ativo


def returns(
    factor: float, days: int = 120
) -> tuple[dict[date, float], dict[date, float]]:
    market = {START + timedelta(days=i): math.sin(i / 3) / 100 for i in range(days)}
    return {d: factor * r for d, r in market.items()}, market


def test_beta_is_how_much_the_asset_moves_per_point_of_the_market():
    asset, market = returns(2.0)

    assert fx.beta_of(asset, market) == pytest.approx(2.0)


def test_beta_is_limited_between_zero_and_three():
    assert fx.beta_of(*returns(5.0)) == fx.MAX_BETA
    assert fx.beta_of(*returns(-1.0)) == 0


def test_beta_is_one_when_there_are_too_few_common_days():
    assert fx.beta_of(*returns(2.0, days=fx.MIN_BETA_DAYS - 1)) == 1


# A linha do tempo do gasto


def test_the_timeline_starts_at_the_defaults_and_follows_each_measure():
    timeline = SpendingTimeline(
        [
            measure(AUX, "0.02", "0.015", id=1, effective=date(2021, 3, 1)),
            measure(AUX, "0.01", "0.02", id=2, effective=date(2021, 9, 1)),
        ]
    )

    assert timeline.value_on(AUX, date(2021, 2, 28)) == spending.DEFAULTS[AUX]
    assert timeline.value_on(AUX, date(2021, 3, 1)) == Decimal("0.02")
    assert timeline.value_on(AUX, date(2021, 9, 1)) == Decimal("0.01")
    assert timeline.latest(AUX) == Decimal("0.01")
    assert timeline.since(AUX, date(2021, 5, 1)) == date(2021, 3, 1)
    assert timeline.since(AUX, date(2021, 2, 1)) is None


def test_the_total_spending_is_the_base_plus_what_the_measures_moved():
    timeline = SpendingTimeline(
        [measure(AUX, "0.02", "0.015", effective=date(2021, 3, 1))]
    )

    assert timeline.spending_on(date(2021, 2, 1)) == spending.BASE_SPENDING
    assert timeline.spending_on(date(2021, 3, 1)) == spending.BASE_SPENDING + Decimal(
        "0.005"
    )


def test_the_raise_compounds_on_each_january_after_it_takes_force():
    timeline = SpendingTimeline(
        [measure(SERVANTS, "0.03", "0", effective=date(2021, 3, 1))]
    )
    base = spending.RAISE_BASES[SERVANTS]

    # O reajuste vale no 1º de janeiro seguinte à vigência, e a cada janeiro a mais
    assert timeline.multiplier(SERVANTS, date(2021, 12, 31)) == 1
    assert timeline.multiplier(SERVANTS, date(2022, 1, 1)) == Decimal("1.03")
    assert timeline.multiplier(SERVANTS, date(2023, 1, 1)) == Decimal("1.03") ** 2
    assert timeline.cost_on(SERVANTS, date(2022, 1, 1)) == base * Decimal("1.03")
    assert timeline.spending_on(
        date(2022, 6, 1)
    ) == spending.BASE_SPENDING + base * Decimal("0.03")


def test_a_raise_at_zero_keeps_the_cost_in_share_of_gdp():
    timeline = SpendingTimeline([])

    assert timeline.multiplier(SERVANTS, date(2030, 1, 1)) == 1
    assert timeline.spending_on(date(2030, 1, 1)) == spending.BASE_SPENDING


def test_the_rest_of_the_spending_is_what_no_measure_touches():
    spent = sum(spending.DEFAULT_COSTS.values())
    assert Decimal("0.19") - spent == spending.REST_SPENDING
    assert spending.REST_SPENDING > 0


def test_the_cost_of_a_step_in_the_first_year():
    assert spending.cost_change(AUX, Decimal("0.02"), Decimal("0.015")) == Decimal(
        "0.005"
    )
    assert spending.cost_change(SERVANTS, Decimal("0.03"), Decimal(0)) == Decimal(
        "0.00099"
    )
    assert spending.cost_change(AUX, Decimal("0.01"), Decimal("0.015")) < 0


def test_a_hypothetical_timeline_does_not_change_the_real_one():
    timeline = SpendingTimeline([])
    draft = measure(AUX, "0.02", "0.015", effective=None, status=MeasureStatus.QUEUED)

    hypothetical = timeline.with_measure(draft, date(2022, 5, 1))

    assert hypothetical.value_on(AUX, date(2022, 5, 1)) == Decimal("0.02")
    assert timeline.value_on(AUX, date(2022, 5, 1)) == spending.DEFAULTS[AUX]


# A leitura das séries


@pytest.fixture
def economy(indicators):
    indicators(IndicatorSeries.IPCA, monthly_series(START, 80, "0.30"))
    indicators(IndicatorSeries.SELIC, daily_series(START, date(2026, 12, 31), "0.05"))
    indicators(IndicatorSeries.CDI, daily_series(START, date(2026, 12, 31), "0.05"))
    indicators(IndicatorSeries.IBOV, daily_series(START, date(2026, 12, 31), "100000"))
    result = fx.SpendingEconomy(1, START)
    result.update([measure(AUX, "0.02", "0.015")])
    return result


def history_of(series: IndicatorSeries) -> IndicatorHistory:
    values = {
        IndicatorSeries.IPCA: monthly_series(START, 80, "0.30"),
        IndicatorSeries.SELIC: daily_series(START, date(2026, 12, 31), "0.05"),
        IndicatorSeries.CDI: daily_series(START, date(2026, 12, 31), "0.05"),
        IndicatorSeries.IBOV: daily_series(START, date(2026, 12, 31), "100000"),
    }[series]
    return IndicatorHistory(sorted(values), values)


def test_the_ipca_gets_the_monthly_share_of_the_points_and_the_past_stays(economy):
    history = history_of(IndicatorSeries.IPCA)
    adjusted = economy.adjust(IndicatorSeries.IPCA, history)
    full = date(2021, 8, 1)

    assert adjusted.values[date(2020, 6, 1)] == Decimal("0.30")
    assert adjusted.values[date(2021, 1, 1)] == Decimal("0.30")
    assert adjusted.values[full] == Decimal("0.30") + Decimal(
        str(round(economy.inflation_points(full) / 12, 6))
    )
    assert adjusted.values[full] > Decimal("0.30")
    # A série guardada não é tocada
    assert history.values[full] == Decimal("0.30")


def test_selic_and_cdi_rise_together_by_the_reaction_of_the_central_bank(economy):
    day = date(2021, 8, 2)
    base = annualize_daily(Decimal("0.05"))

    for series in (IndicatorSeries.SELIC, IndicatorSeries.CDI):
        adjusted = economy.adjust(series, history_of(series))
        assert adjusted.values[day] > Decimal("0.05")
        assert annualize_daily(adjusted.values[day]) == pytest.approx(
            base + Decimal(str(economy.selic_points(day) / 100)), abs=Decimal("0.0001")
        )
        assert adjusted.values[date(2020, 6, 1)] == Decimal("0.05")


def test_the_ibovespa_is_scaled_by_the_level_of_the_stocks(economy):
    day = date(2021, 8, 2)
    adjusted = economy.adjust(IndicatorSeries.IBOV, history_of(IndicatorSeries.IBOV))

    assert float(adjusted.values[day]) == pytest.approx(
        100000 * economy.level(day), abs=0.01
    )
    assert adjusted.values[day] < Decimal("100000")


def test_without_measures_the_series_come_back_untouched():
    nothing = fx.SpendingEconomy(1, START)
    history = history_of(IndicatorSeries.SELIC)

    assert nothing.adjust(IndicatorSeries.SELIC, history) is history
    assert nothing.stock_factor("AAA", date(2021, 8, 2)) == 1.0


def test_a_stock_follows_the_market_level_raised_to_its_beta(economy, monkeypatch):
    day = date(2021, 8, 2)
    monkeypatch.setattr(economy, "_betas", {"HIGH": 2.0, "LOW": 0.5})

    level = economy.level(day)
    assert economy.stock_factor("HIGH", day) == pytest.approx(level**2)
    assert economy.stock_factor("LOW", day) == pytest.approx(level**0.5)
    # Sem beta medido, o ativo anda como o mercado
    assert economy.stock_factor("NEW", day) == pytest.approx(level)
    assert economy.stock_factor("HIGH", day) < economy.stock_factor("LOW", day)
