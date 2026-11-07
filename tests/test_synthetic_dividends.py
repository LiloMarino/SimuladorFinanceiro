"""Dividendos do gerador: calibração pelo retorno total, calendário e queda na data ex."""

from datetime import date

import numpy as np
import pandas as pd

from backend.core.enum import CorporateEventKind
from backend.features.import_data import synthetic
from backend.features.import_data.synthetic import (
    AssetHistory,
    MarketHistory,
    SeriesGenerator,
)
from tests.test_synthetic_series import (
    LAST_REAL,
    UNTIL,
    build_history,
)

PAID_MONTHS = (3, 9)


def _dividends(bars: pd.DataFrame, yearly_yield: float, months=PAID_MONTHS):
    """Dividendos reais: o rendimento do ano dividido nos meses, no primeiro pregão do dia 10."""
    paid: dict[date, float] = {}
    for year in range(2000, LAST_REAL.year + 1):
        for month in months:
            day = next((d for d in bars.index if d >= date(year, month, 10)), None)
            if day is not None and day.year == year:
                paid[day] = float(bars.loc[day, "close"]) * yearly_yield / len(months)
    return pd.Series(paid, dtype=float)


def _with(history: MarketHistory, ticker: str, **changes) -> MarketHistory:
    old = history.assets[ticker]
    fields = {
        "bars": old.bars,
        "segment": old.segment,
        "sector": old.sector,
        "splits": old.splits,
        "dividends": old.dividends,
        "pays_dividends": old.pays_dividends,
    } | changes
    return MarketHistory(
        {**history.assets, ticker: AssetHistory(**fields)}, history.indicators
    )


def _generate(history: MarketHistory, ticker: str = "BANK_A"):
    return SeriesGenerator(history).generate(UNTIL, seed=3, tickers=[ticker])


def test_asset_that_paid_keeps_paying_in_its_months():
    base = build_history()
    payer = _with(
        base, "BANK_A", dividends=_dividends(base.assets["BANK_A"].bars, 0.06)
    )

    generated = _generate(payer)
    events = generated.events["BANK_A"]

    assert events
    assert {e.kind for e in events} == {CorporateEventKind.DIVIDEND}
    assert {e.ex_date.month for e in events} == set(PAID_MONTHS)
    assert all(e.value > 0 for e in events)


def test_ex_date_takes_the_dividend_out_of_the_price():
    base = build_history()
    dividends = _dividends(base.assets["BANK_A"].bars, 0.12)
    # Mesma calibração nos dois; só um deles paga na partida
    pays = _with(base, "BANK_A", dividends=dividends)
    holds = _with(base, "BANK_A", dividends=dividends, pays_dividends=False)

    paying = _generate(pays)
    kept = _generate(holds).assets["BANK_A"]["close"]
    close = paying.assets["BANK_A"]["close"]

    assert paying.events["BANK_A"]
    assert close.iloc[-1] < kept.iloc[-1]
    # Antes do primeiro pagamento os dois caminhos são o mesmo
    first = paying.events["BANK_A"][0]
    before = list(close.index).index(first.ex_date) - 1
    assert close.iloc[before] == kept.iloc[before]
    # Na data ex o preço cai o valor pago em relação ao caminho que não paga
    lost = kept.iloc[before + 1] - close.iloc[before + 1]
    assert abs(lost - first.value * kept.iloc[before + 1] / kept.iloc[before]) < 1e-3


def test_two_silent_years_stop_the_payment():
    base = build_history()
    # Pagava até 2002; nos dois últimos anos reais não pagou nada
    old = _dividends(base.assets["BANK_A"].bars, 0.06)
    old = old[[d.year <= LAST_REAL.year - 3 for d in old.index]]

    generated = _generate(_with(base, "BANK_A", dividends=old))

    assert generated.events["BANK_A"] == []


def test_crypto_never_pays_even_with_history():
    base = build_history()
    payer = _with(
        base,
        "BANK_A",
        dividends=_dividends(base.assets["BANK_A"].bars, 0.06),
        pays_dividends=False,
    )

    assert _generate(payer).events["BANK_A"] == []


def test_short_history_pays_the_segment_average_every_quarter():
    base = build_history()
    # BANK_C tem pouco histórico; BANK_A e BANK_B, do mesmo segmento, pagam
    history = _with(
        base, "BANK_A", dividends=_dividends(base.assets["BANK_A"].bars, 0.08)
    )
    history = _with(
        history, "BANK_B", dividends=_dividends(base.assets["BANK_B"].bars, 0.04)
    )
    young = history.assets["BANK_C"]
    short = _with(history, "BANK_C", bars=young.bars.iloc[-300:])

    events = _generate(short, "BANK_C").events["BANK_C"]

    assert {e.ex_date.month for e in events} == set(synthetic.NEW_ASSET_PAY_MONTHS)


def test_total_return_calibration_counts_the_dividend():
    base = build_history()
    bars = base.assets["BANK_A"].bars
    payer = _with(base, "BANK_A", dividends=_dividends(bars, 0.06))

    plain = SeriesGenerator(base)._asset_returns("BANK_A")
    total = SeriesGenerator(payer)._asset_returns("BANK_A")

    # O dividendo aparece como retorno positivo na data ex
    assert np.nansum(total) > np.nansum(plain)


def test_split_does_not_register_as_a_crash():
    base = build_history()
    bars = base.assets["BANK_A"].bars.copy()
    day = bars.index[1000]
    # Desdobramento 3:1: o preço negociado cai a um terço dali em diante
    bars.loc[bars.index >= day, ["open", "high", "low", "close"]] /= 3
    split = _with(base, "BANK_A", bars=bars, splits=pd.Series({day: 3.0}))
    raw = SeriesGenerator(_with(base, "BANK_A", bars=bars))._asset_returns("BANK_A")
    adjusted = SeriesGenerator(split)._asset_returns("BANK_A")

    index = SeriesGenerator(split).calendar_days.index(day)
    assert np.isnan(raw[index])  # a queda a um terço é erro de dado sem o evento
    assert abs(adjusted[index]) < 0.2
