"""Erro de dado do yfinance: o dia de preço absurdo que volta vira interpolação."""

from __future__ import annotations

import pandas as pd
import pytest

from backend.features.import_data.price_errors import fix_price_errors


def _frame(closes: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Open": closes,
            "High": [c * 1.01 for c in closes],
            "Low": [c * 0.99 for c in closes],
            "Close": closes,
            "Volume": [1000] * len(closes),
        },
        index=pd.bdate_range("2024-01-02", periods=len(closes)),
    )


def test_dip_to_near_zero_that_returns_is_interpolated() -> None:
    frame = _frame([10.0, 10.0, 0.05, 12.0, 12.0])

    fixed, corrected = fix_price_errors(frame)

    assert corrected == [frame.index[2]]
    # Linha reta entre 10 (último bom) e 12 (primeiro bom depois)
    assert fixed["Close"].iloc[2] == pytest.approx(11.0)
    # Sem vela falsa: abertura, máxima e mínima iguais ao fechamento e volume zero
    day = fixed.iloc[2]
    assert day["Open"] == day["High"] == day["Low"] == day["Close"]
    assert day["Volume"] == 0
    # O resto da série fica como veio
    assert fixed["Close"].iloc[[0, 1, 3, 4]].tolist() == [10.0, 10.0, 12.0, 12.0]
    assert frame["Close"].iloc[2] == 0.05


def test_spike_up_that_returns_is_interpolated() -> None:
    fixed, corrected = fix_price_errors(_frame([10.0, 98.0, 10.0]))

    assert len(corrected) == 1
    assert fixed["Close"].iloc[1] == pytest.approx(10.0)


def test_error_that_lasts_several_sessions_is_interpolated_in_a_line() -> None:
    frame = _frame([10.0, 0.1, 0.1, 0.1, 14.0, 14.0])

    fixed, corrected = fix_price_errors(frame)

    assert corrected == list(frame.index[1:4])
    assert fixed["Close"].iloc[1:4].tolist() == pytest.approx([11.0, 12.0, 13.0])


def test_zero_close_that_returns_is_an_error() -> None:
    fixed, corrected = fix_price_errors(_frame([10.0, 0.0, 10.0]))

    assert len(corrected) == 1
    assert fixed["Close"].iloc[1] == pytest.approx(10.0)


def test_step_that_does_not_return_is_left_alone() -> None:
    frame = _frame([10.0, 10.0, 3.4, 3.4, 3.5, 3.5, 3.4, 3.4, 3.5, 3.5])

    fixed, corrected = fix_price_errors(frame)

    assert corrected == []
    assert fixed["Close"].tolist() == frame["Close"].tolist()


def test_return_after_the_recovery_window_is_not_an_error() -> None:
    frame = _frame([10.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 10.0])

    _, corrected = fix_price_errors(frame, max_recovery_days=3)

    assert corrected == []


def test_error_at_the_end_of_the_series_is_left_alone() -> None:
    frame = _frame([10.0, 10.0, 0.05])

    fixed, corrected = fix_price_errors(frame)

    assert corrected == []
    assert fixed["Close"].iloc[2] == 0.05


def test_normal_moves_below_the_threshold_are_left_alone() -> None:
    _, corrected = fix_price_errors(_frame([10.0, 14.0, 9.0, 13.0, 8.0]))

    assert corrected == []


def test_empty_series_has_no_errors() -> None:
    fixed, corrected = fix_price_errors(pd.DataFrame())

    assert fixed.empty
    assert corrected == []


def test_anchor_close_judges_the_first_day_of_an_incremental_import() -> None:
    frame = _frame([0.05, 10.2, 10.3])

    _, without_anchor = fix_price_errors(frame)
    fixed, with_anchor = fix_price_errors(frame, anchor_close=10.0)

    assert without_anchor == []
    assert with_anchor == [frame.index[0]]
    assert fixed["Close"].iloc[0] == pytest.approx(10.1)


def test_two_separate_errors_are_both_corrected() -> None:
    fixed, corrected = fix_price_errors(
        _frame([10.0, 0.1, 10.0, 10.0, 90.0, 10.0, 10.0])
    )

    assert len(corrected) == 2
    assert fixed["Close"].tolist() == pytest.approx([10.0] * 7)
