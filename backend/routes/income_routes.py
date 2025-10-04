from flask import Blueprint

from backend.routes.helpers import make_response
from backend.simulation import get_simulation

income_bp = Blueprint("income", __name__)


@income_bp.route("/api/variable-income", methods=["GET"])
def get_variable_income():
    """Return list of stocks."""
    try:
        simulation = get_simulation()
        stocks = simulation.get_stocks()
        return make_response(True, "Stocks loaded successfully.", stocks)
    except Exception as e:
        return make_response(False, f"Error loading stocks: {e}", status_code=500)


@income_bp.route("/api/variable-income/<string:asset>", methods=["GET"])
def get_variable_income_details(asset):
    """Return details of a specific stock."""
    simulation = get_simulation()
    stock = simulation.get_stock_details(asset)
    if not stock:
        return make_response(False, "Asset not found.", status_code=404)
    return make_response(True, "Asset details loaded.", stock)


@income_bp.route("/api/fixed-income", methods=["GET"])
def get_fixed_income():
    """Return list of fixed-income assets."""
    try:
        simulation = get_simulation()
        fixed = (
            simulation.get_fixed_assets()
            if hasattr(simulation, "get_fixed_assets")
            else []
        )
        return make_response(True, "Fixed income assets loaded.", fixed)
    except Exception as e:
        return make_response(False, f"Error loading fixed income: {e}", status_code=500)


@income_bp.route("/api/fixed-income/<string:asset>", methods=["GET"])
def get_fixed_income_details(asset):
    """Return details of a fixed-income asset."""
    try:
        simulation = get_simulation()
        details = (
            simulation.get_fixed_asset_details(asset)
            if hasattr(simulation, "get_fixed_asset_details")
            else None
        )
        if not details:
            return make_response(False, "Asset not found.", status_code=404)
        return make_response(True, "Asset details loaded.", details)
    except Exception as e:
        return make_response(False, f"Error getting details: {e}", status_code=500)
