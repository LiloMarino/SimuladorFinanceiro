from typing import Any, Dict, Optional, Union

from flask import Blueprint, request
from werkzeug.datastructures import FileStorage

from backend.data_loader import update_from_csv, update_from_yfinance
from backend.routes.helpers import make_response

import_bp = Blueprint("import", __name__)


def str_to_bool(value: Union[str, bool, None]) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on")
    return False


@import_bp.route("/api/import-assets", methods=["POST"])
def import_assets() -> Any:
    data: Dict[str, Any]
    file: Optional[FileStorage] = None

    if request.content_type and "multipart/form-data" in request.content_type:
        data = request.form
        file = request.files.get("csv_file")
    else:
        data = request.get_json() or {}

    action: Optional[str] = data.get("action")
    ticker: Optional[str] = data.get("ticker")
    overwrite: bool = str_to_bool(data.get("overwrite"))
    try:
        if action == "yfinance":
            if not ticker:
                return make_response(False, "Ticker is required.", status_code=400)
            update_from_yfinance(ticker, overwrite=overwrite)
            return make_response(True, f"Asset '{ticker}' imported successfully.")

        elif action == "csv":
            if not ticker or not file:
                return make_response(
                    False, "Ticker and CSV file are required.", status_code=400
                )
            update_from_csv(file, ticker, overwrite=overwrite)
            return make_response(True, f"CSV file '{ticker}' imported successfully.")

        else:
            return make_response(False, "Invalid action.", status_code=400)

    except Exception as e:
        return make_response(False, f"Error importing assets: {e}", status_code=500)
