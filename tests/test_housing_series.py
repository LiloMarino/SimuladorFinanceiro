"""IVG-R, IGP-M e TR: o importador lê o SGS e a Central os trata como séries da economia."""

from __future__ import annotations

import io
import json
import re
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from urllib.request import Request

import pytest

from backend.core.enum import IndicatorSeries
from backend.features.import_data import bcb_sgs
from backend.features.import_data.indicators import (
    INDICATOR_SOURCES,
    monthly_change,
)

FIXTURES = Path(__file__).parent / "fixtures"
# Trecho real da resposta de cada série no SGS, pelo código
RECORDED = {
    21340: FIXTURES / "sgs_ivg_r_2001.json",
    189: FIXTURES / "sgs_igp_m_2024.json",
    7811: FIXTURES / "sgs_tr_2024.json",
}


def _day(text: str) -> date:
    return datetime.strptime(text, "%d/%m/%Y").date()  # noqa: DTZ007


@pytest.fixture
def sgs(monkeypatch: pytest.MonkeyPatch) -> list[tuple[int, date, date]]:
    """Responde com o trecho gravado, só com os meses da janela pedida, e guarda cada pedido."""
    requests: list[tuple[int, date, date]] = []

    def fake_urlopen(request: Request, timeout: int):
        match = re.search(r"bcdata\.sgs\.(\d+)", request.full_url)
        assert match is not None
        code = int(match.group(1))
        query = parse_qs(urlparse(request.full_url).query)
        start, end = _day(query["dataInicial"][0]), _day(query["dataFinal"][0])
        requests.append((code, start, end))
        payload = json.loads(RECORDED[code].read_text())
        inside = [item for item in payload if start <= _day(item["data"]) <= end]
        return io.BytesIO(json.dumps(inside).encode())

    monkeypatch.setattr(bcb_sgs, "urlopen", fake_urlopen)
    return requests


def test_ivg_r_is_stored_as_the_change_of_each_month_over_the_previous(sgs):
    """O SGS publica o número-índice (base 100 em março de 2001): a série guarda % ao mês."""
    rows = INDICATOR_SOURCES[IndicatorSeries.IVG_R].fetch(
        date(2001, 3, 1), date(2001, 6, 30)
    )

    assert rows == [
        (date(2001, 4, 1), Decimal("0.080000")),
        (date(2001, 5, 1), Decimal("0.069944")),
        (date(2001, 6, 1), Decimal("0.069895")),
    ]


def test_ivg_r_has_no_value_before_its_first_month(sgs):
    """Março de 2001 é a base do índice: sem variação e sem dado antes dele."""
    rows = INDICATOR_SOURCES[IndicatorSeries.IVG_R].fetch(
        INDICATOR_SOURCES[IndicatorSeries.IVG_R].first_date, date(2001, 6, 30)
    )

    assert rows[0][0] == date(2001, 4, 1)
    assert [request[0] for request in sgs] == [21340]
    assert sgs[0][1] == date(2001, 3, 1)


def test_ivg_r_refresh_reads_the_month_before_to_get_the_change(sgs):
    """A busca que recomeça em maio pede o índice desde abril, que a variação de maio precisa."""
    rows = INDICATOR_SOURCES[IndicatorSeries.IVG_R].fetch(
        date(2001, 5, 1), date(2001, 6, 30)
    )

    assert sgs[0][1] == date(2001, 4, 1)
    assert [day for day, _ in rows] == [date(2001, 5, 1), date(2001, 6, 1)]


def test_monthly_change_keeps_the_decimal_exact():
    index = [
        (date(2001, 3, 1), Decimal("100.00")),
        (date(2001, 4, 1), Decimal("100.5")),
    ]

    assert monthly_change(index) == [(date(2001, 4, 1), Decimal("0.500000"))]


def test_igp_m_comes_as_published_in_percent_per_month(sgs):
    rows = INDICATOR_SOURCES[IndicatorSeries.IGP_M].fetch(
        date(2024, 1, 1), date(2024, 5, 31)
    )

    assert sgs[0][0] == 189
    assert rows == [
        (date(2024, 1, 1), Decimal("0.07")),
        (date(2024, 2, 1), Decimal("-0.52")),
        (date(2024, 3, 1), Decimal("-0.47")),
        (date(2024, 4, 1), Decimal("0.31")),
        (date(2024, 5, 1), Decimal("0.89")),
    ]


def test_tr_is_the_monthly_series_not_the_daily_one(sgs):
    rows = INDICATOR_SOURCES[IndicatorSeries.TR].fetch(
        date(2024, 1, 1), date(2024, 5, 31)
    )

    assert sgs[0][0] == 7811
    assert rows[0] == (date(2024, 1, 1), Decimal("0.0875"))
    assert rows[-1] == (date(2024, 5, 1), Decimal("0.0870"))


def test_the_three_are_economy_series_with_a_generated_future_and_a_provider():
    for series in (IndicatorSeries.IVG_R, IndicatorSeries.IGP_M, IndicatorSeries.TR):
        assert series.is_macro
        assert series.is_monthly
        assert series.has_generated_future
    assert INDICATOR_SOURCES[IndicatorSeries.IGP_M].provider == "FGV via Banco Central"
