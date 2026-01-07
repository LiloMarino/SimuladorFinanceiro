from __future__ import annotations

from datetime import datetime

import pandas as pd
import yfinance as yf

from backend.core import repository
from backend.core.exceptions.http_exceptions import NotFoundError
from backend.core.logger import setup_logger
from backend.core.models.models import StockPriceHistory

logger = setup_logger(__name__)

# -------------------
# Origens de dados
# -------------------


def from_yfinance(
    ticker: str, start: str | None = None, end: str | None = None
) -> pd.DataFrame:
    if start:
        logger.info(
            f"Baixando dados do YFinance para {ticker} de {start} a {end or datetime.today().strftime('%Y-%m-%d')}"
        )
        df = yf.download(
            ticker,
            start=start,
            end=end or datetime.today().strftime("%Y-%m-%d"),
            auto_adjust=True,
            multi_level_index=False,
        )
    else:
        logger.info(f"Baixando dados do YFinance para {ticker} (Periodo completo)")
        df = yf.download(
            ticker,
            period="max",
            auto_adjust=True,
            multi_level_index=False,
        )
    if df is None or df.empty:
        logger.warning(f"Nenhum dado retornado para {ticker}.")
        raise NotFoundError(f"Nenhum dado retornado para {ticker}.")
    return df


def from_csv(file, fillzero: bool = True) -> pd.DataFrame:
    logger.info(f"Lendo arquivo CSV '{file.filename}'...")
    df = pd.read_csv(file)

    # Converte datas (formato dd.mm.yyyy → datetime)
    df["Data"] = pd.to_datetime(df["Data"], format="%d.%m.%Y", errors="coerce")

    # Renomeia colunas para inglês (o que seu código espera)
    df = df.rename(
        columns={
            "Último": "Close",
            "Abertura": "Open",
            "Máxima": "High",
            "Mínima": "Low",
            "Vol.": "Volume",
        }
    )

    # Remove % e converte para número
    for col in ["Close", "Open", "High", "Low"]:
        df[col] = df[col].astype(str).str.replace(",", ".").astype(float)

    # Trata volume (tipo "28,59K")
    def parse_vol(x):
        x = str(x).replace(".", "").replace(",", ".")
        if "K" in x:
            return float(x.replace("K", "")) * 1000
        if "M" in x:
            return float(x.replace("M", "")) * 1_000_000
        return float(x)

    df["Volume"] = df["Volume"].apply(parse_vol)

    # Trata valores ausentes
    if fillzero:
        missing_before = (
            df[["Open", "High", "Low", "Close", "Volume"]].isna().sum().sum()
        )
        df = df.fillna(0)
        if missing_before > 0:
            logger.warning(
                f"{missing_before} valores ausentes foram preenchidos com zero!"
            )
    else:
        df = df.dropna(subset=["Open", "High", "Low", "Close", "Volume"])

    # Coloca Data como índice
    df = df.set_index("Data")

    return df


# -------------------
# Inserção no banco
# -------------------


def upsert_dataframe(df: pd.DataFrame, ticker: str, overwrite: bool = False):
    # 1. Garante que o ativo existe
    stock = repository.stock.get_by_ticker(ticker)
    if not stock:
        try:
            yf_ticker = yf.Ticker(ticker)
            info = yf_ticker.info
            nome = info.get("longName") or info.get("shortName") or ticker
        except Exception as e:
            logger.warning(
                f"Não foi possível obter nome de '{ticker}' no yfinance: {e}"
            )
            nome = ticker

        stock = repository.stock.add_stock(ticker, nome)
        logger.info(f"Ativo '{ticker}' ({nome}) criado no banco.")

    # 2. Lógica de sobrescrever
    if overwrite:
        logger.info(f"Sobrescrevendo dados de '{ticker}'...")
        repository.stock.delete_stock_price_history(stock.id)

    # 3. Inserção incremental
    else:
        last_date = repository.stock.get_last_stock_price_history(stock.id)
        if last_date:
            df = pd.DataFrame(df[df.index > last_date.price_date])
            if df.empty:
                logger.info(f"'{ticker}' já está atualizado.")
                return

    # 4. Inserir dados no banco
    registros = [
        StockPriceHistory(
            stock_id=stock.id,
            price_date=index,
            open=row["Open"],
            high=row["High"],
            low=row["Low"],
            close=row["Close"],
            volume=row["Volume"],
        )
        for index, row in df.iterrows()
    ]

    repository.stock.add_stock_price_history(registros)
    logger.info(f"{len(registros)} registros inseridos para '{ticker}'.")


# -------------------
# Funções finais do pipeline
# -------------------


def update_from_yfinance(ticker: str, overwrite: bool = False):
    try:
        df = from_yfinance(ticker)
        if not df.empty:
            upsert_dataframe(df, ticker, overwrite=overwrite)
    except Exception:
        logger.exception("Erro ao baixar dados do YFinance")
        raise


def update_from_csv(file, ticker: str, overwrite: bool = False):
    try:
        df = from_csv(file)
        if not df.empty:
            upsert_dataframe(df, ticker, overwrite=overwrite)
    except Exception:
        logger.exception("Erro ao ler arquivo CSV")
        raise
