"""Gerador de séries sintéticas sobre um histórico pequeno montado no teste."""

from datetime import date

import numpy as np
import pandas as pd
import pytest

from backend.core.enum import IndicatorSeries
from backend.core.utils import is_business_day, next_business_day
from backend.features.import_data import synthetic
from backend.features.import_data.synthetic import (
    AssetHistory,
    MarketHistory,
    Regime,
    SeriesGenerator,
)

LAST_REAL = date(2004, 12, 31)
UNTIL = date(2006, 12, 29)


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
    indicators = {
        IndicatorSeries.IBOV: pd.Series(10_000 * np.exp(np.cumsum(market)), index=days),
        IndicatorSeries.SELIC: pd.Series(selic, index=days),
        IndicatorSeries.CDI: pd.Series(cdi, index=days),
        IndicatorSeries.IPCA: pd.Series(ipca, index=[m.date() for m in months]),
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
    selic_real = synthetic._to_annual(
        history.indicators[IndicatorSeries.SELIC].to_numpy()
    )
    last_spread = (
        selic_real[-1]
        - synthetic._to_annual(history.indicators[IndicatorSeries.CDI].to_numpy())[-1]
    )

    for seed in range(20):
        generated = generator.generate(UNTIL, seed=seed)
        selic = synthetic._to_annual(
            generated.indicators[IndicatorSeries.SELIC].to_numpy()
        )
        cdi = synthetic._to_annual(generated.indicators[IndicatorSeries.CDI].to_numpy())
        assert selic.min() >= selic_real.min() - 1e-6
        assert selic.max() <= selic_real.max() + 1e-6
        np.testing.assert_allclose(selic - cdi, last_spread, atol=1e-4)


def test_ipca_repeats_a_historical_month(generator, history):
    real = history.indicators[IndicatorSeries.IPCA]
    generated = generator.generate(UNTIL, seed=2).indicators[IndicatorSeries.IPCA]

    assert generated.index[0] == date(2005, 1, 1)
    assert set(generated.to_numpy()) <= set(real.to_numpy())


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


def test_inflation_shock_outside_the_range_is_refused(generator):
    with pytest.raises(ValueError, match="Choque"):
        generator.generate(UNTIL, seed=1, inflation_shock=25)


def test_inflation_shock_raises_rates_and_hits_the_market(generator):
    calm = generator.generate(UNTIL, seed=4)
    shocked = generator.generate(UNTIL, seed=4, inflation_shock=10)

    # O choque é camada por cima dos mesmos trechos: tudo muda na mesma direção
    ipca_push = (
        shocked.indicators[IndicatorSeries.IPCA] - calm.indicators[IndicatorSeries.IPCA]
    )
    selic_push = synthetic._to_annual(
        shocked.indicators[IndicatorSeries.SELIC].to_numpy()
    ) - synthetic._to_annual(calm.indicators[IndicatorSeries.SELIC].to_numpy())
    assert (ipca_push.iloc[1:] > 0).all()
    assert (selic_push[5:] > 0).all()

    # No pico, seis meses depois, a SELIC subiu 1,5x o que subiu a inflação anual
    peak = date(2005, 7, 1)
    selic_peak = selic_push[
        list(calm.indicators[IndicatorSeries.SELIC].index).index(peak)
    ]
    assert selic_peak == pytest.approx(0.15, abs=0.005)

    ibov_ratio = (
        shocked.indicators[IndicatorSeries.IBOV] / calm.indicators[IndicatorSeries.IBOV]
    )
    assert ibov_ratio.loc[peak] < 0.9
    bank_ratio = shocked.assets["BANK_A"]["close"] / calm.assets["BANK_A"]["close"]
    assert bank_ratio.loc[peak] < ibov_ratio.loc[peak]  # beta do banco acima de 1


def test_inflation_shock_keeps_the_subset_invariant(generator):
    full = generator.generate(UNTIL, seed=6, inflation_shock=-5)
    alone = generator.generate(UNTIL, seed=6, inflation_shock=-5, tickers=["POWER"])

    pd.testing.assert_frame_equal(alone.assets["POWER"], full.assets["POWER"])


def test_next_stretch_starts_close_to_the_current_economy(generator, history):
    # O encaixe de nível sorteia o trecho que começa com SELIC parecida com a de hoje
    today = synthetic._to_annual(
        history.indicators[IndicatorSeries.SELIC].to_numpy()[-1:]
    )[0]
    chosen = [
        generator.selic_annual[
            generator._path(draw, UNTIL).chain[generator.anchor_block]
        ]
        for draw in (
            synthetic._Draw(seed, 1.0, generator.current_regime, 0.0)
            for seed in range(40)
        )
    ]
    anywhere = generator.selic_annual[generator.starts]
    assert np.mean(np.abs(np.array(chosen) - today)) < 0.5 * np.mean(
        np.abs(anywhere - today)
    )


def test_starting_in_a_crisis_begins_agitated(generator):
    def first_quarter_volatility(regime: Regime) -> float:
        return float(
            np.mean(
                [
                    np.std(
                        log_returns(
                            generator.generate(
                                date(2005, 3, 31),
                                seed=seed,
                                start_regime=regime,
                                tickers=[],
                            ).indicators[IndicatorSeries.IBOV]
                        )
                    )
                    for seed in range(30)
                ]
            )
        )

    calm, normal, agitated = (first_quarter_volatility(r) for r in Regime)
    assert calm < normal < agitated


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


def test_market_index_is_required(history):
    without_ibov = MarketHistory(
        history.assets,
        {k: v for k, v in history.indicators.items() if k is not IndicatorSeries.IBOV},
    )
    with pytest.raises(ValueError, match="Ibovespa"):
        SeriesGenerator(without_ibov)
