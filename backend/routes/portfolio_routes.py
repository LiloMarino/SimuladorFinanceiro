from dataclasses import asdict

from flask import Blueprint

from backend.routes.helpers import make_response
from backend.simulation import get_simulation

portfolio_bp = Blueprint("portfolio", __name__)


@portfolio_bp.route("/api/portfolio", methods=["GET"])
def get_portfolio():
    try:
        simulation = get_simulation()
        portfolio_data = simulation.get_portfolio()
        return make_response(
            True, "Portfolio loaded successfully.", data=portfolio_data
        )
    except Exception as e:
        return make_response(False, f"Error loading portfolio: {e}", 500)


@portfolio_bp.route("/api/portfolio/<string:ticker>", methods=["GET"])
def get_portfolio_ticker(ticker):
    try:
        simulation = get_simulation()
        position = simulation.get_portfolio_ticker(ticker)

        return make_response(
            True, "Portfolio ticker data loaded successfully.", data=asdict(position)
        )

    except Exception as e:
        return make_response(False, f"Error loading portfolio ticker data: {e}", 500)


@portfolio_bp.route("/api/portfolio/cash", methods=["GET"])
def get_cash():
    try:
        simulation = get_simulation()
        cash = simulation.get_cash()
        return make_response(
            True, "Cash balance loaded successfully.", data={"cash": cash}
        )
    except Exception as e:
        return make_response(False, f"Error loading cash balance: {e}", 500)


@portfolio_bp.route("/api/economic-indicators", methods=["GET"])
def get_economic_indicators():
    try:
        simulation = get_simulation()
        indicators = simulation.get_economic_indicators()
        return make_response(
            True, "Economic indicators loaded successfully.", data=indicators
        )
    except Exception as e:
        return make_response(False, f"Error loading economic indicators: {e}", 500)
