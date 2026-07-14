import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.core.dependencies import ClientID
from backend.features.realtime import get_broker, get_sse_broker
from backend.features.realtime.schemas import RealtimeEventCatalog

realtime_router = APIRouter(prefix="/api", tags=["Realtime"])

logger = logging.getLogger(__name__)


class UpdateSubscriptionRequest(BaseModel):
    events: list[str] = []


class UpdateSubscriptionResponse(BaseModel):
    client_id: UUID
    events: list[str]


@realtime_router.get(
    "/stream",
    summary="Stream de eventos SSE",
    description="Retorna um stream de eventos em tempo real via Server-Sent Events (SSE).",
)
def stream(client_id: ClientID):
    """
    Abre um stream de eventos em tempo real via SSE.
    """
    broker = get_sse_broker()
    return broker.connect(client_id)


@realtime_router.post(
    "/update-subscription",
    response_model=UpdateSubscriptionResponse,
    summary="Atualizar inscrição de eventos",
    description="Atualiza a lista de eventos em tempo real que o cliente deseja receber.",
)
def update_subscription(client_id: ClientID, payload: UpdateSubscriptionRequest):
    """
    Atualiza os eventos inscritos pelo cliente.
    """
    broker = get_broker()
    events = payload.events

    broker.update_subscription(client_id, events)
    logger.info("Updating subscription: %s -> %s", client_id, events)
    return UpdateSubscriptionResponse(client_id=client_id, events=events)


@realtime_router.get(
    "/internal/realtime-events-schema",
    response_model=RealtimeEventCatalog,
    include_in_schema=True,
    summary="[DEV] Catálogo de payloads de eventos realtime",
    description=(
        "Existe apenas para expor os schemas dos payloads WS/SSE no OpenAPI e "
        "alimentar `pnpm run types:generate` (types/events.ts). Nunca deve ser "
        "chamada por clientes reais."
    ),
)
def get_realtime_events_schema():
    raise HTTPException(
        status_code=501,
        detail="Rota existe apenas para geração de schema OpenAPI.",
    )
