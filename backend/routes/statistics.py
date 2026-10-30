from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Query
from pydantic import BaseModel

from backend.core.dependencies import ActiveSimulation, ClientID
from backend.core.dto.bot import BotReportDTO
from backend.core.dto.economic_indicators import EconomicIndicatorsDTO
from backend.core.dto.economy import EconomyPanelDTO
from backend.core.dto.statistics_report import (
    CompositionReportDTO,
    HighlightsDTO,
    OperationsReportDTO,
    OverviewReportDTO,
    ReturnsReportDTO,
    RiskReportDTO,
    ScoreHistoryReportDTO,
    StatisticsNextUpdateDTO,
)
from backend.core.dto.strategy import StrategyLogPageDTO
from backend.core.runtime.user_manager import UserManager
from backend.features.statistics.bots import bot_orders, build_bots_report
from backend.features.statistics.cache import match_cache
from backend.features.statistics.report import (
    build_composition_report,
    build_highlights,
    build_operations_report,
    build_overview_report,
    build_returns_report,
    build_risk_report,
    build_score_history_report,
)

statistics_router = APIRouter(prefix="/api", tags=["Statistics"])


SimulationIds = Annotated[list[int], Query(min_length=1)]


def _report[T: BaseModel](
    simulation_ids: list[int], tab: str, build: Callable[[list[int]], T]
) -> T:
    """A aba da partida em andamento sai do relatório do mês; as demais, do banco agora."""
    cache = match_cache(simulation_ids)
    if cache is None:
        return build(simulation_ids)
    return cache.report(tab, lambda: build(simulation_ids))


@statistics_router.get(
    "/statistics/overview",
    response_model=OverviewReportDTO,
    summary="Estatísticas: geral",
    description="Ranking dos jogadores das simulações informadas pelo retorno sobre o capital aportado, com a média da sala.",
)
def get_overview(simulation_ids: SimulationIds):
    return _report(simulation_ids, "overview", build_overview_report)


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
    description="Patrimônio e retorno acumulado de cada jogador dia a dia, com o CDI e o Ibovespa do mesmo período como referência. Numa simulação só com mais de um ano, as séries trazem o fechamento de cada semana (até cinco anos) ou de cada mês.",
)
def get_returns(simulation_ids: SimulationIds):
    return _report(simulation_ids, "returns", build_returns_report)


@statistics_router.get(
    "/statistics/risk",
    response_model=RiskReportDTO,
    summary="Estatísticas: risco",
    description="Drawdown e volatilidade em janela móvel de cada jogador dia a dia, com as métricas de risco do período. Numa simulação só com mais de um ano, as séries trazem o fechamento de cada semana (até cinco anos) ou de cada mês.",
)
def get_risk(simulation_ids: SimulationIds):
    return _report(simulation_ids, "risk", build_risk_report)


@statistics_router.get(
    "/statistics/score-history",
    response_model=ScoreHistoryReportDTO,
    summary="Estatísticas: nota ao longo da partida",
    description="A nota geral de cada jogador (e de cada equipe) no fim de cada mês, a partir do primeiro mês com nota; o último ponto é a nota de hoje.",
)
def get_score_history(simulation_ids: SimulationIds):
    cache = match_cache(simulation_ids)
    if cache is None:
        return build_score_history_report(simulation_ids)
    return cache.report(
        "score-history",
        lambda: build_score_history_report(simulation_ids, cache.closed_scores),
    )


@statistics_router.get(
    "/statistics/composition",
    response_model=CompositionReportDTO,
    summary="Estatísticas: composição",
    description="Caixa, renda variável e renda fixa de cada jogador dia a dia, e a exposição e o lucro por setor. Numa simulação só com mais de um ano, as séries trazem o fechamento de cada semana (até cinco anos) ou de cada mês.",
)
def get_composition(simulation_ids: SimulationIds):
    return _report(simulation_ids, "composition", build_composition_report)


@statistics_router.get(
    "/statistics/operations",
    response_model=OperationsReportDTO,
    summary="Estatísticas: operações",
    description="Negócios executados, volume por mês, giro, IR pago e custo de impacto de cada jogador.",
)
def get_operations(simulation_ids: SimulationIds):
    return _report(simulation_ids, "operations", build_operations_report)


@statistics_router.get(
    "/statistics/bots",
    response_model=list[BotReportDTO],
    summary="Estatísticas: bots",
    description="Os bots das simulações informadas: a estratégia em que terminaram, os parâmetros com rótulo e unidade, quem os adicionou e se o log de ordens já abriu.",
)
def get_bots(simulation_ids: SimulationIds):
    return build_bots_report(simulation_ids)


@statistics_router.get(
    "/statistics/bots/log",
    response_model=StrategyLogPageDTO,
    summary="Estatísticas: log de ordens do bot",
    description="As ordens que o bot enviou, da mais recente para a mais antiga. Recusa com 403 enquanto a partida corre e com 404 quem não é bot dela.",
)
def get_bot_log(
    simulation_id: int,
    nickname: str,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
):
    return bot_orders(simulation_id, nickname, offset, limit)


@statistics_router.get(
    "/statistics/next-update",
    response_model=StatisticsNextUpdateDTO,
    summary="Estatísticas: próxima atualização",
    description="Dia da partida em que as estatísticas fecham o mês de novo; nulo quando a partida termina antes.",
)
def get_next_update(simulation: ActiveSimulation):
    return StatisticsNextUpdateDTO(next_update_date=simulation.next_statistics_update())


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


@statistics_router.get(
    "/economy",
    response_model=EconomyPanelDTO,
    summary="Obter o painel da economia",
    description="A SELIC, o IPCA de 12 meses, o juro real, a meta de inflação, o crescimento do PIB e o desemprego, um ponto por mês desde o início da partida até hoje, os dias em que o Copom mudou a SELIC e o que puxa o crescimento hoje. Nas partidas com a expansão Governo & Política, traz também a dívida em % do PIB e o prêmio de risco de cada ponto e o resumo da dívida.",
)
def get_economy(simulation: ActiveSimulation):
    return simulation.get_economy_panel()
