"""
Conversão para real do preço dos ativos que o Yahoo cota em dólar.

A partida joga em real. O ativo em dólar entra na base já convertido pela PTAX de
cada dia, e o desdobramento, que é só uma razão, fica como veio.
"""

import pandas as pd

from backend.core import repository
from backend.core.enum import Currency, IndicatorSeries
from backend.core.exceptions.http_exceptions import ServiceUnavailableError
from backend.features.import_data.corporate_events import (
    DIVIDEND_DECIMALS,
    DIVIDENDS,
    PRICE_COLUMNS,
    PRICE_DECIMALS,
)
from backend.features.import_data.indicators import refresh_indicators


def ptax_by_day() -> pd.Series:
    """
    A PTAX guardada, atualizada antes de ler (a busca recente é reaproveitada). A
    falha da fonte só impede a conversão quando não há PTAX nenhuma na base.
    """
    refresh_indicators([IndicatorSeries.PTAX])
    history = repository.economic.get_history(IndicatorSeries.PTAX, stored=True)
    if not history.dates:
        raise ServiceUnavailableError(
            "Não foi possível obter a PTAX no Banco Central para converter o preço "
            "do dólar em real. Tente de novo mais tarde."
        )
    return pd.Series(
        [float(history.values[day]) for day in history.dates],
        index=pd.DatetimeIndex(history.dates),
    )


def to_brl(df: pd.DataFrame, currency: Currency, ptax: pd.Series) -> pd.DataFrame:
    """
    Preço e dividendo vezes a PTAX do dia; fim de semana e feriado usam a última PTAX
    publicada. Os pregões de antes da primeira PTAX saem do quadro.
    """
    if currency is Currency.BRL or df.empty:
        return df
    rates = ptax.reindex(df.index, method="ffill").dropna()
    priced = pd.DataFrame(df.loc[rates.index]).copy()
    for column in PRICE_COLUMNS:
        priced[column] = (pd.Series(priced[column]) * rates).round(PRICE_DECIMALS)
    if DIVIDENDS in priced.columns:
        dividends = pd.Series(priced[DIVIDENDS]).fillna(0.0)
        priced[DIVIDENDS] = (dividends * rates).round(DIVIDEND_DECIMALS)
    return priced
