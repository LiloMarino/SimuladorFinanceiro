from datetime import datetime

from flask import Blueprint, request

from backend import config
from backend.core import repository
from backend.core.decorators.cookie import require_client_id
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
        data = sim.settings
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

    repository.user.reset_users_data(start_date)
    sim = SimulationManager.create_simulation(
        SimulationDTO(
            start_date=start_date,
            end_date=end_date,
        )
    )
    data = sim.settings
    controller.trigger_start()

    notify(
        "simulation_started",
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


@simulation_bp.route("/api/simulation/continue", methods=["POST"])
@require_host
def continue_simulation():
    """Continua a simulação a partir do último snapshot"""

    data = request.get_json(force=True)

    try:
        end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
    except Exception:
        return make_response(False, "Invalid end_date.", status_code=422)

    last_snapshot_date = repository.snapshot.get_last_snapshot_date()
    if not last_snapshot_date:
        return make_response(
            False, "No snapshots found to continue simulation.", status_code=404
        )

    if last_snapshot_date >= end_date:
        return make_response(
            False,
            "Last snapshot date is after or equal to the target end date.",
            status_code=422,
        )

    sim = SimulationManager.create_simulation(
        SimulationDTO(
            start_date=last_snapshot_date,
            end_date=end_date,
        )
    )

    controller.trigger_start()

    notify(
        "simulation_started",
        {
            "active": True,
            "simulation": sim.settings.to_json(),
        },
    )

    return make_response(
        True,
        "Simulation continued from last snapshot.",
        status_code=201,
        data={
            "active": True,
            "simulation": sim.settings.to_json(),
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
@require_client_id
def get_simulation_settings(client_id: str):
    user = UserManager.get_user(client_id)
    if user is None:
        return make_response(False, "User not found.", status_code=404)
    host_nickname = config.toml.host.nickname

    settings = SimulationManager.get_settings()
    return make_response(
        True,
        "Simulation settings loaded.",
        data={
            "is_host": user.nickname == host_nickname,
            "simulation": settings.to_json(),
        },
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
