from flask import Blueprint, request

from backend import logger_utils
from backend.realtime import get_broker
from backend.routes.helpers import make_response

realtime_bp = Blueprint("realtime", __name__)

logger = logger_utils.setup_logger(__name__)


@realtime_bp.route("/api/stream")
def stream():
    try:
        broker = get_broker()
        return broker.connect()
    except Exception as e:
        logger.exception("Erro ao abrir SSE stream: %s", e)
        return make_response(False, "Internal server error", status_code=500)


@realtime_bp.route("/api/update-subscription", methods=["POST"])
def update_subscription():
    try:
        broker = get_broker()
        data = request.get_json(force=True)
        client_id = data.get("client_id")
        events = data.get("events", [])

        if not client_id:
            return make_response(False, "client_id required", status_code=400)

        broker.update_subscription(client_id, events)
        logger.info("Updating subscription: %s -> %s", client_id, events)
        return make_response(
            True, "Subscription updated", {"client_id": client_id, "events": events}
        )
    except Exception as e:
        logger.exception("Erro ao atualizar subscription: %s", e)
        return make_response(False, "Internal server error", status_code=500)
