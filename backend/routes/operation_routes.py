from flask import Blueprint, request

from backend.routes.helpers import make_response
from backend.simulation import get_simulation
from backend.strategy.manual import ManualStrategy

operation_bp = Blueprint("operation", __name__)


@operation_bp.route("/api/variable-income", methods=["GET"])
def get_variable_income():
    """Return list of stocks."""
    try:
        simulation = get_simulation()
        stocks = simulation.get_stocks()
        return make_response(True, "Stocks loaded successfully.", data=stocks)
    except Exception as e:
        return make_response(False, f"Error loading stocks: {e}", 500)


@operation_bp.route("/api/variable-income/<string:asset>", methods=["GET"])
def get_variable_income_details(asset):
    """Return details of a specific stock."""
    simulation = get_simulation()
    stock = simulation.get_stock_details(asset)
    if not stock:
        return make_response(False, "Asset not found.", 404)
    return make_response(True, "Asset details loaded.", data=stock)


@operation_bp.route("/api/variable-income/<string:asset>/buy", methods=["POST"])
def buy_stock(asset):
    data = request.get_json(silent=True) or {}
    quantity = data.get("quantity")
    if not quantity:
        return make_response(False, "Quantity is required.", 422)
    ManualStrategy.queue_order("buy", asset, quantity)
    return make_response(True, "Order queued successfully.")


@operation_bp.route("/api/variable-income/<string:asset>/sell", methods=["POST"])
def sell_stock(asset):
    data = request.get_json(silent=True) or {}
    quantity = data.get("quantity")
    if not quantity:
        return make_response(False, "Quantity is required.", 422)
    ManualStrategy.queue_order("sell", asset, quantity)
    return make_response(True, "Order queued successfully.")


@operation_bp.route("/api/fixed-income", methods=["GET"])
def get_fixed_income():
    """Return list of fixed-income assets."""
    try:
        simulation = get_simulation()
        fixed = simulation.get_fixed_assets()
        return make_response(True, "Fixed income assets loaded.", data=fixed)
    except Exception as e:
        return make_response(False, f"Error loading fixed income: {e}", 500)


@operation_bp.route("/api/fixed-income/<string:asset>", methods=["GET"])
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
            return make_response(False, "Asset not found.", 404)
        return make_response(True, "Asset details loaded.", details)
    except Exception as e:
        return make_response(False, f"Error getting details: {e}", 500)
