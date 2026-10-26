from fastapi import APIRouter, status

from backend.core import repository
from backend.core.dependencies import ActiveSimulation, CurrentUser
from backend.core.dto.inbox import InboxDTO
from backend.core.exceptions.http_exceptions import NotFoundError
from backend.features.inbox.service import inbox_of

inbox_router = APIRouter(prefix="/api/inbox", tags=["Inbox"])


@inbox_router.get(
    "",
    response_model=InboxDTO,
    summary="Caixa de entrada",
    description="As entradas do jogador e as da sala na partida em andamento, da mais nova para a mais antiga, com quantas ainda não foram lidas.",
)
def get_inbox(simulation: ActiveSimulation, user: CurrentUser):
    return inbox_of(simulation.settings.id, user.id)


@inbox_router.post(
    "/read",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Marcar todas como lidas",
    description="Marca como lidas todas as entradas do jogador na partida em andamento.",
)
def mark_all_read(simulation: ActiveSimulation, user: CurrentUser):
    repository.inbox.mark_all_read(simulation.settings.id, user.id)


@inbox_router.post(
    "/{entry_id}/read",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Marcar uma entrada como lida",
    description="Chamado ao abrir a entrada na caixa de entrada.",
)
def mark_read(entry_id: int, simulation: ActiveSimulation, user: CurrentUser):
    if not repository.inbox.mark_read(simulation.settings.id, user.id, entry_id):
        raise NotFoundError("Essa entrada não está na sua caixa de entrada.")
