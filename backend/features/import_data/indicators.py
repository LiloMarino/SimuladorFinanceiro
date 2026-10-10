"""
Atualização dos indicadores econômicos: CDI, SELIC e IPCA pelo SGS do Banco
Central e o Ibovespa pelo yfinance.
"""

import logging
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from functools import partial

import yfinance as yf

from backend.core import repository
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
            logger.info(f"{s.value}: busca recente, nada a fazer.")
            continue
        if not refresh_series(s, now):
            failed.append(s)
    return failed


def _attempted_recently(series: IndicatorSeries, now: datetime) -> bool:
    log = repository.economic.get_fetch_log(series)
    return log is not None and now - log.attempted_at < FETCH_INTERVAL


def refresh_series(series: IndicatorSeries, now: datetime) -> bool:
    """
    Busca a série do início (primeira carga) ou do dia 1 do mês do último valor
    guardado, que cobre revisões recentes. Falha mantém o que já está no banco.
    """
    source = INDICATOR_SOURCES[series]
    last = repository.economic.get_last_real_date(series)
    start = last.replace(day=1) if last else source.first_date

    succeeded = False
    try:
        rows = source.fetch(start, now.date())
        if rows:
            repository.economic.save_history(series, rows)
        succeeded = True
        logger.info(f"{series.value}: {len(rows)} valores desde {start:%d/%m/%Y}.")
    except Exception:
        logger.exception(f"{series.value}: falha na busca; o banco fica como está.")

    repository.economic.save_fetch_attempt(series, now, succeeded)
    return succeeded
