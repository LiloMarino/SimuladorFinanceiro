"""
Cliente do Focus, a pesquisa semanal do Banco Central com as projeções do mercado
(API de expectativas, em OData). Cada série guarda a mediana das projeções, um valor por
dia de pesquisa, em % como publicada.
"""

import json
import re
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any
from urllib.parse import quote
from urllib.request import Request, urlopen

from backend.features.import_data.bcb_sgs import MAX_WINDOW, TIMEOUT_SECONDS

FOCUS_URL = (
    "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/{resource}"
)
# Teto de linhas por resposta da API
PAGE_SIZE = 100_000
# A mediana da pesquisa inteira, sem o recorte das respostas dos últimos 5 dias úteis
FULL_SURVEY = 0
_MEETING = re.compile(r"R(\d+)/(\d{4})")


def fetch_focus_selic(start: date, end: date) -> list[tuple[date, Decimal]]:
    """A SELIC que o mercado espera para a próxima reunião do Copom, em cada dia de pesquisa."""
    rows = _fetch_all("ExpectativasMercadoSelic", start, end, ["Reuniao"])
    next_meeting: dict[date, tuple[tuple[int, int], Decimal]] = {}
    for row in rows:
        match = _MEETING.fullmatch(row["Reuniao"])
        if match is None:
            continue
        order = (int(match.group(2)), int(match.group(1)))
        day = _day(row)
        if day not in next_meeting or order < next_meeting[day][0]:
            next_meeting[day] = (order, row["Mediana"])
    return sorted((day, value) for day, (_, value) in next_meeting.items())


def fetch_focus_ipca(start: date, end: date) -> list[tuple[date, Decimal]]:
    """O IPCA dos próximos 12 meses que o mercado espera (série suavizada)."""
    rows = _fetch_all(
        "ExpectativasMercadoInflacao12Meses",
        start,
        end,
        [],
        "Indicador eq 'IPCA' and Suavizada eq 'S'",
    )
    return sorted((_day(row), row["Mediana"]) for row in rows)


def fetch_focus_annual(
    indicator: str, start: date, end: date
) -> list[tuple[date, Decimal]]:
    """A projeção do `indicator` (PIB Total, Câmbio) para o ano da própria pesquisa."""
    rows = _fetch_all(
        "ExpectativasMercadoAnuais",
        start,
        end,
        ["DataReferencia"],
        f"Indicador eq '{indicator}'",
    )
    return sorted(
        (_day(row), row["Mediana"])
        for row in rows
        if row["DataReferencia"] == str(_day(row).year)
    )


def _day(row: dict[str, Any]) -> date:
    return datetime.strptime(row["Data"], "%Y-%m-%d").date()  # noqa: DTZ007


def _fetch_all(
    resource: str,
    start: date,
    end: date,
    extra_fields: list[str],
    extra_filter: str = "",
) -> list[dict[str, Any]]:
    """As linhas entre `start` e `end`, em janelas de até 10 anos."""
    rows: list[dict[str, Any]] = []
    window_start = start
    while window_start <= end:
        window_end = min(window_start + MAX_WINDOW, end)
        rows.extend(
            _fetch_window(
                resource, window_start, window_end, extra_fields, extra_filter
            )
        )
        window_start = window_end + timedelta(days=1)
    return rows


def _fetch_window(
    resource: str,
    start: date,
    end: date,
    extra_fields: list[str],
    extra_filter: str,
) -> list[dict[str, Any]]:
    conditions = [
        f"baseCalculo eq {FULL_SURVEY}",
        f"Data ge '{start.isoformat()}'",
        f"Data le '{end.isoformat()}'",
    ]
    if extra_filter:
        conditions.append(extra_filter)
    fields = ",".join(["Data", "Mediana", *extra_fields])
    query = (
        f"?$format=json&$top={PAGE_SIZE}"
        f"&$select={fields}"
        f"&$filter={quote(' and '.join(conditions), safe='')}"
    )
    request = Request(  # noqa: S310
        FOCUS_URL.format(resource=resource) + query,
        headers={"Accept": "application/json", "User-Agent": "SimuladorFinanceiro"},
    )
    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:  # noqa: S310
        # A mediana vem como número JSON e vira Decimal direto do texto
        payload = json.load(response, parse_float=Decimal)
    return [
        {**row, "Mediana": Decimal(row["Mediana"])}
        for row in payload["value"]
        if row.get("Mediana") is not None
    ]
