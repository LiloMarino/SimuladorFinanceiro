from __future__ import annotations

import io
from datetime import date
from decimal import Decimal
from urllib.parse import parse_qs, urlparse
from urllib.request import Request

import pytest

from backend.features.import_data import fred
from backend.features.import_data.fred import fetch_fed_funds, parse_fred_csv

CSV = """observation_date,DFF
2026-10-30,3.87
2026-10-31,3.87
2026-11-01,.
2026-11-02,3.88
"""


def test_csv_becomes_annual_percent_as_decimal():
    rows = parse_fred_csv(CSV)

    assert rows == [
        (date(2026, 10, 30), Decimal("3.87")),
        (date(2026, 10, 31), Decimal("3.87")),
        (date(2026, 11, 2), Decimal("3.88")),
    ]
    assert all(isinstance(value, Decimal) for _, value in rows)


def test_csv_without_rows_is_empty():
    assert parse_fred_csv("observation_date,DFF\n") == []


def test_fetch_asks_for_the_dff_series_in_the_window(monkeypatch: pytest.MonkeyPatch):
    sent: list[Request] = []

    def fake_urlopen(request: Request, timeout: int):
        sent.append(request)
        return io.BytesIO(CSV.encode())

    monkeypatch.setattr(fred, "urlopen", fake_urlopen)

    rows = fetch_fed_funds(date(2026, 10, 30), date(2026, 11, 2))

    query = parse_qs(urlparse(sent[0].full_url).query)
    assert query["id"] == ["DFF"]
    assert query["cosd"] == ["2026-10-30"]
    assert query["coed"] == ["2026-11-02"]
    assert len(rows) == 3
