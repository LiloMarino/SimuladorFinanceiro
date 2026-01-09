"""
Real-time communication routes for FastAPI (SSE).
Migrated from Flask Blueprint to FastAPI APIRouter.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from backend.core.exceptions.fastapi_exceptions import BadRequestError
from backend.core.logger import setup_logger
from backend.features.realtime import get_broker, get_sse_broker
from backend.routes.fastapi_helpers import make_response_data

router = APIRouter(prefix="/api", tags=["realtime"])

logger = setup_logger(__name__)


class UpdateSubscriptionRequest(BaseModel):
    client_id: str
    events: list[str]


@router.get("/stream")
async def stream():
    """SSE stream endpoint."""
    broker = get_sse_broker()
    return broker.connect()


@router.post("/update-subscription")
async def update_subscription(request: UpdateSubscriptionRequest):
    """Update client's event subscriptions."""
    broker = get_broker()
    client_id = request.client_id
    events = request.events

    if not client_id:
        raise BadRequestError("client_id required")

    broker.update_subscription(client_id, events)
    logger.info("Updating subscription: %s -> %s", client_id, events)
    return make_response_data(
        True,
        "Subscription updated",
        data={"client_id": client_id, "events": events},
    )
