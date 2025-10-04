from flask import Blueprint, request

from backend.data_loader import update_from_csv, update_from_yfinance
from backend.routes.helpers import make_response

import_bp = Blueprint("import", __name__)


@import_bp.route("/api/import-assets", methods=["POST"])
def import_assets():
    """Import assets via yfinance or CSV."""
    data = request.get_json() or {}
    action = data.get("action")
    overwrite = data.get("overwrite", False)

    try:
        if action == "yfinance":
            ticker = data.get("ticker")
            if not ticker:
                return make_response(False, "Ticker is required.", status_code=400)
            update_from_yfinance(ticker, overwrite=overwrite)
            return make_response(True, f"Asset '{ticker}' imported successfully.")

        elif action == "csv":
            ticker = data.get("ticker")
            file = request.files.get("csv_file")
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
