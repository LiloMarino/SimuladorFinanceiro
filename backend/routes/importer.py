from fastapi import APIRouter, File, Form, UploadFile, status

from backend.fastapi_helpers import make_response
from backend.features.import_data.importer_service import (
    update_from_csv,
    update_from_yfinance,
)

import_router = APIRouter(prefix="/api", tags=["import"])


def str_to_bool(value: str | bool | None) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on")
    return False


@import_router.post("/import-assets")
async def import_assets(
    action: str = Form(...),
    ticker: str = Form(...),
    overwrite: str | bool = Form(False),
    csv_file: UploadFile | None = None,
):
    overwrite_bool = str_to_bool(overwrite)

    if action == "yfinance":
        if not ticker:
            return make_response(
                False,
                "Ticker is required.",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        update_from_yfinance(ticker, overwrite_bool)
        return make_response(True, f"Asset '{ticker}' imported successfully.")
    elif action == "csv":
        if not ticker or not csv_file:
            return make_response(
                False,
                "Ticker and CSV file are required.",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        # Read file content and create a BytesIO object for compatibility
        import io

        content = await csv_file.read()
        file_obj = io.BytesIO(content)
        file_obj.name = csv_file.filename or "upload.csv"
        
        update_from_csv(file_obj, ticker, overwrite_bool)
        return make_response(True, f"CSV '{ticker}' imported successfully.")
    else:
        return make_response(
            False, "Invalid action.", status_code=status.HTTP_400_BAD_REQUEST
        )
