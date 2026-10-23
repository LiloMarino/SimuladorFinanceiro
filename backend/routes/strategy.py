from typing import Annotated

from fastapi import APIRouter, Query, status

from backend.core.dependencies import ActiveSimulation, CurrentUser
from backend.core.dto.strategy import (
    MyStrategyDTO,
    SetStrategyRequestDTO,
    SignalDTO,
    SignalRequestDTO,
    StrategyInfoDTO,
    StrategyLogPageDTO,
)
from backend.core.repository.strategy import LogFilter

strategy_router = APIRouter(prefix="/api/strategies", tags=["Strategy"])


@strategy_router.get(
    "",
    response_model=list[StrategyInfoDTO],
    summary="Listar as estratégias",
    description="Retorna as estratégias do app, com a regra, os parâmetros, a faixa de cada um e o padrão calculado para a partida.",
)
def list_strategies(simulation: ActiveSimulation):
    return simulation.get_strategies()


@strategy_router.get(
    "/me",
    response_model=MyStrategyDTO,
    summary="Obter a minha estratégia",
    description="Retorna a estratégia que o jogador deixou ligada (ou nenhuma, no modo manual), o erro que o devolveu ao manual e o painel desde que ligou.",
)
def get_my_strategy(simulation: ActiveSimulation, user: CurrentUser):
    return simulation.get_my_strategy(user)


@strategy_router.put(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Ligar, ajustar ou desligar a estratégia",
    description="Liga a estratégia com os parâmetros, troca por outra, ajusta os parâmetros ou, sem chave, volta ao manual. Ligar, trocar e desligar cancelam as ordens abertas do jogador.",
)
def set_my_strategy(
    simulation: ActiveSimulation, user: CurrentUser, payload: SetStrategyRequestDTO
):
    simulation.set_my_strategy(user, payload.key, payload.params)


@strategy_router.post(
    "/me/error-seen",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Marcar o erro como visto",
    description="Registra que o jogador viu o erro que desligou a estratégia, para o aviso do menu sair.",
)
def mark_error_seen(simulation: ActiveSimulation, user: CurrentUser):
    simulation.mark_strategy_error_seen(user)


@strategy_router.post(
    "/{key}/signal",
    response_model=SignalDTO,
    summary="Calcular o sinal de uma estratégia",
    description="Valida os parâmetros e devolve as linhas e os marcadores que a estratégia desenha no ativo, sem salvar nada.",
)
def get_signal(simulation: ActiveSimulation, key: str, payload: SignalRequestDTO):
    return simulation.get_strategy_signal(key, payload.params, payload.ticker)


@strategy_router.get(
    "/me/log",
    response_model=StrategyLogPageDTO,
    summary="Listar o registro da estratégia",
    description="Retorna, da mais recente para a mais antiga, as ordens enviadas pela estratégia e as mudanças de modo do jogador.",
)
def get_strategy_log(
    simulation: ActiveSimulation,
    user: CurrentUser,
    kind: Annotated[LogFilter, Query()] = "all",
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
):
    return simulation.get_strategy_log(user, kind, offset, limit)
