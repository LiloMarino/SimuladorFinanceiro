from __future__ import annotations

import io
import json
from datetime import date
from decimal import Decimal
from urllib.parse import parse_qs, urlparse
from urllib.request import Request

import pytest

from backend.features.import_data import bcb_focus
from backend.features.import_data.bcb_focus import (
    fetch_focus_annual,
    fetch_focus_ipca,
    fetch_focus_selic,
)


@pytest.fixture
def focus(monkeypatch: pytest.MonkeyPatch):
    """Troca a rede por respostas em memória e guarda cada pedido (recurso e filtro)."""
    requests: list[tuple[str, str]] = []
    responses: list[list[dict]] = []

    def fake_urlopen(request: Request, timeout: int):
        url = urlparse(request.full_url)
        requests.append(
            (url.path.rsplit("/", 1)[-1], parse_qs(url.query)["$filter"][0])
        )
        rows = responses.pop(0) if responses else []
        body = json.dumps({"value": rows})
        return io.BytesIO(body.encode())

    monkeypatch.setattr(bcb_focus, "urlopen", fake_urlopen)
    return requests, responses


def test_selic_keeps_the_next_meeting_of_each_survey_day(focus):
    """A menor reunião de cada dia, por (ano, número): R8/2006 vem antes de R1/2007."""
    _, responses = focus
    responses.append(
        [
            {"Data": "2006-03-01", "Reuniao": "R1/2007", "Mediana": 13.5},
            {"Data": "2006-03-01", "Reuniao": "R8/2006", "Mediana": 16.5},
            {"Data": "2006-03-01", "Reuniao": "R2/2006", "Mediana": 17.25},
            {"Data": "2006-03-02", "Reuniao": "R2/2006", "Mediana": 17.0},
            {"Data": "2006-03-02", "Reuniao": "R3/2006", "Mediana": 16.0},
        ]
    )

    rows = fetch_focus_selic(date(2006, 3, 1), date(2006, 3, 2))

    assert rows == [
        (date(2006, 3, 1), Decimal("17.25")),
        (date(2006, 3, 2), Decimal("17.0")),
    ]


def test_the_median_is_a_decimal_read_from_the_text(focus):
    _, responses = focus
    responses.append([{"Data": "2020-01-02", "Mediana": 4.1}])

    ((_, value),) = fetch_focus_ipca(date(2020, 1, 1), date(2020, 1, 31))

    assert isinstance(value, Decimal)
    assert value == Decimal("4.1")


def test_ipca_asks_for_the_smoothed_twelve_months_with_the_full_survey(focus):
    requests, _ = focus

    fetch_focus_ipca(date(2020, 1, 1), date(2020, 1, 31))

    resource, condition = requests[0]
    assert resource == "ExpectativasMercadoInflacao12Meses"
    assert "Indicador eq 'IPCA'" in condition
    assert "Suavizada eq 'S'" in condition
    assert "baseCalculo eq 0" in condition


def test_annual_series_keep_the_reference_year_of_the_survey_day(focus):
    """O PIB e o câmbio do ano são os da `DataReferencia` igual ao ano da pesquisa."""
    requests, responses = focus
    responses.append(
        [
            {"Data": "2020-06-05", "DataReferencia": "2020", "Mediana": -6.5},
            {"Data": "2020-06-05", "DataReferencia": "2021", "Mediana": 3.0},
            {"Data": "2020-06-05", "DataReferencia": "2022", "Mediana": 2.5},
        ]
    )

    rows = fetch_focus_annual("PIB Total", date(2020, 6, 1), date(2020, 6, 30))

    assert rows == [(date(2020, 6, 5), Decimal("-6.5"))]
    assert requests[0][0] == "ExpectativasMercadoAnuais"
    assert "Indicador eq 'PIB Total'" in requests[0][1]


def test_an_empty_answer_is_an_empty_series(focus):
    assert fetch_focus_selic(date(2030, 1, 1), date(2030, 2, 1)) == []
    assert fetch_focus_ipca(date(2030, 1, 1), date(2030, 2, 1)) == []
    assert fetch_focus_annual("Câmbio", date(2030, 1, 1), date(2030, 2, 1)) == []


def test_a_long_period_is_split_in_windows_of_ten_years(focus):
    requests, _ = focus

    fetch_focus_ipca(date(2001, 11, 7), date(2024, 12, 31))

    assert len(requests) == 3
    assert "Data ge '2001-11-07'" in requests[0][1]
    assert "Data le '2024-12-31'" in requests[-1][1]
