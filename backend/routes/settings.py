# type: ignore
from flask import Blueprint, request

from backend.features.simulation import get_simulation
from backend.routes.helpers import make_response

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/api/strategies", methods=["GET"])
def get_strategies():
    """Return available strategies."""
    simulation = get_simulation()
    strategies = (
        simulation.get_strategies() if hasattr(simulation, "get_strategies") else []
    )
    return make_response(True, "Strategies loaded successfully.", strategies)


@settings_bp.route("/api/lobby", methods=["GET"])
def get_lobby():
    """Return lobby or simulation status."""
    simulation = get_simulation()
    state = simulation.get_state() if hasattr(simulation, "get_state") else {}
    return make_response(True, "Lobby loaded successfully.", state)


@settings_bp.route("/api/settings", methods=["GET", "PUT"])
def get_or_update_settings():
    """Retrieve or update configuration settings."""
    simulation = get_simulation()
    if request.method == "GET":
        settings = (
            simulation.get_settings() if hasattr(simulation, "get_settings") else {}
        )
        return make_response(True, "Settings loaded successfully.", settings)
    else:
        data = request.get_json() or {}
        simulation.update_settings(data)
        return make_response(
            True,
            "Settings updated successfully.",
            simulation.get_settings(),
        )
