from flask import Blueprint

from backend.core.decorators.cookie import require_client_id
from backend.features.simulation import get_simulation
from backend.routes.helpers import make_response

portfolio_bp = Blueprint("portfolio", __name__)


@portfolio_bp.route("/api/portfolio", methods=["GET"])
@require_client_id
def get_portfolio(client_id: str):
    simulation = get_simulation()
    portfolio_data = simulation.get_portfolio(client_id)
    return make_response(
        True, "Portfolio loaded successfully.", data=portfolio_data.to_json()
    )


@portfolio_bp.route("/api/portfolio/<string:ticker>", methods=["GET"])
@require_client_id
def get_portfolio_ticker(client_id, ticker):
    simulation = get_simulation()
    position = simulation.get_portfolio_ticker(client_id, ticker)
    return make_response(
        True, "Portfolio ticker data loaded successfully.", data=position.to_json()
    )


@portfolio_bp.route("/api/portfolio/cash", methods=["GET"])
@require_client_id
def get_cash(client_id: str):
    simulation = get_simulation()
    cash = simulation.get_cash(client_id)
    return make_response(True, "Cash balance loaded successfully.", data={"cash": cash})


@portfolio_bp.route("/api/economic-indicators", methods=["GET"])
def get_economic_indicators():
    simulation = get_simulation()
    indicators = simulation.get_economic_indicators()
    return make_response(
        True, "Economic indicators loaded successfully.", data=indicators
    )
