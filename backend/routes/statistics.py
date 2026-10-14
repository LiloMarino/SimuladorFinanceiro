from typing import Annotated

from fastapi import APIRouter, Query

from backend.core.dependencies import ActiveSimulation, ClientID
from backend.core.dto.economic_indicators import EconomicIndicatorsDTO
from backend.core.dto.statistics_report import (
    CompositionReportDTO,
    HighlightsDTO,
    OperationsReportDTO,
    OverviewReportDTO,
    ReturnsReportDTO,
    RiskReportDTO,
)
from backend.core.runtime.user_manager import UserManager
from backend.features.statistics.report import (
    build_composition_report,
    build_highlights,
    build_operations_report,
    build_overview_report,
    build_returns_report,
    build_risk_report,
)

statistics_router = APIRouter(prefix="/api", tags=["Statistics"])


SimulationIds = Annotated[list[int], Query(min_length=1)]


@statistics_router.get(
    "/statistics/overview",
    response_model=OverviewReportDTO,
    summary="Estatísticas: geral",
    description="Ranking dos jogadores das simulações informadas pelo retorno sobre o capital aportado, com a média da sala.",
)
def get_overview(simulation_ids: SimulationIds):
    return build_overview_report(simulation_ids)


@statistics_router.get(
    "/statistics/highlights",
    response_model=HighlightsDTO,
    summary="Estatísticas: destaques",
    description="Quem teve o maior retorno, a menor queda, mais negócios e mais IR pago, e o melhor mês de quem pede.",
)
def get_highlights(simulation_ids: SimulationIds, client_id: ClientID):
    user = UserManager.get_user(client_id)
    return build_highlights(simulation_ids, user.nickname if user else None)


@statistics_router.get(
    "/statistics/returns",
    response_model=ReturnsReportDTO,
    summary="Estatísticas: rentabilidade",
    description="Patrimônio e retorno acumulado de cada jogador dia a dia, com o CDI e o Ibovespa do mesmo período como referência.",
)
def get_returns(simulation_ids: SimulationIds):
    return build_returns_report(simulation_ids)


@statistics_router.get(
    "/statistics/risk",
    response_model=RiskReportDTO,
    summary="Estatísticas: risco",
    description="Drawdown e volatilidade em janela móvel de cada jogador dia a dia, com as métricas de risco do período.",
)
def get_risk(simulation_ids: SimulationIds):
    return build_risk_report(simulation_ids)


@statistics_router.get(
    "/statistics/composition",
    response_model=CompositionReportDTO,
    summary="Estatísticas: composição",
    description="Caixa, renda variável e renda fixa de cada jogador dia a dia, e a exposição e o lucro por setor.",
)
def get_composition(simulation_ids: SimulationIds):
    return build_composition_report(simulation_ids)


@statistics_router.get(
    "/statistics/operations",
    response_model=OperationsReportDTO,
    summary="Estatísticas: operações",
    description="Negócios executados, volume por mês, giro, IR pago e custo de impacto de cada jogador.",
)
def get_operations(simulation_ids: SimulationIds):
    return build_operations_report(simulation_ids)


@statistics_router.get(
    "/economic-indicators",
    response_model=EconomicIndicatorsDTO,
    summary="Obter indicadores econômicos",
    description="Retorna os indicadores econômicos da simulação atual.",
)
def get_economic_indicators(simulation: ActiveSimulation):
    """
    Retorna os indicadores econômicos da simulação.
    """
    indicators = simulation.get_economic_indicators()
    return indicators
