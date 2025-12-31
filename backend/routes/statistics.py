from flask import Blueprint

from backend.features.simulation import get_simulation
from backend.routes.helpers import make_response

statistics_bp = Blueprint("statistics", __name__)


@statistics_bp.route("/api/statistics", methods=["GET"])
def get_statistics():
    """Return performance statistics."""
    simulation = get_simulation()
    stats = simulation.get_statistics()
    return make_response(True, "Statistics loaded successfully.", stats)
