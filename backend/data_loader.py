from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import pandas as pd
import yfinance as yf

from backend.database import SessionLocal
from backend.logger_utils import setup_logger
from backend.models.models import Ativos, PrecoHistorico

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = setup_logger(__name__)


def importar_ativo(session: Session, ticker: str, classe: str = "acao") -> Ativos:
    ativo = session.query(Ativos).filter_by(ticker=ticker).first()

    if ativo:
        logger.info(f"Ativo '{ticker}' já existe no banco.")
        return ativo

    novo_ativo = Ativos(ticker=ticker, classe=classe)
    session.add(novo_ativo)
    session.commit()
    logger.info(f"Ativo '{ticker}' importado com sucesso.")

    return novo_ativo


def atualizar_ativo(ticker: str):
    logger.info(f"Atualizando dados do ativo '{ticker}'")
    with SessionLocal() as session:
        ativo = importar_ativo(session, ticker)

        # Buscar a última data registrada
        ultima_data = (
            session.query(PrecoHistorico)
            .filter_by(ativos_id=ativo.ativos_id)
            .order_by(PrecoHistorico.time.desc())
            .first()
        )

        # Definir a data de hoje
        hoje = datetime.today().date()

        # Verificar se já existem dados anteriores
        if ultima_data:
            data_inicio = ultima_data.time + timedelta(days=1)
            if data_inicio.date() > hoje:
                logger.info("Dados já estão atualizados.")
                return
            start_str = data_inicio.strftime("%Y-%m-%d")
            logger.info(f"Buscando dados de {data_inicio.date()} até {hoje}")
        else:
            # Sem dados prévios, buscar desde o início
            start_str = None
            logger.info(f"Buscando dados desde o início até {hoje}")

        # Baixar os dados
        df = yf.download(
            ticker,
            start=start_str,
            end=hoje.strftime("%Y-%m-%d"),
            auto_adjust=True,
            multi_level_index=False,
        )

        for index, row in df.iterrows():
            registro = PrecoHistorico(
                ativos_id=ativo.ativos_id,
                time=index.to_pydatetime(),
                open=row["Open"],
                high=row["High"],
                low=row["Low"],
                close=row["Close"],
                volume=row["Volume"],
                openinterest=None,
            )
            session.add(registro)

        session.commit()
        logger.info(f"Dados de '{ticker}' atualizados com sucesso.")
