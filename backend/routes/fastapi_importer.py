"""
Asset import routes for FastAPI.
Migrated from Flask Blueprint to FastAPI APIRouter.
"""

from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel

from backend.core.exceptions.fastapi_exceptions import (
    BadRequestError,
    UnprocessableEntityError,
)
from backend.features.import_data.importer_service import (
    update_from_csv,
    update_from_yfinance,
)
from backend.routes.fastapi_helpers import make_response_data

router = APIRouter(prefix="/api", tags=["import"])


def str_to_bool(value: str | bool | None) -> bool:
    """Convert string to boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on")
    return False


class ImportYFinanceRequest(BaseModel):
    action: str
    ticker: str
    overwrite: bool = False


# Create annotated type for optional file
OptionalFile = Annotated[UploadFile | None, File()]


@router.post("/import-assets")
async def import_assets_json(request: ImportYFinanceRequest):
    """Import assets from yfinance (JSON payload)."""
    if request.action == "yfinance":
        ticker = request.ticker
        overwrite = request.overwrite
        if not ticker:
            raise UnprocessableEntityError("Ticker is required.")
        update_from_yfinance(ticker, overwrite)
        return make_response_data(True, f"Asset '{ticker}' imported successfully.")
    else:
        raise BadRequestError("Invalid action.")


@router.post("/import-assets-csv")
async def import_assets_csv(
    action: str = Form(...),
    ticker: str = Form(...),
    overwrite: str | bool = Form(False),
    csv_file: OptionalFile = None,
):
    """Import assets from CSV (multipart/form-data)."""
    overwrite_bool = str_to_bool(overwrite)

    if action == "csv":
        if not ticker or not csv_file:
            raise UnprocessableEntityError("Ticker and CSV file are required.")
        # Convert UploadFile to file-like object for update_from_csv
        update_from_csv(csv_file.file, ticker, overwrite_bool)
        return make_response_data(True, f"CSV '{ticker}' imported successfully.")
    else:
        raise BadRequestError("Invalid action.")
