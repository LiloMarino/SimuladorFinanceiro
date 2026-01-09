from fastapi import APIRouter

from backend.fastapi_deps import ActiveSimulation, ClientID
from backend.fastapi_helpers import make_response

portfolio_router = APIRouter(prefix="/api", tags=["portfolio"])


@portfolio_router.get("/portfolio")
def get_portfolio(client_id: ClientID, simulation: ActiveSimulation):
    portfolio_data = simulation.get_portfolio(client_id)
    return make_response(
        True, "Portfolio loaded successfully.", data=portfolio_data.to_json()
    )


@portfolio_router.get("/portfolio/{ticker}")
def get_portfolio_ticker(client_id: ClientID, simulation: ActiveSimulation, ticker: str):
    position = simulation.get_portfolio_ticker(client_id, ticker)
    return make_response(
        True, "Portfolio ticker data loaded successfully.", data=position.to_json()
    )


@portfolio_router.get("/portfolio/cash")
def get_cash(client_id: ClientID, simulation: ActiveSimulation):
    cash = simulation.get_cash(client_id)
    return make_response(True, "Cash balance loaded successfully.", data={"cash": cash})


@portfolio_router.get("/economic-indicators")
def get_statistics(simulation: ActiveSimulation):
    indicators = simulation.get_economic_indicators()
    return make_response(
        True, "Economic indicators loaded successfully.", data=indicators
    )
