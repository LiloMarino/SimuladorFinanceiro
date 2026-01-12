from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel

from backend.features.import_data.importer_service import (
    update_from_csv,
    update_from_yfinance,
)
from backend.routes.helpers import make_response

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


@import_router.post("/yfinance")
def import_assets_json(request: ImportYFinanceRequest):
    """Import assets from yfinance (JSON payload)."""
    ticker = request.ticker
    overwrite = request.overwrite
    update_from_yfinance(ticker, overwrite)
    return make_response(True, f"Asset '{ticker}' imported successfully.")


@import_router.post("/csv")
def import_assets_csv(
    ticker: Annotated[str, Form(...)],
    csv_file: Annotated[UploadFile, File(...)],
    overwrite: Annotated[str, Form(...)] = "false",
):
    """Import assets from CSV (multipart/form-data)."""
    overwrite_bool = str_to_bool(overwrite)
    update_from_csv(csv_file.file, ticker, overwrite_bool)
    return make_response(True, f"CSV '{ticker}' imported successfully.")
