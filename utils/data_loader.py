import backtrader as bt
import pandas as pd
import yfinance as yf


class StockData(bt.feeds.PandasData):
    params = (
        ("datetime", None),
        ("open", -1),
        ("high", -1),
        ("low", -1),
        ("close", -1),
        ("volume", -1),
        ("openinterest", -1),
    )


def get_stock_data(ticker, start="2020-01-01", end="2024-01-01"):
    """Baixa dados históricos de ações usando Yahoo Finance e ajusta as colunas"""
    df = yf.download(ticker, start=start, end=end)

    # Garantir que os nomes das colunas estejam no formato esperado pelo Backtrader
    df = df[["Open", "High", "Low", "Close", "Volume"]]
    df.columns = ["open", "high", "low", "close", "volume"]

    df.index = pd.to_datetime(df.index)
    return df
