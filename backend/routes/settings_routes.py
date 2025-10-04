from flask import Blueprint, request

from backend.routes.helpers import make_response
from backend.simulation import get_simulation

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/api/strategies", methods=["GET"])
def get_strategies():
    """Return available strategies."""
    try:
        simulation = get_simulation()
        strategies = (
            simulation.get_strategies() if hasattr(simulation, "get_strategies") else []
        )
        return make_response(True, "Strategies loaded successfully.", strategies)
    except Exception as e:
        return make_response(False, f"Error loading strategies: {e}", status_code=500)


@settings_bp.route("/api/statistics", methods=["GET"])
def get_statistics():
    """Return performance statistics."""
    try:
        simulation = get_simulation()
        stats = (
            simulation.get_statistics() if hasattr(simulation, "get_statistics") else {}
        )
        return make_response(True, "Statistics loaded successfully.", stats)
    except Exception as e:
        return make_response(False, f"Error loading statistics: {e}", status_code=500)


@settings_bp.route("/api/lobby", methods=["GET"])
def get_lobby():
    """Return lobby or simulation status."""
    try:
        simulation = get_simulation()
        state = simulation.get_state() if hasattr(simulation, "get_state") else {}
        return make_response(True, "Lobby loaded successfully.", state)
    except Exception as e:
        return make_response(False, f"Error loading lobby: {e}", status_code=500)


@settings_bp.route("/api/settings", methods=["GET", "PUT"])
def get_or_update_settings():
    """Retrieve or update configuration settings."""
    simulation = get_simulation()
    if request.method == "GET":
        try:
            settings = (
                simulation.get_settings() if hasattr(simulation, "get_settings") else {}
            )
            return make_response(True, "Settings loaded successfully.", settings)
        except Exception as e:
            return make_response(False, f"Error loading settings: {e}", status_code=500)
    else:
        try:
            data = request.get_json() or {}
            simulation.update_settings(data)
            return make_response(
                True,
                "Settings updated successfully.",
                simulation.get_settings(),
            )
        except Exception as e:
            return make_response(
                False, f"Error updating settings: {e}", status_code=500
            )
