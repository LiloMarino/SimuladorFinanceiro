from fastapi import APIRouter
from pydantic import BaseModel

from backend.core.dependencies import ActiveSimulation, ClientID
from backend.core.dto.portfolio import PortfolioDTO
from backend.core.dto.position import PositionDTO

portfolio_router = APIRouter(prefix="/api/portfolio", tags=["Portfolio"])


class CashResponse(BaseModel):
    cash: float


@portfolio_router.get(
    "",
    response_model=PortfolioDTO,
    summary="Obter portfólio",
    description="Retorna o portfólio atual do cliente com todas as posições e saldos.",
)
def get_portfolio(client_id: ClientID, simulation: ActiveSimulation):
    """
    Retorna o portfólio atual do cliente.
    """
    portfolio_data = simulation.get_portfolio(client_id)
    return portfolio_data


@portfolio_router.get(
    "/cash",
    response_model=CashResponse,
    summary="Obter saldo em caixa",
    description="Retorna o saldo de caixa (dinheiro disponível) do cliente.",
)
def get_cash(client_id: ClientID, simulation: ActiveSimulation):
    """
    Retorna o saldo em caixa do cliente.
    """
    cash = simulation.get_cash(client_id)
    return CashResponse(cash=cash)


@portfolio_router.get(
    "/{ticker}",
    response_model=PositionDTO,
    summary="Obter posição de um ativo",
    description="Retorna as informações de posição (quantidade, preço médio, etc.) de um ativo específico no portfólio.",
)
def get_portfolio_ticker(
    client_id: ClientID, simulation: ActiveSimulation, ticker: str
):
    """
    Retorna a posição de um ativo específico.
    """
    position = simulation.get_portfolio_ticker(client_id, ticker)
    return position
