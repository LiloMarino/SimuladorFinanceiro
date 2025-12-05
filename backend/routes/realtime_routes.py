from flask import Blueprint, request

from backend.core.logger import setup_logger
from backend.features.realtime import get_broker
from backend.routes.helpers import make_response

realtime_bp = Blueprint("realtime", __name__)

logger = setup_logger(__name__)


@realtime_bp.route("/api/stream")
def stream():
    try:
        broker = get_broker()
        return broker.connect()
    except Exception:
        logger.exception("Erro ao abrir SSE stream")
        return make_response(False, "Internal server error", 500)


@realtime_bp.route("/api/update-subscription", methods=["POST"])
def update_subscription():
    broker = get_broker()
    data = request.get_json(force=True)
    client_id = data.get("client_id")
    events = data.get("events", [])

    if not client_id:
        return make_response(False, "client_id required", 400)

    broker.update_subscription(client_id, events)
    logger.info("Updating subscription: %s -> %s", client_id, events)
    return make_response(
        True,
        "Subscription updated",
        data={"client_id": client_id, "events": events},
    )
