from __future__ import annotations

import logging
import re
from datetime import datetime

import pandas as pd
import yfinance as yf
from fastapi import UploadFile

from backend.core import repository
from backend.core.dto.sector import StockSegmentDTO
from backend.core.dto.ticker_profile import TickerProfileDTO, TickerSuggestionDTO
from backend.core.enum import AssetClass, DataOrigin
from backend.core.exceptions.http_exceptions import (
    BadGatewayError,
    NotFoundError,
    ServiceUnavailableError,
)
from backend.core.models.models import StockPriceHistory

logger = logging.getLogger(__name__)

# -------------------
# Origens de dados
# -------------------


def from_yfinance(
    ticker: str, start: str | None = None, end: str | None = None
) -> pd.DataFrame:
    if start:
        end = end or datetime.today().strftime("%Y-%m-%d")
        logger.debug(
            "Baixando dados do YFinance para %s de %s a %s", ticker, start, end
        )
        df = yf.download(
            ticker,
            start=start,
            end=end,
            auto_adjust=True,
            multi_level_index=False,
        )
    else:
        logger.debug("Baixando dados do YFinance para %s (período completo)", ticker)
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


def from_csv(file: UploadFile, fillzero: bool = True) -> pd.DataFrame:
    logger.debug("Lendo o arquivo CSV '%s'", file.filename)
    df = pd.read_csv(file.file)
    logger.debug(
        "CSV '%s': %s linhas, colunas %s", file.filename, len(df), list(df.columns)
    )

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


BDR_SUFFIXES = ("31", "32", "33", "34", "35", "39")


def _asset_class_by_suffix(ticker: str) -> AssetClass:
    """Pelo sufixo do código, com ou sem o `.SA` do yfinance: 11 é FII, 31 a 39 é BDR."""
    suffix = re.search(r"(\d+)(?:\.SA)?$", ticker, re.IGNORECASE)
    digits = suffix.group(1) if suffix else ""
    if digits.endswith(BDR_SUFFIXES):
        return AssetClass.BDR
    if digits.endswith("11"):
        return AssetClass.FII
    return AssetClass.STOCK


# Fundo imobiliário pelo nome: "FII ...", "Fundo de Investimento Imobiliário ..."
FII_NAME = re.compile(r"\bFII\b|fundo\s+(de\s+investimento\s+)?imobili", re.IGNORECASE)


def infer_asset_class(ticker: str, info: dict | None = None) -> AssetClass:
    """A classe vem do tipo que o yfinance devolve (`quoteType`): ETF é ETF e ação
    é ação, exceto fundo imobiliário (indústria REIT ou nome de fundo) e BDR (sufixo).
    Sem o dado do yfinance, vale o final do código. O usuário confere na Central de dados."""
    info = info or {}
    quote_type = str(info.get("quoteType") or "").upper()
    if quote_type == "ETF":
        return AssetClass.ETF
    if quote_type == "EQUITY":
        name = f"{info.get('longName') or ''} {info.get('shortName') or ''}"
        if str(info.get("industry") or "").upper().startswith(
            "REIT"
        ) or FII_NAME.search(name):
            return AssetClass.FII
        by_suffix = _asset_class_by_suffix(ticker)
        # Final 11 sem sinal de fundo imobiliário é unit de ação
        return AssetClass.STOCK if by_suffix == AssetClass.FII else by_suffix
    return _asset_class_by_suffix(ticker)


# Os 11 setores do yfinance, nos nomes em português da classificação da B3
YFINANCE_SECTORS = {
    "Basic Materials": "Materiais Básicos",
    "Communication Services": "Comunicações",
    "Consumer Cyclical": "Consumo Cíclico",
    "Consumer Defensive": "Consumo Não Cíclico",
    "Energy": "Petróleo, Gás e Biocombustíveis",
    "Financial Services": "Financeiro",
    "Healthcare": "Saúde",
    "Industrials": "Bens Industriais",
    "Real Estate": "Imobiliário",
    "Technology": "Tecnologia da Informação",
    "Utilities": "Utilidade Pública",
}


def suggest_segment(info: dict) -> StockSegmentDTO | None:
    """Setor e indústria do yfinance como sugestão de setor e segmento."""
    sector: str = info.get("sector") or ""
    if not sector:
        return None
    return StockSegmentDTO(
        sector=YFINANCE_SECTORS.get(sector) or sector,
        segment=info.get("industry") or sector,
    )


def _download_profile(ticker: str) -> TickerProfileDTO:
    """Consulta o yfinance; levanta quando a fonte falha."""
    info = yf.Ticker(ticker).info or {}
    return TickerProfileDTO(
        ticker=ticker,
        name=info.get("longName") or info.get("shortName"),
        quote_type=info.get("quoteType"),
        sector=info.get("sector"),
        industry=info.get("industry"),
    )


def _profile_to_info(profile: TickerProfileDTO) -> dict:
    return {
        "longName": profile.name,
        "quoteType": profile.quote_type,
        "sector": profile.sector,
        "industry": profile.industry,
    }


def fetch_info(ticker: str) -> dict:
    """O perfil do ativo: lê o guardado e só vai ao yfinance quando não há. A resposta
    vazia também é guardada; se a fonte falhar, nada é gravado e volta vazio."""
    if profile := repository.stock.get_ticker_profile(ticker):
        return _profile_to_info(profile)
    try:
        profile = _download_profile(ticker)
    except Exception as e:
        logger.warning(f"Não foi possível obter dados de '{ticker}' no yfinance: {e}")
        return {}
    repository.stock.save_ticker_profile(profile)
    return _profile_to_info(profile)


def refresh_profile(ticker: str) -> None:
    """Refaz a consulta ao yfinance e troca o perfil guardado."""
    try:
        profile = _download_profile(ticker)
    except Exception as e:
        logger.warning(f"Não foi possível obter dados de '{ticker}' no yfinance: {e}")
        raise BadGatewayError(
            f"Não foi possível buscar o perfil de {ticker} no yfinance."
        ) from e
    repository.stock.save_ticker_profile(profile)


# Código de ativo da B3: quatro caracteres e o número da classe (PETR4, KNRI11)
B3_TICKER = re.compile(r"[A-Z0-9]{4}\d{1,2}")


def search_tickers(query: str) -> list[TickerSuggestionDTO]:
    """Códigos da B3 que o yfinance acha para o texto, com o nome da empresa."""
    query = query.strip()
    if len(query) < 2:
        return []
    try:
        quotes = yf.Search(query, max_results=20, news_count=0, lists_count=0).quotes
    except Exception as e:
        logger.warning(f"Não foi possível buscar '{query}' no yfinance: {e}")
        raise ServiceUnavailableError(
            "A busca de códigos está indisponível. Digite o código à mão."
        ) from e

    found: dict[str, TickerSuggestionDTO] = {}
    for quote in quotes:
        symbol = str(quote.get("symbol") or "").upper()
        if quote.get("exchange") != "SAO" or not symbol.endswith(".SA"):
            continue
        ticker = symbol.removesuffix(".SA")
        if not B3_TICKER.fullmatch(ticker) or ticker in found:
            continue
        name = quote.get("longname") or quote.get("shortname") or ticker
        found[ticker] = TickerSuggestionDTO(ticker=ticker, name=name)
    return list(found.values())


def upsert_dataframe(df: pd.DataFrame, ticker: str, overwrite: bool = False):
    # 1. Garante que o ativo existe e, enquanto não tiver classificação, sugere a
    # do yfinance; a que o usuário escolheu na Central de dados fica como está
    stock = repository.stock.get_by_ticker(ticker)
    classified = stock is not None and ticker in repository.stock.get_classification()
    info = {} if classified else fetch_info(ticker)

    if not stock:
        nome = info.get("longName") or info.get("shortName") or ticker
        asset_class = infer_asset_class(ticker, info)
        stock = repository.stock.add_stock(ticker, nome, asset_class)
        logger.info(
            f"Ativo '{ticker}' ({nome}) criado no banco como {asset_class.value}."
        )

    if not classified and (segment := suggest_segment(info)):
        repository.stock.classify(ticker, segment)

    # 2. Lógica de sobrescrever
    if overwrite:
        logger.debug("Sobrescrevendo os dados de '%s'", ticker)
        repository.stock.delete_stock_price_history(stock.id)

    # 3. Inserção incremental
    else:
        last_date = repository.stock.get_last_stock_price_history(stock.id)
        if last_date:
            df = pd.DataFrame(df[df.index > pd.Timestamp(last_date.price_date)])
            if df.empty:
                logger.debug("'%s' já está atualizado.", ticker)
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
            origin=DataOrigin.REAL.value,
        )
        for index, row in df.iterrows()
    ]

    repository.stock.add_stock_price_history(registros)
    logger.info("%s registros inseridos para '%s'.", len(registros), ticker)


# -------------------
# Funções finais do pipeline
# -------------------


def from_yfinance_batch(tickers: list[str]) -> dict[str, pd.DataFrame]:
    if not tickers:
        return {}
    if len(tickers) == 1:
        return {tickers[0]: from_yfinance(tickers[0])}

    logger.info(f"Baixando dados em lote do YFinance para: {', '.join(tickers)}")
    df = yf.download(
        tickers,
        period="max",
        group_by="ticker",
        auto_adjust=True,
    )

    if df is None:
        return {}

    result = {}
    for ticker in tickers:
        try:
            ticker_df = df[ticker].dropna(how="all")
            if not ticker_df.empty:
                result[ticker] = ticker_df
            else:
                logger.warning(f"Nenhum dado retornado para {ticker} no lote.")
        except KeyError:
            logger.warning(f"Ticker '{ticker}' não encontrado no resultado do lote.")

    return result


def update_from_yfinance_batch(tickers: list[str], overwrite: bool = False):
    try:
        batch = from_yfinance_batch(tickers)
        for ticker, df in batch.items():
            upsert_dataframe(df, ticker, overwrite=overwrite)
    except Exception:
        logger.exception("Erro ao baixar dados em lote do YFinance")
        raise


def update_from_yfinance(ticker: str, overwrite: bool = False):
    try:
        df = from_yfinance(ticker)
        if not df.empty:
            upsert_dataframe(df, ticker, overwrite=overwrite)
    except Exception:
        logger.exception("Erro ao baixar dados do YFinance")
        raise


def update_from_csv(file: UploadFile, ticker: str, overwrite: bool = False):
    try:
        df = from_csv(file)
        if not df.empty:
            upsert_dataframe(df, ticker, overwrite=overwrite)
    except Exception:
        logger.exception("Erro ao ler arquivo CSV")
        raise
