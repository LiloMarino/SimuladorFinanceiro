from fastapi import APIRouter

from backend.core.dependencies import ActiveSimulation, ClientID
from backend.core.dto.government import (
    GovernmentActionDTO,
    GovernmentPreviewDTO,
    GovernmentViewDTO,
)
from backend.core.exceptions.http_exceptions import ConflictError

government_router = APIRouter(prefix="/api/government", tags=["Government"])


@government_router.post(
    "/preview",
    response_model=GovernmentPreviewDTO,
    summary="Prévia pública de uma medida, sem gravar nem movimentar dinheiro",
)
def government_preview(
    payload: GovernmentActionDTO, simulation: ActiveSimulation, client_id: ClientID
):
    with simulation.lock:
        if not simulation._government:
            raise ConflictError("A expansão Governo está desligada nesta partida.")
        return simulation._government.preview(client_id, payload)


@government_router.get(
    "",
    response_model=GovernmentViewDTO,
    summary="Governo, eleição e efeitos econômicos públicos",
)
def government_view(simulation: ActiveSimulation, client_id: ClientID):
    with simulation.lock:
        if not simulation._government:
            raise ConflictError("A expansão Governo está desligada nesta partida.")
        return simulation._government.view(client_id)


@government_router.post(
    "/actions",
    response_model=GovernmentViewDTO,
    summary="Atuar na política ou propor uma medida como presidente",
)
def government_action(
    payload: GovernmentActionDTO, simulation: ActiveSimulation, client_id: ClientID
):
    with simulation.lock:
        if not simulation._government:
            raise ConflictError("A expansão Governo está desligada nesta partida.")
        return simulation._government.command(client_id, payload)
