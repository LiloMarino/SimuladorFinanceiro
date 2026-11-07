"""
Preço bruto e eventos corporativos (desdobramentos e dividendos) da importação.

O yfinance devolve o histórico ajustado por desdobramento: o preço de antes de
um 2:1 vem dividido por dois. A partida joga o preço que o mercado negociou, e
o desdobramento chega como evento na data ex. Aqui o preço ajustado volta ao
bruto e as colunas de ação do yfinance viram os eventos.
"""

import numpy as np
import pandas as pd

from backend.core.dto.corporate_event import CorporateEventDTO
from backend.core.enum import CorporateEventKind

DIVIDENDS = "Dividends"
SPLITS = "Stock Splits"
PRICE_COLUMNS = ["Open", "High", "Low", "Close"]
# Preço negocia em centavos: o produto pelo fator só carrega ruído de ponto flutuante
PRICE_DECIMALS = 2
DIVIDEND_DECIMALS = 6


def has_actions(df: pd.DataFrame) -> bool:
    """O quadro traz as colunas de eventos (o CSV não traz)."""
    return DIVIDENDS in df.columns and SPLITS in df.columns


def to_raw_prices(df: pd.DataFrame) -> pd.DataFrame:
    """
    Desfaz o ajuste de desdobramento do histórico completo: cada pregão e cada
    dividendo é multiplicado pelo produto das razões dos desdobramentos com data
    ex posterior a ele, e o volume é dividido por esse mesmo fator. O pregão da
    própria data ex já negocia depois do desdobramento e fica como veio.
    """
    if df.empty or not has_actions(df):
        return df
    ratios = df[SPLITS].fillna(0.0).to_numpy(dtype=float)
    ratios = np.where(ratios > 0, ratios, 1.0)
    # Produto das razões de cada dia em diante, deslocado um dia: só as posteriores
    after = np.append(np.cumprod(ratios[::-1])[::-1][1:], 1.0)
    changed = after != 1.0

    raw = df.copy()
    for column in PRICE_COLUMNS:
        values = raw[column].to_numpy(dtype=float)
        raw[column] = np.where(
            changed, np.round(values * after, PRICE_DECIMALS), values
        )
    volume = raw["Volume"].to_numpy(dtype=float)
    raw["Volume"] = np.where(changed, np.round(volume / after), volume)
    dividends = raw[DIVIDENDS].fillna(0.0).to_numpy(dtype=float)
    raw[DIVIDENDS] = np.round(dividends * after, DIVIDEND_DECIMALS)
    return raw


def events_from_frame(df: pd.DataFrame, stock_id: int) -> list[CorporateEventDTO]:
    """Os desdobramentos e os dividendos do quadro de preço bruto, por data ex."""
    if df.empty or not has_actions(df):
        return []
    events: list[CorporateEventDTO] = []
    for day, ratio, dividend in zip(
        df.index.to_numpy().astype("datetime64[D]").tolist(),
        df[SPLITS].fillna(0.0),
        df[DIVIDENDS].fillna(0.0),
        strict=True,
    ):
        if ratio > 0 and ratio != 1:
            events.append(
                CorporateEventDTO(
                    stock_id=stock_id,
                    ex_date=day,
                    kind=CorporateEventKind.SPLIT,
                    value=float(ratio),
                )
            )
        if dividend > 0:
            events.append(
                CorporateEventDTO(
                    stock_id=stock_id,
                    ex_date=day,
                    kind=CorporateEventKind.DIVIDEND,
                    value=float(dividend),
                )
            )
    return events
