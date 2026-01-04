from flask import Blueprint, request

from backend.core.decorators.cookie import require_client_id
from backend.core.decorators.simulation import require_simulation
from backend.features.realtime import notify
from backend.features.simulation.simulation import Simulation
from backend.routes.helpers import make_response

timespeed_bp = Blueprint("timespeed_bp", __name__)


@timespeed_bp.route("/api/set-speed", methods=["POST"])
@require_simulation
def set_speed(simulation: Simulation):
    data = request.get_json()
    speed = data.get("speed", 0)

    simulation.set_speed(speed)
    speed = simulation.get_speed()

    # Envia a atualização de velocidade para todos os clientes
    notify("speed_update", {"speed": speed})
    return make_response(True, "Speed updated", data={"speed": speed})


@timespeed_bp.route("/api/get-simulation-state", methods=["GET"])
@require_client_id
@require_simulation
def get_simulation_state(client_id: str, simulation: Simulation):
    current_date = simulation.get_current_date_formatted()
    speed = simulation.get_speed()
    cash = simulation.get_cash(client_id)
    return make_response(
        True,
        "Simulation state",
        data={"currentDate": current_date, "speed": speed, "cash": cash},
    )
