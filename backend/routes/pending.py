from fastapi import APIRouter

from backend.core.dependencies import ActiveSimulation, CurrentUser
from backend.core.dto.pending import PendingDTO

pending_router = APIRouter(prefix="/api/pending", tags=["Pending"])


@pending_router.get(
    "",
    response_model=list[PendingDTO],
    summary="Pendências do jogador",
    description="O que pede ação do jogador agora, das graves para as de aviso: parcela em atraso, caixa negativo ou curto, estratégia desligada por erro, risco de impeachment, convite de vice e campanha aberta sem filiação.",
)
def get_pending(simulation: ActiveSimulation, user: CurrentUser):
    return simulation.get_pending(user)
