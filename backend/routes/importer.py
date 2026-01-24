from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile, status
from pydantic import BaseModel

from backend.features.import_data.importer_service import (
    update_from_csv,
    update_from_yfinance,
)

import_router = APIRouter(prefix="/api/import-assets", tags=["Import Assets"])


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
    update_from_csv(csv_file.file, ticker, overwrite_bool)
