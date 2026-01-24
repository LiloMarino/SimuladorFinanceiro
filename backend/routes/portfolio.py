from fastapi import APIRouter
from pydantic import BaseModel

from backend.core.dependencies import ActiveSimulation, ClientID
from backend.core.dto.portfolio import PortfolioDTO
from backend.core.dto.position import PositionDTO

portfolio_router = APIRouter(prefix="/api/portfolio", tags=["Portfolio"])


class CashResponse(BaseModel):
    cash: float


@portfolio_router.get("", response_model=PortfolioDTO)
def get_portfolio(client_id: ClientID, simulation: ActiveSimulation):
    portfolio_data = simulation.get_portfolio(client_id)
    return portfolio_data


@portfolio_router.get("/cash", response_model=CashResponse)
def get_cash(client_id: ClientID, simulation: ActiveSimulation):
    cash = simulation.get_cash(client_id)
    return CashResponse(cash=cash)


@portfolio_router.get("/{ticker}", response_model=PositionDTO)
def get_portfolio_ticker(
    client_id: ClientID, simulation: ActiveSimulation, ticker: str
):
    position = simulation.get_portfolio_ticker(client_id, ticker)
    return position
