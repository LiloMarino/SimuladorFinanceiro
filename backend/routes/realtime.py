from fastapi import APIRouter, status
from pydantic import BaseModel

from backend.core.logger import setup_logger
from backend.fastapi_helpers import make_response
from backend.features.realtime import get_broker, get_sse_broker

realtime_router = APIRouter(prefix="/api", tags=["realtime"])

logger = setup_logger(__name__)


class UpdateSubscriptionRequest(BaseModel):
    client_id: str
    events: list[str] = []


@realtime_router.get("/stream")
def stream():
    broker = get_sse_broker()
    return broker.connect()


@realtime_router.post("/update-subscription")
def update_subscription(payload: UpdateSubscriptionRequest):
    broker = get_broker()

    if not payload.client_id:
        return make_response(
            False, "client_id required", status_code=status.HTTP_400_BAD_REQUEST
        )

    broker.update_subscription(payload.client_id, payload.events)
    logger.info("Updating subscription: %s -> %s", payload.client_id, payload.events)
    return make_response(
        True,
        "Subscription updated",
        data={"client_id": payload.client_id, "events": payload.events},
    )
