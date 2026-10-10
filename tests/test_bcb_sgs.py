from __future__ import annotations

import io
import json
from datetime import date
from decimal import Decimal
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlparse
from urllib.request import Request

import pytest

from backend.features.import_data import bcb_sgs
from backend.features.import_data.bcb_sgs import fetch_sgs


@pytest.fixture
def sgs(monkeypatch: pytest.MonkeyPatch):
    """Troca a rede por respostas em memória e guarda as janelas pedidas."""
    windows: list[tuple[str, str]] = []
    responses: list[object] = []

    def fake_urlopen(request: Request, timeout: int):
        query = parse_qs(urlparse(request.full_url).query)
        windows.append((query["dataInicial"][0], query["dataFinal"][0]))
        response = responses.pop(0) if responses else []
        if isinstance(response, Exception):
            raise response
        return io.BytesIO(json.dumps(response).encode())

    monkeypatch.setattr(bcb_sgs, "urlopen", fake_urlopen)
    return windows, responses


def test_long_period_is_split_in_windows_of_ten_years(sgs):
    """Acima de 10 anos a API recusa: 25 anos viram três janelas contíguas."""
    windows, _ = sgs

    fetch_sgs(12, date(2000, 1, 1), date(2024, 12, 31))

    assert windows == [
        ("01/01/2000", "29/12/2009"),
        ("30/12/2009", "28/12/2019"),
        ("29/12/2019", "31/12/2024"),
    ]


def test_value_is_read_from_text_into_decimal(sgs):
    """O valor vira Decimal direto do texto, sem passar por float."""
    _, responses = sgs
    responses.append([{"data": "02/01/2020", "valor": "0.017089"}])

    rows = fetch_sgs(12, date(2020, 1, 1), date(2020, 1, 31))

    assert rows == [(date(2020, 1, 2), Decimal("0.017089"))]


def test_window_without_values_is_empty(sgs):
    """O SGS responde 404 para janela sem valor: a busca segue sem erro."""
    _, responses = sgs
    responses.append(HTTPError("url", 404, "Not Found", {}, None))  # type: ignore[arg-type]

    assert fetch_sgs(433, date(2030, 1, 1), date(2030, 2, 1)) == []


def test_month_split_between_windows_appears_once(sgs):
    """O IPCA do mês que as janelas dividem vem nas duas respostas e fica uma vez só."""
    _, responses = sgs
    december = {"data": "01/12/2009", "valor": "0.37"}
    responses += [[december], [december, {"data": "01/01/2010", "valor": "0.75"}]]

    rows = fetch_sgs(433, date(2000, 1, 1), date(2010, 2, 1))

    assert rows == [
        (date(2009, 12, 1), Decimal("0.37")),
        (date(2010, 1, 1), Decimal("0.75")),
    ]
