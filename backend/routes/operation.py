from flask import Blueprint, request

from backend.core.decorators.cookie import require_client_id
from backend.core.exceptions import FixedIncomeExpiredAssetError
from backend.features.simulation import get_simulation
from backend.features.simulation.entities.order import OrderAction
from backend.features.strategy.manual import ManualStrategy
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


@operation_bp.route("/api/variable-income/<string:asset>/buy", methods=["POST"])
@require_client_id
def buy_stock(client_id, asset):
    data = request.get_json(silent=True) or {}
    quantity = data.get("quantity")
    if not quantity:
        return make_response(False, "Quantity is required.", 422)
    ManualStrategy.queue_order(client_id, OrderAction.BUY, asset, quantity)
    return make_response(True, "Order queued successfully.")


@operation_bp.route("/api/variable-income/<string:asset>/sell", methods=["POST"])
@require_client_id
def sell_stock(client_id, asset):
    data = request.get_json(silent=True) or {}
    quantity = data.get("quantity")
    if not quantity:
        return make_response(False, "Quantity is required.", 422)
    ManualStrategy.queue_order(client_id, OrderAction.SELL, asset, quantity)
    return make_response(True, "Order queued successfully.")


# New unified orders endpoints
@operation_bp.route("/api/variable-income/<string:asset>/orders", methods=["GET"])
def list_orders(asset):
    """Retorna ordens (pendentes e histórico) para um ativo específico."""
    from backend.core import repository

    orders = ManualStrategy.get_orders(asset)

    # Convert orders to json-friendly dicts
    def _to_json(o):
        user = repository.user.get_by_client_id(o.client_id)
        nickname = user.nickname if user else None
        return {
            "id": o.id,
            "client_id": o.client_id,
            "nickname": nickname,
            "ticker": o.ticker,
            "size": o.size,
            "action": o.action.value,
            "order_type": o.order_type.value,
            "price": o.price,
            "timestamp": o.timestamp.isoformat(),
            "status": o.status.value,
        }

    return make_response(True, "Orders loaded.", data=[_to_json(o) for o in orders])


@operation_bp.route(
    "/api/variable-income/<string:asset>/orders/<string:order_id>/cancel",
    methods=["POST"],
)
@require_client_id
def cancel_order(client_id, asset, order_id):
    canceled = ManualStrategy.cancel_order(client_id, order_id)
    if not canceled:
        return make_response(False, "Order not found or cannot be canceled.", 404)
    return make_response(True, "Order canceled successfully.")


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
