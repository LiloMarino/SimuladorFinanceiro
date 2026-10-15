from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query

from backend.core.dependencies import ClientID
from backend.core.dto.correlation import (
    CorrelationAssetsDTO,
    CorrelationMatrixDTO,
    CorrelationWindow,
)
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.correlation.correlation import (
    build_correlation_assets,
    build_correlation_matrix,
)

correlation_router = APIRouter(prefix="/api/correlation", tags=["Correlation"])


@correlation_router.get(
    "/assets",
    response_model=CorrelationAssetsDTO,
    summary="Ativos da correlação",
    description="Tickers com preço para a ferramenta de correlação e o último dia que a janela alcança. Na partida, a janela termina na data da simulação.",
)
def get_correlation_assets():
    return build_correlation_assets()


@correlation_router.get(
    "",
    response_model=CorrelationMatrixDTO,
    summary="Matriz de correlação",
    description="Correlação dos retornos diários de cada par de tickers, com o Ibovespa como referência, na janela que termina em `end`, e os pares que se destacam. Na partida, `end` é sempre a data da simulação e a média da carteira usa as ações de quem pede.",
)
def get_correlation(
    tickers: Annotated[list[str], Query(min_length=1, max_length=20)],
    client_id: ClientID,
    window: CorrelationWindow = "1y",
    end: date | None = None,
):
    held: set[str] = set()
    if SimulationManager.has_active_simulation():
        portfolio = SimulationManager.get_active_simulation().get_portfolio(client_id)
        held = {p.ticker for p in portfolio.variable_income}
    return build_correlation_matrix(tickers, window, end, held)
