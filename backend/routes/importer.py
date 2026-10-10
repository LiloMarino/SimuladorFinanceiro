from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from pydantic import BaseModel

from backend.core import repository
from backend.core.dependencies.simulation import require_no_active_simulation
from backend.core.dto.series_coverage import SeriesCoverageDTO
from backend.core.enum import AssetClass, IndicatorSeries
from backend.core.exceptions.http_exceptions import BadGatewayError, NotFoundError
from backend.features.import_data.coverage import get_series_coverage
from backend.features.import_data.importer_service import (
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


def str_to_bool(value: str | bool | None) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on")
    return False


class ImportYFinanceRequest(BaseModel):
    ticker: str
    overwrite: bool = False


@import_router.post(
    "/yfinance",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Importar dados de yfinance",
    description="Importa dados de ativos do yfinance para um ticker especificado.",
)
def import_assets_json(request: ImportYFinanceRequest):
    """
    Importa dados de ativos do yfinance.
    """
    ticker = request.ticker
    overwrite = request.overwrite
    update_from_yfinance(ticker, overwrite)


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
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Importar dados de CSV",
    description="Importa dados de ativos a partir de um arquivo CSV enviado via multipart/form-data.",
)
def import_assets_csv(
    ticker: Annotated[str, Form(...)],
    csv_file: Annotated[UploadFile, File(...)],
    overwrite: Annotated[str, Form(...)] = "false",
):
    """
    Importa dados de ativos de um arquivo CSV.
    """
    overwrite_bool = str_to_bool(overwrite)
    update_from_csv(csv_file, ticker, overwrite_bool)
