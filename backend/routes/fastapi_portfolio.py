"""
Portfolio routes for FastAPI.
Migrated from Flask Blueprint to FastAPI APIRouter.
"""

from fastapi import APIRouter

from backend.core.dependencies import ActiveSimulation, ClientID
from backend.routes.fastapi_helpers import make_response_data

router = APIRouter(prefix="/api", tags=["portfolio"])


@router.get("/portfolio")
async def get_portfolio(client_id: ClientID, simulation: ActiveSimulation):
    """Get user's portfolio."""
    portfolio_data = simulation.get_portfolio(client_id)
    return make_response_data(
        True, "Portfolio loaded successfully.", data=portfolio_data.to_json()
    )


@router.get("/portfolio/{ticker}")
async def get_portfolio_ticker(
    client_id: ClientID, simulation: ActiveSimulation, ticker: str
):
    """Get specific ticker position in portfolio."""
    position = simulation.get_portfolio_ticker(client_id, ticker)
    return make_response_data(
        True, "Portfolio ticker data loaded successfully.", data=position.to_json()
    )


@router.get("/portfolio/cash")
async def get_cash(client_id: ClientID, simulation: ActiveSimulation):
    """Get user's cash balance."""
    cash = simulation.get_cash(client_id)
    return make_response_data(True, "Cash balance loaded successfully.", data={"cash": cash})


@router.get("/economic-indicators")
async def get_economic_indicators(simulation: ActiveSimulation):
    """Get economic indicators."""
    indicators = simulation.get_economic_indicators()
    return make_response_data(
        True, "Economic indicators loaded successfully.", data=indicators
    )
