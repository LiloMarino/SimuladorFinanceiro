from __future__ import annotations

from datetime import datetime
from typing import Optional

import pandas as pd
import yfinance as yf

from backend.database import SessionLocal
from backend.logger_utils import setup_logger
from backend.models.models import Ativos, PrecoHistorico

logger = setup_logger(__name__)

# -------------------
# Origens de dados
# -------------------


def from_yfinance(
    ticker: str, start: Optional[str] = None, end: Optional[str] = None
) -> pd.DataFrame:
    logger.info(f"Baixando dados do YFinance para {ticker}...")
    df = yf.download(
        ticker,
        start=start,
        end=end or datetime.today().strftime("%Y-%m-%d"),
        auto_adjust=True,
        multi_level_index=False,
    )
    if df is None or df.empty:
        logger.warning(f"Nenhum dado retornado para {ticker}.")
        raise ValueError(f"Nenhum dado retornado para {ticker}.")
    return df


def from_csv(file) -> pd.DataFrame:
    logger.info(f"Lendo arquivo CSV '{file.filename}'...")
    df = pd.read_csv(file)
    return df


# -------------------
# Inserção no banco
# -------------------


def upsert_dataframe(
    df: pd.DataFrame, ticker: str, classe: str = "acao", overwrite: bool = False
):
    with SessionLocal() as session:
        # 1. Garante que o ativo existe
        ativo = session.query(Ativos).filter_by(ticker=ticker).first()
        if not ativo:
            ativo = Ativos(ticker=ticker, classe=classe)
            session.add(ativo)
            session.commit()
            logger.info(f"Ativo '{ticker}' criado no banco.")

        # 2. Lógica de sobrescrever
        if overwrite:
            logger.info(f"Sobrescrevendo dados de '{ticker}'...")
            session.query(PrecoHistorico).filter_by(ativos_id=ativo.ativos_id).delete()
            session.commit()

        # 3. Inserção incremental
        else:
            ultima_data = (
                session.query(PrecoHistorico)
                .filter_by(ativos_id=ativo.ativos_id)
                .order_by(PrecoHistorico.time.desc())
                .first()
            )
            if ultima_data:
                df = df[df.index > ultima_data.time]
                if df.empty:
                    logger.info(f"'{ticker}' já está atualizado.")
                    return

        # 4. Inserir dados no banco
        registros = [
            PrecoHistorico(
                ativos_id=ativo.ativos_id,
                time=index.to_pydatetime(),
                open=row["Open"],
                high=row["High"],
                low=row["Low"],
                close=row["Close"],
                volume=row["Volume"],
            )
            for index, row in df.iterrows()
        ]

        session.add_all(registros)
        session.commit()
        logger.info(f"{len(registros)} registros inseridos para '{ticker}'.")


# -------------------
# Funções finais do pipeline
# -------------------


def update_from_yfinance(ticker: str, overwrite: bool = False):
    try:
        df = from_yfinance(ticker)
        if not df.empty:
            upsert_dataframe(df, ticker, overwrite=overwrite)
    except Exception as e:
        logger.error(f"Erro ao baixar dados do YFinance: {str(e)}")
        raise


def update_from_csv(file, ticker: str, overwrite: bool = False):
    try:
        df = from_csv(file)
        if not df.empty:
            upsert_dataframe(df, ticker, overwrite=overwrite)
    except Exception as e:
        logger.error(f"Erro ao ler arquivo CSV: {str(e)}")
        raise
