from flask import Blueprint, current_app, jsonify, request

from backend.realtime import get_realtime_manager
from backend.simulation import get_simulation

realtime_bp = Blueprint("realtime", __name__)


@realtime_bp.route("/api/stream")
def stream():
    """SSE stream endpoint for real-time updates."""
    manager = current_app.config.get("realtime")
    if manager is None:
        return "Realtime not configured", 500
    return manager.connect()


@realtime_bp.route("/api/update-subscription", methods=["POST"])
def update_subscription():
    """Update client subscriptions to topics."""
    manager = current_app.config.get("realtime")
    if manager is None:
        return jsonify({"error": "realtime not configured"}), 500

    data = request.get_json(force=True)
    client_id = data.get("client_id")
    topics = data.get("topics", [])

    if not client_id:
        return jsonify({"error": "client_id required"}), 400

    manager.update_subscription(client_id, topics)
    return jsonify({"status": "ok", "client_id": client_id, "topics": topics})


@realtime_bp.route("/api/set-speed", methods=["POST"])
def set_speed():
    data = request.get_json()
    speed = data.get("speed", 0)

    simulation = get_simulation()
    simulation.set_speed(speed)

    # Envia a atualização de velocidade via WebSocket para todos
    manager = get_realtime_manager()
    # manager.broadcast("speed_update", {"speed": simulation.get_speed()})

    return jsonify({"speed": simulation.get_speed()})
