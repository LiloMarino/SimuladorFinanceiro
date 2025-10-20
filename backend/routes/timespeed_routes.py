from flask import Blueprint, request

from backend.realtime import notify
from backend.routes.helpers import make_response
from backend.simulation import get_simulation

timespeed_bp = Blueprint("timespeed_bp", __name__)


@timespeed_bp.route("/api/set-speed", methods=["POST"])
def set_speed():
    data = request.get_json()
    speed = data.get("speed", 0)

    simulation = get_simulation()
    simulation.set_speed(speed)
    speed = simulation.get_speed()

    # Envia a atualização de velocidade para todos os clientes
    notify("speed_update", {"speed": speed})
    return make_response(True, "Speed updated", data={"speed": speed})


@timespeed_bp.route("/api/get-simulation-state", methods=["GET"])
def get_simulation_state():
    simulation = get_simulation()
    current_date = simulation.get_current_date_formatted()
    speed = simulation.get_speed()
    return make_response(
        True, "Simulation state", data={"currentDate": current_date, "speed": speed}
    )
