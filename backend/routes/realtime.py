from fastapi import APIRouter, Request
from pydantic import BaseModel

from backend.core.logger import setup_logger
from backend.features.realtime import get_broker, get_sse_broker
from backend.routes.helpers import make_response

realtime_router = APIRouter(prefix="/api", tags=["Realtime"])

logger = setup_logger(__name__)


class UpdateSubscriptionRequest(BaseModel):
    client_id: str
    events: list[str] = []


@realtime_router.get("/stream")
def stream(request: Request):
    """SSE stream endpoint - retorna eventos em tempo real."""
    broker = get_sse_broker()
    return broker.connect(request)


@realtime_router.post("/update-subscription")
def update_subscription(payload: UpdateSubscriptionRequest):
    """Atualiza os eventos que um cliente está inscrito."""
    broker = get_broker()
    client_id = payload.client_id
    events = payload.events

    broker.update_subscription(client_id, events)
    logger.info("Updating subscription: %s -> %s", client_id, events)
    return make_response(
        True,
        "Subscription updated",
        data={"client_id": client_id, "events": events},
    )
