from flask import Blueprint, request

from backend.core.decorators.cookie import require_client_id
from backend.core.exceptions import FixedIncomeExpiredAssetError
from backend.features.simulation import get_simulation
from backend.features.variable_income.entities.order import (
    LimitOrder,
    MarketOrder,
    OrderAction,
    OrderType,
)
from backend.routes.helpers import make_response

operation_bp = Blueprint("operation", __name__)


@operation_bp.route("/api/variable-income", methods=["GET"])
def get_variable_income():
    """Return list of stocks."""
    simulation = get_simulation()
    stocks = simulation.get_stocks()
    return make_response(
        True, "Stocks loaded successfully.", data=[s.to_json() for s in stocks]
    )


@operation_bp.route("/api/variable-income/<string:asset>", methods=["GET"])
def get_variable_income_details(asset):
    """Return details of a specific stock."""
    simulation = get_simulation()
    stock = simulation.get_stock_details(asset)
    if not stock:
        return make_response(False, "Asset not found.", 404)
    return make_response(True, "Asset details loaded.", data=stock.to_json())


@operation_bp.route("/api/variable-income/<string:asset>/orders", methods=["POST"])
@require_client_id
def submit_order(client_id, asset):
    data = request.get_json(silent=True) or {}
    size = data.get("quantity")
    order_type: str = data.get("type", "").lower()
    action: str = data.get("action", "").lower()

    # Valida os parâmetros
    if not size:
        return make_response(False, "Quantity is required.", 422)
    try:
        action_enum = OrderAction(action.lower())
    except ValueError:
        return make_response(False, "Invalid action.", 422)
    try:
        order_type_enum = OrderType(order_type.lower())
    except ValueError:
        return make_response(False, "Invalid order_type.", 422)

    if order_type_enum == OrderType.MARKET:
        order = MarketOrder(
            client_id=client_id, ticker=asset, size=size, action=action_enum
        )
    else:
        price = data.get("limit_price")
        if price is None:
            return make_response(False, "Price required for limit orders.", 422)
        order = LimitOrder(
            client_id=client_id,
            ticker=asset,
            size=size,
            action=action_enum,
            price=price,
        )

    simulation = get_simulation()
    simulation.create_order(order)
    return make_response(
        True,
        "Order submitted successfully.",
        data={"order_id": order.id, "status": order.status.name},
    )


@operation_bp.route(
    "/api/variable-income/<string:asset>/orders",
    methods=["DELETE"],
)
@require_client_id
def cancel_order(client_id, asset):
    data = request.get_json(silent=True) or {}
    order_id = data.get("order_id")
    if not order_id:
        return make_response(False, "Order ID is required.", 422)
    simulation = get_simulation()
    try:
        canceled = simulation.cancel_order(order_id=order_id, client_id=client_id)
        if not canceled:
            return make_response(False, "Order not found", 404)
    except PermissionError as e:
        return make_response(False, str(e), 403)
    except ValueError as e:
        return make_response(False, str(e), 400)
    return make_response(True, "Order canceled successfully.")


@operation_bp.route("/api/variable-income/<string:asset>/orders", methods=["GET"])
def list_order_book(asset):
    """Lista todas as ordens (BUY + SELL) no book para o ativo"""
    simulation = get_simulation()
    orders = simulation.get_orders(asset)
    return make_response(
        True,
        "Order book loaded.",
        data=[o.to_json() for o in orders],
    )


@operation_bp.route("/api/fixed-income", methods=["GET"])
def get_fixed_income():
    """Return list of fixed-income assets."""
    simulation = get_simulation()
    fixed = simulation.get_fixed_assets()
    fixed_json = [asset.to_json() for asset in fixed]
    return make_response(True, "Fixed income assets loaded.", data=fixed_json)


@operation_bp.route("/api/fixed-income/<string:asset_uuid>", methods=["GET"])
def get_fixed_income_details(asset_uuid):
    """Return details of a fixed-income asset."""
    simulation = get_simulation()
    fixed = simulation.get_fixed_asset(asset_uuid)
    if not fixed:
        return make_response(False, "Asset not found.", 404)
    return make_response(True, "Asset details loaded.", data=fixed.to_json())


@operation_bp.route("/api/fixed-income/<string:asset_uuid>/buy", methods=["POST"])
@require_client_id
def buy_fixed_income(client_id, asset_uuid):
    simulation = get_simulation()
    fixed = simulation.get_fixed_asset(asset_uuid)
    if not fixed:
        return make_response(False, "Asset not found.", 404)

    data = request.get_json(silent=True) or {}
    quantity = data.get("quantity")
    if not quantity:
        return make_response(False, "Quantity is required.", 422)

    try:
        simulation._engine.fixed_broker.buy(client_id, fixed, quantity)
    except FixedIncomeExpiredAssetError as e:
        return make_response(False, str(e), 409)
    except ValueError as e:
        return make_response(False, str(e), 400)

    return make_response(True, "Investment queued successfully.")
