from flask import Blueprint

from backend.routes.helpers import make_response
from backend.simulation import get_simulation

portfolio_bp = Blueprint("portfolio", __name__)


@portfolio_bp.route("/api/portfolio", methods=["GET"])
def get_portfolio():
    """Return portfolio composition."""
    try:
        simulation = get_simulation()
        portfolio_data = (
            simulation.get_portfolio() if hasattr(simulation, "get_portfolio") else {}
        )
        return make_response(True, "Portfolio loaded successfully.", portfolio_data)
    except Exception as e:
        return make_response(False, f"Error loading portfolio: {e}", status_code=500)
