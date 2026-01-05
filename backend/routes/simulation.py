from datetime import datetime

from flask import Blueprint, request

from backend.core.decorators.host import require_host
from backend.core.dto.simulation import SimulationDTO
from backend.core.exceptions import NoActiveSimulationError
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.realtime import notify
from backend.features.simulation.simulation_loop import controller
from backend.routes.helpers import make_response

simulation_bp = Blueprint("simulation", __name__)


@simulation_bp.route("/api/simulation/status", methods=["GET"])
def simulation_status():
    try:
        sim = SimulationManager.get_active_simulation()
        data = sim.simulation_data
        return make_response(
            True,
            "Simulation active.",
            data={
                "active": True,
                "simulation": data.to_json(),
            },
        )
    except NoActiveSimulationError:
        return make_response(
            True,
            "No active simulation.",
            data={
                "active": False,
            },
        )


@simulation_bp.route("/api/simulation/create", methods=["POST"])
@require_host
def create_simulation():
    data = request.get_json(force=True)

    try:
        start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
    except Exception:
        return make_response(
            False,
            "Invalid start_date or end_date.",
            status_code=422,
        )

    sim = SimulationManager.create_simulation(
        SimulationDTO(
            start_date=start_date,
            end_date=end_date,
        )
    )
    data = sim.simulation_data
    controller.trigger_start()

    notify(
        "simulation_created",
        {
            "active": True,
            "simulation": data.to_json(),
        },
    )
    return make_response(
        True,
        "Simulation created.",
        status_code=201,
        data={
            "active": True,
            "simulation": data.to_json(),
        },
    )


@simulation_bp.route("/api/simulation/players", methods=["GET"])
def get_active_players():
    active_players = UserManager.list_active_players()
    return make_response(
        True,
        "Players loaded successfully.",
        data=[{"nickname": p.nickname} for p in active_players],
    )


@simulation_bp.route("/api/simulation/settings", methods=["GET"])
def get_simulation_settings():
    settings = SimulationManager.get_settings()
    return make_response(
        True,
        "Simulation settings loaded.",
        data=settings.to_json(),
    )


@simulation_bp.route("/api/simulation/settings", methods=["PUT"])
@require_host
def update_simulation_settings():
    payload = request.get_json(force=True)

    try:
        start_date = datetime.strptime(payload["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(payload["end_date"], "%Y-%m-%d").date()
    except Exception:
        return make_response(False, "Invalid payload.", status_code=422)

    if start_date > end_date:
        return make_response(
            False,
            "start_date must be before end_date.",
            status_code=422,
        )

    settings = SimulationManager.update_settings(
        SimulationDTO(
            start_date=start_date,
            end_date=end_date,
        )
    )

    notify("simulation_settings_update", settings.to_json())

    return make_response(
        True,
        "Simulation settings updated.",
        data=settings.to_json(),
    )
