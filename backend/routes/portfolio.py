from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.core.dependencies import ActiveSimulation, ClientID

portfolio_router = APIRouter(prefix="/api/portfolio", tags=["Portfolio"])


@portfolio_router.get("")
def get_portfolio(client_id: ClientID, simulation: ActiveSimulation):
    portfolio_data = simulation.get_portfolio(client_id)
    return JSONResponse(content={"data": portfolio_data.to_json()})


@portfolio_router.get("/cash")
def get_cash(client_id: ClientID, simulation: ActiveSimulation):
    cash = simulation.get_cash(client_id)
    return JSONResponse(content={"data": {"cash": cash}})


@portfolio_router.get("/{ticker}")
def get_portfolio_ticker(
    client_id: ClientID, simulation: ActiveSimulation, ticker: str
):
    position = simulation.get_portfolio_ticker(client_id, ticker)
    return JSONResponse(content={"data": position.to_json()})
