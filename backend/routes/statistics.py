from flask import Blueprint

from backend.core.decorators.simulation import require_simulation
from backend.features.simulation.simulation import Simulation
from backend.routes.helpers import make_response

statistics_bp = Blueprint("statistics", __name__)


@statistics_bp.route("/api/statistics", methods=["GET"])
@require_simulation
def get_statistics(simulation: Simulation):
    """Return performance statistics."""
    stats = simulation.get_statistics()
    return make_response(
        True,
        "Statistics loaded successfully.",
        data=[stat.to_json() for stat in stats],
    )
