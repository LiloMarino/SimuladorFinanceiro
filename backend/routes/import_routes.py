from typing import Union

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


def handle_yfinance(data: dict):
    ticker = data.get("ticker")
    overwrite = str_to_bool(data.get("overwrite"))
    if not ticker:
        return make_response(False, "Ticker is required.", 422)
    update_from_yfinance(ticker, overwrite)
    return make_response(True, f"Asset '{ticker}' imported successfully.")


def handle_csv(data: dict, file: FileStorage | None):
    ticker = data.get("ticker")
    overwrite = str_to_bool(data.get("overwrite"))
    if not ticker or not file:
        return make_response(False, "Ticker and CSV file are required.", 422)
    update_from_csv(file, ticker, overwrite)
    return make_response(True, f"CSV '{ticker}' imported successfully.")


@import_bp.route("/api/import-assets", methods=["POST"])
def import_assets():
    if request.content_type and "multipart/form-data" in request.content_type:
        data = request.form
        file = request.files.get("csv_file")
    else:
        data = request.get_json() or {}
        file = None

    action = data.get("action")

    try:
        raise NotImplementedError
        if action == "yfinance":
            return handle_yfinance(data)
        elif action == "csv":
            return handle_csv(data, file)
        else:
            return make_response(False, "Invalid action.", 400)
    except Exception as e:
        return make_response(False, f"Error importing assets: {e}", 500)
