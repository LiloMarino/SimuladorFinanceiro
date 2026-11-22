"""Gerador de séries sintéticas sobre um histórico pequeno montado no teste."""

from datetime import date
from typing import cast

import numpy as np
import pandas as pd
import pytest

from backend.core.copom import meeting_days, next_meeting
from backend.core.enum import IndicatorSeries
from backend.core.utils import is_business_day, next_business_day
from backend.features.import_data import synthetic
from backend.features.import_data.synthetic import (
    AssetHistory,
    MarketHistory,
    SeriesGenerator,
)

LAST_REAL = date(2004, 12, 31)
UNTIL = date(2006, 12, 29)
IVG_R_FIRST_MONTH = date(2001, 4, 1)
FOLLOWERS = (IndicatorSeries.IVG_R, IndicatorSeries.IGP_M, IndicatorSeries.TR)


def business_days(start: date, end: date) -> list[date]:
    days = [start if is_business_day(start) else next_business_day(start)]
    while (day := next_business_day(days[-1])) <= end:
        days.append(day)
    return days


def bars_from(
    days: list[date], returns: np.ndarray, start_price: float
) -> pd.DataFrame:
    close = start_price * np.exp(np.cumsum(returns))
    return pd.DataFrame(
        {
            "open": close * 0.995,
            "high": close * 1.01,
            "low": close * 0.985,
            "close": close,
            "volume": np.full(len(days), 1_000_000),
        },
        index=days,
    )


def build_history() -> MarketHistory:
    """
    Ibovespa com trimestres calmos, normais e agitados; dois bancos que seguem o
    mercado, um terceiro que abriu capital em 2003 e anda colado no primeiro, e
    uma elétrica que parou de negociar em junho de 2004.
    """
    rng = np.random.default_rng(42)
    days = business_days(synthetic.POOL_START, LAST_REAL)
    vol = np.repeat(rng.choice([0.004, 0.012, 0.035], size=len(days) // 60 + 1), 60)
    # SELIC sobe e desce em ondas, e o mercado cai quando ela sobe, como no real
    selic_annual = 0.12 + 0.06 * np.sin(np.arange(len(days)) / 200)
    market = rng.standard_normal(len(days)) * vol[: len(days)]
    market -= 5 * np.diff(selic_annual, prepend=selic_annual[0])
    bank_a = 1.1 * market + rng.standard_normal(len(days)) * 0.008
    bank_b = 0.9 * market + rng.standard_normal(len(days)) * 0.008
    bank_c = bank_a + rng.standard_normal(len(days)) * 0.004
    power = 0.5 * market + rng.standard_normal(len(days)) * 0.01

    young_from = days.index(next_business_day(date(2002, 12, 31)))
    power_until = days.index(date(2004, 6, 30)) + 1
    assets = {
        "BANK_A": AssetHistory(bars_from(days, bank_a, 20), "Bancos", "Financeiro"),
        "BANK_B": AssetHistory(bars_from(days, bank_b, 30), "Bancos", "Financeiro"),
        "BANK_C": AssetHistory(
            bars_from(days[young_from:], bank_c[young_from:], 10),
            "Bancos",
            "Financeiro",
        ),
        "POWER": AssetHistory(
            bars_from(days[:power_until], power[:power_until], 15),
            "Elétricas",
            "Utilidade Pública",
        ),
    }

    # O CDI anda um pouco abaixo da SELIC
    selic = ((1 + selic_annual) ** (1 / 252) - 1) * 100
    cdi = ((1 + selic_annual - 0.001) ** (1 / 252) - 1) * 100
    months = pd.date_range(synthetic.POOL_START, LAST_REAL, freq="MS")
    ipca = np.round(rng.uniform(0.1, 1.2, len(months)), 2)
    # IGP-M e TR trazem um valor único por mês, que diz de que mês histórico o futuro
    # gerado saiu; o IVG-R só existe desde abril de 2001
    igp_m = np.round(0.01 * np.arange(1, len(months) + 1), 2)
    tr = np.round(0.0001 * np.arange(1, len(months) + 1), 4)
    ivg_r_months = [m.date() for m in months if m.date() >= IVG_R_FIRST_MONTH]
    ivg_r = np.round(rng.uniform(0.0, 0.9, len(ivg_r_months)), 6)
    indicators = {
        IndicatorSeries.IBOV: pd.Series(10_000 * np.exp(np.cumsum(market)), index=days),
        IndicatorSeries.SELIC: pd.Series(selic, index=days),
        IndicatorSeries.CDI: pd.Series(cdi, index=days),
        IndicatorSeries.IPCA: pd.Series(ipca, index=[m.date() for m in months]),
        IndicatorSeries.IGP_M: pd.Series(igp_m, index=[m.date() for m in months]),
        IndicatorSeries.TR: pd.Series(tr, index=[m.date() for m in months]),
        IndicatorSeries.IVG_R: pd.Series(ivg_r, index=ivg_r_months),
        # Fed Funds em % ao ano, parado em 6%
        IndicatorSeries.FED_FUNDS: pd.Series(np.full(len(days), 6.0), index=days),
    }
    return MarketHistory(assets, indicators)


@pytest.fixture(scope="module")
def history() -> MarketHistory:
    return build_history()


@pytest.fixture(scope="module")
def generator(history: MarketHistory) -> SeriesGenerator:
    return SeriesGenerator(history)


def log_returns(values: pd.Series | pd.DataFrame) -> np.ndarray:
    """Variação diária de uma coluna (o pandas tipa `df["close"]` como as duas)."""
    return np.diff(np.log(np.asarray(values, dtype=float).ravel()))


def test_same_seed_repeats_and_other_seed_differs(generator):
    first = generator.generate(UNTIL, seed=7)
    again = SeriesGenerator(build_history()).generate(UNTIL, seed=7)
    other = generator.generate(UNTIL, seed=8)

    for ticker, bars in first.assets.items():
        pd.testing.assert_frame_equal(bars, again.assets[ticker])
    for series, values in first.indicators.items():
        pd.testing.assert_series_equal(values, again.indicators[series])
    assert not first.assets["BANK_A"].equals(other.assets["BANK_A"])


def test_each_series_starts_after_its_own_last_real_day(generator, history):
    generated = generator.generate(UNTIL, seed=1)

    for ticker, bars in generated.assets.items():
        last_real = history.assets[ticker].bars.index[-1]
        assert bars.index[0] == next_business_day(last_real)
        assert all(is_business_day(day) for day in bars.index)
        assert bars.index[-1] <= UNTIL
    assert generated.assets["POWER"].index[0] == date(2004, 7, 1)
    assert generated.assets["BANK_A"].index[0] == date(2005, 1, 3)


def test_subset_matches_the_full_generation(generator):
    full = generator.generate(UNTIL, seed=3, temperature=1.7)
    alone = generator.generate(UNTIL, seed=3, temperature=1.7, tickers=["BANK_C"])

    assert list(alone.assets) == ["BANK_C"]
    pd.testing.assert_frame_equal(alone.assets["BANK_C"], full.assets["BANK_C"])


def test_prices_continue_from_the_last_close_with_coherent_bars(generator, history):
    generated = generator.generate(UNTIL, seed=5)

    for ticker, bars in generated.assets.items():
        last_close = history.assets[ticker].bars["close"].iloc[-1]
        assert abs(bars["close"].iloc[0] / last_close - 1) < 0.2
        assert (bars["low"] <= bars[["open", "close"]].min(axis=1)).all()
        assert (bars["high"] >= bars[["open", "close"]].max(axis=1)).all()
        assert (bars["volume"] >= 0).all()


def test_selic_stays_within_history_and_cdi_keeps_the_spread(generator, history):
    selic_real = synthetic.to_annual(
        history.indicators[IndicatorSeries.SELIC].to_numpy()
    )
    last_spread = (
        selic_real[-1]
        - synthetic.to_annual(history.indicators[IndicatorSeries.CDI].to_numpy())[-1]
    )

    for seed in range(20):
        generated = generator.generate(UNTIL, seed=seed)
        selic = synthetic.to_annual(
            generated.indicators[IndicatorSeries.SELIC].to_numpy()
        )
        cdi = synthetic.to_annual(generated.indicators[IndicatorSeries.CDI].to_numpy())
        assert selic.min() >= selic_real.min() - 1e-6
        assert selic.max() <= selic_real.max() + 1e-6
        np.testing.assert_allclose(selic - cdi, last_spread, atol=1e-4)


def test_fed_funds_halves_the_distance_to_three_percent_every_two_years(generator):
    fed = generator.generate(date(2008, 12, 31), seed=2).indicators[
        IndicatorSeries.FED_FUNDS
    ]

    # De 6% para 3%: a distância é 3 pontos e cai à metade a cada 2 anos
    two_years = fed.loc[date(2006, 12, 31) :]
    assert fed.iloc[0] == pytest.approx(6.0, abs=0.01)
    assert two_years.iloc[0] == pytest.approx(4.5, abs=0.02)
    assert fed.is_monotonic_decreasing


def test_fed_funds_future_does_not_depend_on_the_seed(generator):
    one = generator.generate(UNTIL, seed=1).indicators[IndicatorSeries.FED_FUNDS]
    other = generator.generate(UNTIL, seed=99).indicators[IndicatorSeries.FED_FUNDS]

    pd.testing.assert_series_equal(one, other)


def test_ipca_repeats_a_historical_month(generator, history):
    real = history.indicators[IndicatorSeries.IPCA]
    generated = generator.generate(UNTIL, seed=2).indicators[IndicatorSeries.IPCA]

    assert generated.index[0] == date(2005, 1, 1)
    assert set(generated.to_numpy()) <= set(real.to_numpy())


def drawn_months(generated: pd.Series, history: MarketHistory) -> list[date]:
    """O mês histórico de que cada mês gerado saiu, lido pelo valor único do IGP-M."""
    igp_m = history.indicators[IndicatorSeries.IGP_M]
    month_of = {float(value): cast("date", month) for month, value in igp_m.items()}
    return [month_of[float(value)] for value in generated]


def test_housing_series_show_up_in_the_future(generator):
    generated = generator.generate(UNTIL, seed=2).indicators

    for series in FOLLOWERS:
        assert generated[series].index[0] == date(2005, 1, 1)
        assert generated[series].index[-1] == date(2006, 12, 1)


def test_housing_series_carry_the_value_of_the_drawn_historical_month(
    generator, history
):
    """O IPCA, o IGP-M e a TR do mesmo mês gerado vêm do mesmo mês histórico."""
    generated = generator.generate(
        UNTIL, seed=3, inflation_level=0, surge_frequency=0
    ).indicators
    months = drawn_months(generated[IndicatorSeries.IGP_M], history)

    for series in (IndicatorSeries.IPCA, IndicatorSeries.TR):
        real = history.indicators[series]
        assert list(generated[series]) == [real[m] for m in months]


def test_ivg_r_drawn_before_its_first_month_follows_the_ipca_of_that_month(
    generator, history
):
    ivg_r = history.indicators[IndicatorSeries.IVG_R]
    ipca = history.indicators[IndicatorSeries.IPCA]
    before_first = 0
    for seed in range(1, 6):
        generated = generator.generate(
            UNTIL, seed=seed, inflation_level=0, surge_frequency=0
        ).indicators
        months = drawn_months(generated[IndicatorSeries.IGP_M], history)
        expected = [ivg_r[m] if m in ivg_r else ipca[m] for m in months]
        before_first += sum(m < IVG_R_FIRST_MONTH for m in months)

        assert list(generated[IndicatorSeries.IVG_R]) == expected
    assert before_first > 0


def test_series_that_start_late_repeat_the_last_value_when_the_drawn_month_is_missing(
    history,
):
    """Mês sorteado sem valor na TR: vale o último valor, que no começo é o último real."""
    tr = history.indicators[IndicatorSeries.TR]
    late_start = date(2003, 1, 1)
    late_tr = tr[[m for m in tr.index if m >= late_start]]
    shortened = MarketHistory(
        history.assets, {**history.indicators, IndicatorSeries.TR: late_tr}
    )
    generated = SeriesGenerator(shortened).generate(UNTIL, seed=3).indicators

    months = drawn_months(generated[IndicatorSeries.IGP_M], history)
    last = float(late_tr.iloc[-1])
    expected = []
    for month in months:
        last = float(late_tr[month]) if month in late_tr else last
        expected.append(last)
    assert list(generated[IndicatorSeries.TR]) == expected
    assert any(month < late_start for month in months)


def test_inflation_level_and_surges_leave_the_housing_series_alone(generator):
    calm = generator.generate(
        UNTIL, seed=4, inflation_level=0, surge_frequency=0
    ).indicators
    raised = generator.generate(
        UNTIL, seed=4, inflation_level=15, surge_frequency=5, surge_intensity=20
    ).indicators

    assert not calm[IndicatorSeries.IPCA].equals(raised[IndicatorSeries.IPCA])
    for series in FOLLOWERS:
        pd.testing.assert_series_equal(calm[series], raised[series])


def test_higher_temperature_means_a_more_agitated_market(generator):
    def mean_volatility(temperature: float) -> float:
        return float(
            np.mean(
                [
                    np.std(
                        log_returns(
                            generator.generate(
                                UNTIL, seed=seed, temperature=temperature, tickers=[]
                            ).indicators[IndicatorSeries.IBOV]
                        )
                    )
                    for seed in range(30)
                ]
            )
        )

    assert mean_volatility(0.0) < mean_volatility(1.0) < mean_volatility(3.0)


def test_temperature_outside_the_range_is_refused(generator):
    with pytest.raises(ValueError, match="Temperatura"):
        generator.generate(UNTIL, seed=1, temperature=3.5)


@pytest.mark.parametrize(
    ("controls", "message"),
    [
        ({"inflation_level": 25}, "Nível"),
        ({"surge_frequency": 6}, "Frequência"),
        ({"surge_intensity": 1}, "Intensidade"),
    ],
)
def test_inflation_controls_outside_the_range_are_refused(generator, controls, message):
    with pytest.raises(ValueError, match=message):
        generator.generate(UNTIL, seed=1, **controls)


def test_inflation_level_raises_rates_and_hits_the_market(generator):
    until = date(2010, 12, 31)
    calm = generator.generate(until, seed=4)
    raised = generator.generate(until, seed=4, inflation_level=10)

    # O nível é camada por cima dos mesmos trechos: tudo muda na mesma direção
    selic_days = list(calm.indicators[IndicatorSeries.SELIC].index)
    selic_push = synthetic.to_annual(
        raised.indicators[IndicatorSeries.SELIC].to_numpy()
    ) - synthetic.to_annual(calm.indicators[IndicatorSeries.SELIC].to_numpy())
    # A SELIC só muda em reunião: o empurrão vale do dia seguinte à primeira
    first_meeting = next_meeting(selic_days[0])
    start = next(i for i, d in enumerate(selic_days) if d > first_meeting)
    assert (selic_push[start:] > 0).all()

    # No pico, seis meses depois, a SELIC subiu 1,5x o que subiu a inflação anual, no
    # degrau da última reunião
    peak = date(2005, 7, 1)
    assert selic_push[selic_days.index(peak)] == pytest.approx(0.15, abs=0.01)
    # Cinco anos depois ela assentou perto de 1x: o juro real volta ao de antes
    assert selic_push[selic_days.index(date(2010, 1, 4))] == pytest.approx(
        0.10, abs=0.01
    )

    # A inflação fica mais alta de forma permanente: +10% ao ano são ~0,8% ao mês
    ipca_push = (
        raised.indicators[IndicatorSeries.IPCA] - calm.indicators[IndicatorSeries.IPCA]
    )
    assert ipca_push.loc[date(2010, 1, 1) :].mean() == pytest.approx(0.797, abs=0.01)

    # Na subida a bolsa leva o tombo da SELIC, e o banco, de beta maior, cai mais
    ibov_ratio = (
        raised.indicators[IndicatorSeries.IBOV] / calm.indicators[IndicatorSeries.IBOV]
    )
    assert ibov_ratio.loc[peak] < 0.9
    bank_ratio = raised.assets["BANK_A"]["close"] / calm.assets["BANK_A"]["close"]
    assert bank_ratio.loc[peak] < ibov_ratio.loc[peak]  # beta do banco acima de 1

    # Depois a bolsa sobe com a inflação somada no nominal
    assert ibov_ratio.iloc[-1] > ibov_ratio.loc[peak]


def test_the_generated_selic_changes_only_at_meetings_in_quarter_points(generator):
    generated = generator.generate(
        UNTIL, seed=7, inflation_level=8, surge_frequency=3, surge_intensity=8
    )
    series = generated.indicators[IndicatorSeries.SELIC]
    days = list(series.index)
    annual = synthetic.to_annual(series.to_numpy())
    meetings = [
        m for year in range(days[0].year, days[-1].year + 1) for m in meeting_days(year)
    ]

    # Depois da primeira reunião toda SELIC é múltipla de 0,25
    start = next(i for i, d in enumerate(days) if d > next_meeting(days[0]))
    steps = annual[start:] / 0.0025
    assert steps == pytest.approx(np.round(steps), abs=1e-3)

    # Cada mudança cai no pregão seguinte a uma reunião: no máximo 8 por ano
    changes = [
        days[i] for i in range(1, len(days)) if abs(annual[i] - annual[i - 1]) > 1e-5
    ]
    assert changes
    for day in changes:
        i = days.index(day)
        assert any(days[i - 1] <= m < day for m in meetings)
    assert (
        max(sum(d.year == y for d in changes) for y in {d.year for d in changes}) <= 8
    )


def test_inflation_level_keeps_the_subset_invariant(generator):
    controls = {"inflation_level": -5, "surge_frequency": 3, "surge_intensity": 8}
    full = generator.generate(UNTIL, seed=6, **controls)
    alone = generator.generate(UNTIL, seed=6, tickers=["POWER"], **controls)

    pd.testing.assert_frame_equal(alone.assets["POWER"], full.assets["POWER"])


def test_more_frequent_surges_contain_the_less_frequent_ones(generator):
    def surges(frequency: float) -> set[tuple[float, float]]:
        draw = synthetic._Draw(5, 1.0, 0.0, frequency / 10, 0.06)
        return set(generator._surges(draw, 30))

    rare, frequent = surges(1), surges(5)
    assert rare < frequent
    assert surges(0) == set()


def test_surges_are_pulses_over_the_same_stretches(generator):
    until = date(2014, 12, 31)
    calm = generator.generate(until, seed=9)
    surged = generator.generate(until, seed=9, surge_frequency=5, surge_intensity=12)

    ipca_push = (
        surged.indicators[IndicatorSeries.IPCA] - calm.indicators[IndicatorSeries.IPCA]
    )
    # Cada surto só soma inflação, e some quando passa
    assert (ipca_push >= -0.011).all()
    assert ipca_push.max() > 0.3
    assert ipca_push.min() < 0.05


def test_next_stretch_starts_close_to_the_current_economy(generator, history):
    # O encaixe de nível sorteia o trecho que começa com SELIC parecida com a de hoje
    today = synthetic.to_annual(
        history.indicators[IndicatorSeries.SELIC].to_numpy()[-1:]
    )[0]
    chosen = [
        generator.selic_annual[
            generator._path(draw, UNTIL).chain[generator.anchor_block]
        ]
        for draw in (synthetic._Draw(seed, 1.0, 0.0, 0.0, 0.06) for seed in range(40))
    ]
    anywhere = generator.selic_annual[generator.starts]
    assert np.mean(np.abs(np.array(chosen) - today)) < 0.5 * np.mean(
        np.abs(anywhere - today)
    )


def test_asset_without_history_in_the_drawn_stretch_follows_its_segment(generator):
    # BANK_C só existe desde 2003: os trechos de 2000 a 2002 usam os pares do segmento
    correlations = []
    for seed in range(20):
        generated = generator.generate(UNTIL, seed=seed)
        young = log_returns(generated.assets["BANK_C"]["close"])
        peer = log_returns(generated.assets["BANK_A"]["close"])
        correlations.append(np.corrcoef(young, peer)[0, 1])
    assert np.mean(correlations) > 0.8


def test_source_errors_never_reach_the_generated_series():
    history = build_history()
    bars = history.assets["BANK_A"].bars.copy()
    # Erro da fonte: o preço vai a quase zero num dia e volta no seguinte
    bars.iloc[100, bars.columns.get_loc("close")] *= 0.01
    broken = MarketHistory(
        {**history.assets, "BANK_A": AssetHistory(bars, "Bancos", "Financeiro")},
        history.indicators,
    )
    generator = SeriesGenerator(broken)

    for seed in range(20):
        generated = generator.generate(UNTIL, seed=seed, tickers=["BANK_A"])
        moves = log_returns(generated.assets["BANK_A"]["close"])
        assert moves.max() <= synthetic.MAX_DAILY_UP
        assert moves.min() >= synthetic.MAX_DAILY_DOWN


def test_zero_close_is_a_day_without_trade_and_warns(caplog):
    history = build_history()
    bars = history.assets["BANK_A"].bars.copy()
    bars.iloc[100:103, bars.columns.get_loc("close")] = 0.0
    broken = MarketHistory(
        {**history.assets, "BANK_A": AssetHistory(bars, "Bancos", "Financeiro")},
        history.indicators,
    )

    generator = SeriesGenerator(broken)
    with np.errstate(all="raise"):
        returns = generator._asset_returns("BANK_A")

    first, last = pd.Timestamp(bars.index[100]), pd.Timestamp(bars.index[102])
    zeroed = generator.calendar.get_indexer(pd.date_range(first, last, freq="B"))
    assert np.isnan(returns[zeroed]).all()
    assert "'BANK_A' tem fechamento zerado em 3 pregões" in caplog.text
    assert f"de {first.date()} a {last.date()}" in caplog.text


def test_market_index_is_required(history):
    without_ibov = MarketHistory(
        history.assets,
        {k: v for k, v in history.indicators.items() if k is not IndicatorSeries.IBOV},
    )
    with pytest.raises(ValueError, match="Ibovespa"):
        SeriesGenerator(without_ibov)
