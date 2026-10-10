"""Cliente da API SGS (Sistema Gerenciador de Séries Temporais) do Banco Central."""

import json
from datetime import date, datetime, timedelta
from decimal import Decimal
from urllib.error import HTTPError
from urllib.request import Request, urlopen

SGS_URL = (
    "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados"
    "?formato=json&dataInicial={start:%d/%m/%Y}&dataFinal={end:%d/%m/%Y}"
)
# A API recusa consultas acima de 10 anos
MAX_WINDOW = timedelta(days=3650)
TIMEOUT_SECONDS = 30


def fetch_sgs(code: int, start: date, end: date) -> list[tuple[date, Decimal]]:
    """Valores da série `code` entre `start` e `end`, em janelas de até 10 anos."""
    # Série mensal vem datada no dia 1 e aparece nas duas janelas que dividem o mês
    rows: dict[date, Decimal] = {}
    window_start = start
    while window_start <= end:
        window_end = min(window_start + MAX_WINDOW, end)
        rows.update(_fetch_window(code, window_start, window_end))
        window_start = window_end + timedelta(days=1)
    return sorted(rows.items())


def _fetch_window(code: int, start: date, end: date) -> list[tuple[date, Decimal]]:
    request = Request(
        SGS_URL.format(code=code, start=start, end=end),
        headers={"Accept": "application/json", "User-Agent": "SimuladorFinanceiro"},
    )
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            payload = json.load(response)
    except HTTPError as error:
        # O SGS responde 404 quando a janela não tem nenhum valor
        if error.code == 404:
            return []
        raise

    # O valor vem como texto ("0.055131") e vira Decimal sem passar por float
    return [
        (datetime.strptime(item["data"], "%d/%m/%Y").date(), Decimal(item["valor"]))
        for item in payload
    ]
