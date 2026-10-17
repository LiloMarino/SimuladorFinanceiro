from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from pydantic import BaseModel, Field

from backend.core import repository
from backend.core.dependencies.simulation import require_no_active_simulation
from backend.core.dto.sector import SectorDTO, StockSegmentDTO
from backend.core.dto.series_coverage import SeriesCoverageDTO
from backend.core.dto.ticker_profile import TickerSuggestionDTO
from backend.core.enum import AssetClass, IndicatorSeries
from backend.core.exceptions.http_exceptions import BadGatewayError, NotFoundError
from backend.features.import_data.coverage import get_series_coverage
from backend.features.import_data.importer_service import (
    fetch_info,
    refresh_profile,
    search_tickers,
    suggest_segment,
    update_from_csv,
    update_from_yfinance,
    update_from_yfinance_batch,
)
from backend.features.import_data.indicators import refresh_indicators

import_router = APIRouter(
    prefix="/api/import-assets",
    tags=["Import Assets"],
    dependencies=[Depends(require_no_active_simulation)],
)


@import_router.get(
    "/coverage",
    response_model=list[SeriesCoverageDTO],
    summary="Cobertura das séries",
    description="Retorna cada série da base (indicadores e ações) com o início, o fim do dado real e o fim do dado gerado.",
)
def get_coverage():
    return get_series_coverage()


def refresh_or_raise(series: list[IndicatorSeries] | None) -> None:
    failed = refresh_indicators(series, force=True)
    if failed:
        raise BadGatewayError(
            f"Não foi possível buscar {', '.join(s.value for s in failed)}. "
            "O que já estava no banco foi mantido."
        )


@import_router.post(
    "/indicators",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Atualizar todos os indicadores",
    description="Busca CDI, SELIC e IPCA no Banco Central e o Ibovespa no yfinance, a partir do último valor guardado.",
)
def refresh_all_indicators():
    refresh_or_raise(None)


@import_router.post(
    "/indicators/{series}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Atualizar um indicador",
    description="Busca um indicador a partir do último valor guardado.",
)
def refresh_one_indicator(series: IndicatorSeries):
    refresh_or_raise([series])


class AssetClassRequest(BaseModel):
    asset_class: AssetClass


@import_router.put(
    "/stocks/{ticker}/asset-class",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Alterar a classe de um ativo",
    description="Define se o ativo é ação, FII, ETF ou BDR, o que decide a alíquota e a isenção do IR na venda.",
)
def update_asset_class(ticker: str, request: AssetClassRequest):
    if repository.stock.set_asset_class(ticker, request.asset_class) is None:
        raise NotFoundError(f"Ativo '{ticker}' não encontrado.")


class StockSegmentRequest(BaseModel):
    sector: str = Field(min_length=1)
    segment: str = Field(min_length=1)


@import_router.put(
    "/stocks/{ticker}/segment",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Classificar um ativo por setor e segmento",
    description="Põe o ativo no setor e segmento informados, criando-os pelo nome quando ainda não existem.",
)
def update_segment(ticker: str, request: StockSegmentRequest):
    segment = StockSegmentDTO(
        sector=request.sector.strip(), segment=request.segment.strip()
    )
    if repository.stock.classify(ticker, segment) is None:
        raise NotFoundError(f"Ativo '{ticker}' não encontrado.")


@import_router.delete(
    "/stocks/{ticker}/segment",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover a classificação de um ativo",
    description="Tira o ativo do setor e do segmento; ele passa a aparecer como sem setor.",
)
def delete_segment(ticker: str):
    if repository.stock.classify(ticker, None) is None:
        raise NotFoundError(f"Ativo '{ticker}' não encontrado.")


@import_router.get(
    "/sectors",
    response_model=list[SectorDTO],
    summary="Setores e segmentos",
    description="Retorna os setores em uso, cada um com os seus segmentos, para sugerir na classificação.",
)
def get_sectors():
    return repository.stock.get_sectors()


def str_to_bool(value: str | bool | None) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on")
    return False


class ImportYFinanceRequest(BaseModel):
    ticker: str
    overwrite: bool = False


def imported_series(ticker: str) -> SeriesCoverageDTO:
    """A série como ficou na base depois da importação; sem pregão nenhum, a fonte não tinha dado."""
    series = next((s for s in get_series_coverage() if s.key == ticker), None)
    if series is None or series.start is None:
        raise NotFoundError(
            f"Nenhum pregão de {ticker} veio da fonte: confira o código."
        )
    return series


@import_router.post(
    "/yfinance",
    response_model=SeriesCoverageDTO,
    summary="Importar dados de yfinance",
    description="Importa dados de ativos do yfinance para um ticker especificado e devolve a série como ficou na base.",
)
def import_assets_json(request: ImportYFinanceRequest):
    """
    Importa dados de ativos do yfinance.
    """
    update_from_yfinance(request.ticker, request.overwrite)
    return imported_series(request.ticker)


class ImportYFinanceBatchRequest(BaseModel):
    tickers: list[str]
    overwrite: bool = False


@import_router.post(
    "/yfinance/batch",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Importar dados de múltiplos ativos via yfinance",
    description="Baixa dados de vários ativos em uma única chamada ao yfinance.",
)
def import_assets_batch(request: ImportYFinanceBatchRequest):
    update_from_yfinance_batch(request.tickers, request.overwrite)


@import_router.post(
    "/csv",
    response_model=SeriesCoverageDTO,
    summary="Importar dados de CSV",
    description="Importa dados de ativos a partir de um arquivo CSV enviado via multipart/form-data e devolve a série como ficou na base.",
)
def import_assets_csv(
    ticker: Annotated[str, Form(...)],
    csv_file: Annotated[UploadFile, File(...)],
    overwrite: Annotated[str, Form(...)] = "false",
):
    """
    Importa dados de ativos de um arquivo CSV.
    """
    update_from_csv(csv_file, ticker, str_to_bool(overwrite))
    return imported_series(ticker)


@import_router.get(
    "/stocks/{ticker}/suggestion",
    response_model=StockSegmentDTO | None,
    summary="Sugestão de setor do yfinance",
    description="Setor e segmento que o yfinance sugere para o ativo, ou nada quando ele não sabe.",
)
def get_segment_suggestion(ticker: str):
    return suggest_segment(fetch_info(ticker))


@import_router.post(
    "/stocks/{ticker}/profile/refresh",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Atualizar o perfil do ativo",
    description="Refaz a consulta do perfil (nome, tipo, setor e indústria) ao yfinance e troca o que estava guardado.",
)
def refresh_stock_profile(ticker: str):
    refresh_profile(ticker)


@import_router.get(
    "/tickers",
    response_model=list[TickerSuggestionDTO],
    summary="Sugestão de código de ativo",
    description="Códigos da B3 que o yfinance acha para o texto digitado, com o nome da empresa. Com menos de 2 caracteres devolve vazio sem consultar a fonte.",
)
def get_ticker_suggestions(q: Annotated[str, Query(max_length=30)] = ""):
    return search_tickers(q)
