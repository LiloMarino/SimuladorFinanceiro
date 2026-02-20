import logging
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel

from backend.core.dependencies import ClientID
from backend.features.realtime import get_broker, get_sse_broker

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
