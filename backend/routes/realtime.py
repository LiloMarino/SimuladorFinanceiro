from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.core.dependencies import ClientID
from backend.core.logger import setup_logger
from backend.features.realtime import get_broker, get_sse_broker

realtime_router = APIRouter(prefix="/api", tags=["Realtime"])

logger = setup_logger(__name__)


class UpdateSubscriptionRequest(BaseModel):
    client_id: str
    events: list[str] = []


@realtime_router.get("/stream")
def stream(client_id: ClientID):
    """SSE stream endpoint - retorna eventos em tempo real."""
    broker = get_sse_broker()
    return broker.connect(client_id)


@realtime_router.post("/update-subscription")
def update_subscription(payload: UpdateSubscriptionRequest):
    """Atualiza os eventos que um cliente está inscrito."""
    broker = get_broker()
    client_id = payload.client_id
    events = payload.events

    broker.update_subscription(client_id, events)
    logger.info("Updating subscription: %s -> %s", client_id, events)
    return JSONResponse(content={"data": {"client_id": client_id, "events": events}})
