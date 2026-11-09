"""
Cliente do FRED (banco de dados do Federal Reserve de St. Louis), pelo CSV público do
gráfico, sem chave. A série DFF é a taxa efetiva do Fed Funds, o juro básico americano:
um valor por dia corrido, em % ao ano como o FRED publica.
"""

import csv
import io
from datetime import date, datetime
from decimal import Decimal
from urllib.request import Request, urlopen

from backend.features.import_data.bcb_sgs import TIMEOUT_SECONDS

FRED_URL = (
    "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
    "&cosd={start:%Y-%m-%d}&coed={end:%Y-%m-%d}"
)
FED_FUNDS_ID = "DFF"
# Dia sem observação no CSV do FRED
_MISSING = "."


def fetch_fed_funds(start: date, end: date) -> list[tuple[date, Decimal]]:
    """O Fed Funds em % ao ano em cada dia entre `start` e `end`."""
    request = Request(  # noqa: S310
        FRED_URL.format(series=FED_FUNDS_ID, start=start, end=end),
        headers={"Accept": "text/csv", "User-Agent": "SimuladorFinanceiro"},
    )
    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:  # noqa: S310
        return parse_fred_csv(response.read().decode("utf-8"))


def parse_fred_csv(text: str) -> list[tuple[date, Decimal]]:
    """As linhas (data, valor) do CSV do FRED; a primeira linha é o cabeçalho e o valor vira Decimal direto do texto."""
    rows = csv.reader(io.StringIO(text))
    next(rows, None)
    return [
        (datetime.strptime(day, "%Y-%m-%d").date(), Decimal(value))  # noqa: DTZ007
        for day, value in rows
        if value and value != _MISSING
    ]
