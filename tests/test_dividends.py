"""Contas dos proventos: janela de 12 meses, desdobramento, DY, YoC e o histórico do ativo."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core.dto.corporate_event import CorporateEventDTO
from backend.core.dto.dividends import DividendPaymentDTO
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.enum import AssetClass, CorporateEventKind, EquityEventType
from backend.features.variable_income.dividends import (
    build_asset_events,
    build_portfolio_dividends,
    dividend_yield,
    monthly_buckets,
    scale_dividends,
    trailing_per_share,
    yearly_buckets,
    yield_on_cost,
)

TODAY = date(2021, 6, 15)
STOCK = 1


def _dividend(ex_date: date, value: float, stock_id: int = STOCK) -> CorporateEventDTO:
    return CorporateEventDTO(
        stock_id=stock_id,
        ex_date=ex_date,
        kind=CorporateEventKind.DIVIDEND,
        value=value,
    )


def _split(ex_date: date, ratio: float, stock_id: int = STOCK) -> CorporateEventDTO:
    return CorporateEventDTO(
        stock_id=stock_id,
        ex_date=ex_date,
        kind=CorporateEventKind.SPLIT,
        value=ratio,
    )


def _payment(
    day: date,
    amount: str,
    ticker: str = "ABCD",
    asset_class: AssetClass = AssetClass.STOCK,
) -> DividendPaymentDTO:
    return DividendPaymentDTO(
        ticker=ticker,
        name=ticker,
        asset_class=asset_class,
        event_date=day,
        amount=Decimal(amount),
    )


def _equity(
    day: date, event_type: EquityEventType, quantity: str, price: str = "0"
) -> EquityEventDTO:
    return EquityEventDTO(
        simulation_id=1,
        portfolio_id=1,
        event_date=day,
        ticker="ABCD",
        event_type=event_type,
        quantity=Decimal(quantity),
        price=Decimal(price),
    )


def test_the_dividend_follows_the_stock_factor_of_the_ex_date():
    """Com a bolsa a 1/400 da história, o provento sai a 1/400 do valor guardado."""
    events = [_dividend(date(2021, 3, 10), 2.0), _dividend(date(2021, 4, 10), 4.0)]
    factors = {date(2021, 3, 10): 1 / 400, date(2021, 4, 10): 0.5}

    scaled = scale_dividends(events, {STOCK: "ABCD"}, lambda _, day: factors[day])

    assert [e.value for e in scaled] == [pytest.approx(0.005), 2.0]
    # Os originais seguem como foram guardados
    assert [e.value for e in events] == [2.0, 4.0]


def test_the_split_ratio_is_not_scaled():
    events = [_split(date(2021, 3, 10), 2.0)]

    scaled = scale_dividends(events, {STOCK: "ABCD"}, lambda _ticker, _day: 0.01)

    assert scaled == events


def test_the_yield_of_a_scaled_dividend_stays_at_the_historical_one():
    """Preço e provento na mesma escala: o rendimento não muda com o fator da bolsa."""
    factor = 1 / 400
    events = scale_dividends(
        [_dividend(date(2021, 3, 10), 0.44)], {STOCK: "ABCD"}, lambda _t, _d: factor
    )

    per_share = trailing_per_share(events, TODAY)[STOCK]
    price = Decimal("4.40") * Decimal(str(factor))

    assert dividend_yield(per_share, price, AssetClass.STOCK) == pytest.approx(
        Decimal("0.10")
    )


def test_trailing_window_includes_today_and_excludes_exactly_twelve_months_ago():
    """A data ex em (hoje - 12 meses, hoje]: o dia exato de um ano atrás já ficou de fora."""
    events = [
        _dividend(date(2020, 6, 15), 9),
        _dividend(date(2020, 6, 16), 1),
        _dividend(TODAY, 2),
        _dividend(date(2021, 6, 16), 50),
    ]

    assert trailing_per_share(events, TODAY) == {STOCK: Decimal(3)}


def test_split_after_a_dividend_scales_it_to_todays_unit():
    """Provento de R$ 1,00 antes de um 2 para 1 vale R$ 0,50 na unidade de hoje."""
    events = [
        _dividend(date(2020, 9, 1), 1),
        _split(date(2021, 1, 4), 2),
        _dividend(date(2021, 3, 1), 0.30),
    ]

    assert trailing_per_share(events, TODAY)[STOCK] == Decimal("0.80")


def test_reverse_split_multiplies_earlier_dividends():
    """Grupamento 10 para 1 (razão 0,1): o provento de antes sobe dez vezes."""
    events = [_dividend(date(2020, 9, 1), 0.10), _split(date(2021, 1, 4), 0.1)]

    assert trailing_per_share(events, TODAY)[STOCK] == Decimal(1)


def test_split_on_the_same_day_as_the_dividend_does_not_adjust_it():
    events = [_dividend(date(2021, 1, 4), 1), _split(date(2021, 1, 4), 2)]

    assert trailing_per_share(events, TODAY)[STOCK] == Decimal(1)


def test_yields_use_price_today_and_average_price():
    """R$ 1,20 por ação: sobre o preço de hoje (R$ 20) dá 6%; sobre o médio (R$ 12) dá 10%."""
    assert dividend_yield(Decimal("1.2"), Decimal(20), AssetClass.STOCK) == Decimal(
        "0.06"
    )
    assert yield_on_cost(Decimal("1.2"), Decimal(12), AssetClass.STOCK) == Decimal(
        "0.1"
    )


def test_asset_without_payment_yields_zero():
    assert dividend_yield(Decimal(0), Decimal(20), AssetClass.STOCK) == Decimal(0)


def test_crypto_and_zero_price_have_no_yield():
    assert dividend_yield(Decimal(1), Decimal(20), AssetClass.CRYPTO) is None
    assert yield_on_cost(Decimal(1), Decimal(10), AssetClass.CRYPTO) is None
    assert dividend_yield(Decimal(1), Decimal(0), AssetClass.STOCK) is None


def test_monthly_buckets_cover_twelve_calendar_months_with_zeros():
    payments = [
        _payment(date(2020, 6, 30), "5"),
        _payment(date(2020, 7, 1), "10"),
        _payment(date(2021, 6, 15), "30", "WXYZ", AssetClass.FII),
    ]

    buckets = monthly_buckets(payments, TODAY)

    assert len(buckets) == 12
    assert buckets[0].period == date(2020, 7, 1)
    assert buckets[-1].period == date(2021, 6, 1)
    assert buckets[0].amount == Decimal(10)
    assert buckets[5].amount == Decimal(0)
    assert buckets[-1].amount == Decimal(30)
    assert buckets[-1].by_class[0].asset_class is AssetClass.FII


def test_yearly_buckets_run_from_first_payment_to_this_year():
    payments = [_payment(date(2019, 3, 1), "7"), _payment(date(2021, 2, 1), "3")]

    buckets = yearly_buckets(payments, TODAY)

    assert [(b.period.year, b.amount) for b in buckets] == [
        (2019, Decimal(7)),
        (2020, Decimal(0)),
        (2021, Decimal(3)),
    ]
    assert [b.period.year for b in yearly_buckets([], TODAY)] == [2021]


def test_portfolio_dividends_totals_average_and_payers():
    payments = [
        _payment(date(2020, 1, 10), "100"),
        _payment(date(2020, 8, 10), "60", "ABCD"),
        _payment(date(2021, 3, 10), "120", "WXYZ", AssetClass.FII),
        _payment(date(2021, 4, 10), "60", "ABCD"),
    ]

    result = build_portfolio_dividends(payments, TODAY)

    assert result.total == Decimal(340)
    assert result.total_12m == Decimal(240)
    assert result.average_per_month == Decimal(20)
    assert result.payments_count == 4
    assert result.first_payment_date == date(2020, 1, 10)
    assert result.classes == [AssetClass.STOCK, AssetClass.FII]
    assert {(p.ticker, p.amount, p.share) for p in result.payers} == {
        ("ABCD", Decimal(120), Decimal("0.5")),
        ("WXYZ", Decimal(120), Decimal("0.5")),
    }


def test_portfolio_dividends_without_payments():
    result = build_portfolio_dividends([], TODAY)

    assert result.total == Decimal(0)
    assert result.average_per_month == Decimal(0)
    assert result.first_payment_date is None
    assert result.payers == []


def _asset_events(**overrides):
    args = {
        "ticker": "ABCD",
        "asset_class": AssetClass.STOCK,
        "events": [],
        "equity_events": [],
        "payments": [],
        "match_start": date(2020, 1, 1),
        "per_share": Decimal("1.2"),
        "price": Decimal(20),
        "avg_price": Decimal(12),
    }
    return build_asset_events(**{**args, **overrides})


def test_asset_history_dividend_row_uses_opening_shares_and_credit():
    events = [_dividend(date(2020, 5, 4), 0.5)]
    equity = [
        _equity(date(2020, 3, 2), EquityEventType.BUY, "100", "10"),
        _equity(date(2020, 5, 4), EquityEventType.BUY, "50", "10"),
    ]
    payments = [_payment(date(2020, 5, 4), "50")]

    result = _asset_events(events=events, equity_events=equity, payments=payments)

    row = result.events[0]
    assert (row.shares, row.received, row.before_match) == (
        Decimal(100),
        Decimal(50),
        False,
    )
    assert result.received_total == Decimal(50)
    assert result.dividend_yield_12m == Decimal("0.06")
    assert result.yield_on_cost == Decimal("0.1")


def test_asset_history_split_row_shows_before_and_after_and_fraction():
    events = [_split(date(2020, 5, 4), 2)]
    equity = [
        _equity(date(2020, 3, 2), EquityEventType.BUY, "101", "10"),
        _equity(date(2020, 5, 4), EquityEventType.SPLIT, "101"),
        _equity(date(2020, 5, 4), EquityEventType.FRACTION_SELL, "0.5", "6"),
    ]

    row = _asset_events(events=events, equity_events=equity).events[0]

    assert (row.shares, row.shares_after, row.received) == (
        Decimal(101),
        Decimal("201.5"),
        Decimal(3),
    )


def test_asset_history_marks_events_before_the_match_without_values():
    events = [_dividend(date(2019, 12, 2), 0.5), _dividend(date(2020, 1, 1), 0.5)]

    rows = _asset_events(events=events).events

    assert all(r.before_match for r in rows)
    assert all(r.shares is None and r.received is None for r in rows)


def test_asset_history_without_open_position_has_no_yield_on_cost():
    assert _asset_events(avg_price=None).yield_on_cost is None
