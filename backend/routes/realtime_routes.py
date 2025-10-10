from flask import Blueprint, request

from backend import logger_utils
from backend.realtime import get_broker, notify
from backend.routes.helpers import make_response
from backend.simulation import get_simulation

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
        topics = data.get("topics", [])

        if not client_id:
            return make_response(False, "client_id required", status_code=400)

        broker.update_subscription(client_id, topics)
        return make_response(
            True, "Subscription updated", {"client_id": client_id, "topics": topics}
        )
    except Exception as e:
        logger.exception("Erro ao atualizar subscription: %s", e)
        return make_response(False, "Internal server error", status_code=500)


@realtime_bp.route("/api/set-speed", methods=["POST"])
def set_speed():
    data = request.get_json()
    speed = data.get("speed", 0)

    simulation = get_simulation()
    simulation.set_speed(speed)
    speed = simulation.get_speed()

    # Envia a atualização de velocidade para todos os clientes
    notify("speed_update", {"speed": speed})
    return make_response(True, "Speed updated", {"speed": speed})
