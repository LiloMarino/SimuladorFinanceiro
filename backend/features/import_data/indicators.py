"""
Atualização dos indicadores econômicos: CDI, SELIC, IPCA e PTAX (o dólar) pelo SGS
do Banco Central e o Ibovespa pelo yfinance. O crescimento do PIB e o desemprego são do
IBGE e chegam pelo mesmo SGS, que os republica.
"""

import logging
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from functools import partial

import yfinance as yf

from backend.core import repository
from backend.core.dto.generated_future import ReplacedGeneratedDTO
from backend.core.enum import IndicatorSeries
from backend.features.import_data.bcb_sgs import fetch_sgs

logger = logging.getLogger(__name__)

# Intervalo entre tentativas automáticas; a falha também conta como tentativa
FETCH_INTERVAL = timedelta(hours=6)


def fetch_ibov(start: date, end: date) -> list[tuple[date, Decimal]]:
    """Fechamento diário do Ibovespa entre `start` e `end`."""
    df = yf.download(
        "^BVSP",
        start=start.isoformat(),
        end=(end + timedelta(days=1)).isoformat(),
        auto_adjust=True,
        multi_level_index=False,
        progress=False,
    )
    if df is None or df.empty:
        return []
    return [
        (date.fromisoformat(str(timestamp)[:10]), Decimal(str(close)))
        for timestamp, close in df["Close"].dropna().items()
    ]


# Índice do PIB real trimestral do IBGE (1995 = 100, sem ajuste sazonal), no SGS desde 1996
GDP_INDEX_SGS = 22099
GDP_INDEX_START = date(1996, 1, 1)
QUARTERS_PER_YEAR = 4
# Taxa de desocupação da PNAD Contínua: % da força de trabalho, trimestre móvel datado no último mês
UNEMPLOYMENT_SGS = 24369
# Dólar comercial (venda), a PTAX; o real nasce em 01/07/1994, antes disso a série é de outras moedas
PTAX_SGS = 1


def gdp_growth(index: list[tuple[date, Decimal]]) -> list[tuple[date, Decimal]]:
    """
    Crescimento real em 4 trimestres, em %: a soma dos 4 últimos trimestres do índice
    contra a dos 4 anteriores, como o IBGE divulga o "PIB acumulado em 4 trimestres".
    Datado no dia 1 do trimestre que fecha a conta.
    """
    values = [value for _, value in index]
    rows = []
    for i in range(2 * QUARTERS_PER_YEAR - 1, len(values)):
        last = sum(values[i - QUARTERS_PER_YEAR + 1 : i + 1], Decimal(0))
        before = sum(
            values[i - 2 * QUARTERS_PER_YEAR + 1 : i - QUARTERS_PER_YEAR + 1],
            Decimal(0),
        )
        rows.append(
            (index[i][0], ((last / before - 1) * 100).quantize(Decimal("0.01")))
        )
    return rows


def fetch_gdp_growth(start: date, end: date) -> list[tuple[date, Decimal]]:
    """O crescimento de cada trimestre entre `start` e `end`; o índice vem inteiro, porque a conta pede os 8 trimestres anteriores."""
    index = fetch_sgs(GDP_INDEX_SGS, GDP_INDEX_START, end)
    return [(day, value) for day, value in gdp_growth(index) if day >= start]


@dataclass(frozen=True)
class IndicatorSource:
    name: str
    first_date: date
    fetch: Callable[[date, date], list[tuple[date, Decimal]]]


INDICATOR_SOURCES: dict[IndicatorSeries, IndicatorSource] = {
    IndicatorSeries.CDI: IndicatorSource(
        "CDI", date(1986, 3, 6), partial(fetch_sgs, 12)
    ),
    IndicatorSeries.SELIC: IndicatorSource(
        "SELIC", date(1986, 6, 4), partial(fetch_sgs, 11)
    ),
    IndicatorSeries.IPCA: IndicatorSource(
        "IPCA", date(1980, 1, 1), partial(fetch_sgs, 433)
    ),
    IndicatorSeries.IBOV: IndicatorSource("Ibovespa", date(1993, 4, 27), fetch_ibov),
    IndicatorSeries.GDP_GROWTH: IndicatorSource(
        "PIB (crescimento em 4 trimestres)", date(1997, 10, 1), fetch_gdp_growth
    ),
    IndicatorSeries.UNEMPLOYMENT: IndicatorSource(
        "Desemprego (PNAD Contínua)",
        date(2012, 3, 1),
        partial(fetch_sgs, UNEMPLOYMENT_SGS),
    ),
    IndicatorSeries.PTAX: IndicatorSource(
        "PTAX (dólar)", date(1994, 7, 1), partial(fetch_sgs, PTAX_SGS)
    ),
}


def refresh_indicators(
    series: Iterable[IndicatorSeries] | None = None, force: bool = False
) -> list[IndicatorSeries]:
    """
    Busca o que falta de cada série e devolve as que falharam.

    Sem `force`, a série buscada há menos de 6 horas fica como está.
    """
    now = datetime.now(UTC)
    failed = []
    for s in series or INDICATOR_SOURCES:
        if not force and _attempted_recently(s, now):
            logger.debug("%s: busca recente, nada a fazer.", s.value)
            continue
        if not refresh_series(s, now).succeeded:
            failed.append(s)
    return failed


def _attempted_recently(series: IndicatorSeries, now: datetime) -> bool:
    log = repository.economic.get_fetch_log(series)
    return log is not None and now - log.attempted_at < FETCH_INTERVAL


@dataclass(frozen=True)
class SeriesRefresh:
    succeeded: bool
    # Dias gerados que o real que chegou ocupou
    replaced: ReplacedGeneratedDTO | None = None


def refresh_series(series: IndicatorSeries, now: datetime) -> SeriesRefresh:
    """
    Busca a série do início (primeira carga) ou do dia 1 do mês do último valor
    real guardado, que cobre revisões recentes. Falha mantém o que já está no banco.
    """
    source = INDICATOR_SOURCES[series]
    last = repository.economic.get_last_real_date(series)
    start = last.replace(day=1) if last else source.first_date

    succeeded = False
    replaced = None
    try:
        rows = source.fetch(start, now.date())
        if rows:
            replaced = repository.economic.save_history(series, rows)
        succeeded = True
        logger.info(
            "%s: %s valores desde %s.", series.value, len(rows), f"{start:%d/%m/%Y}"
        )
    except Exception:
        logger.exception("%s: falha na busca; o banco fica como está.", series.value)

    repository.economic.save_fetch_attempt(series, now, succeeded)
    return SeriesRefresh(succeeded, replaced)
