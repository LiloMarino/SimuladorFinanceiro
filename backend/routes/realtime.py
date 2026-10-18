import logging

from fastapi import APIRouter, HTTPException

from backend.features.realtime.schemas import RealtimeEventCatalog

realtime_router = APIRouter(prefix="/api", tags=["Realtime"])

logger = logging.getLogger(__name__)


@realtime_router.get(
    "/internal/realtime-events-schema",
    response_model=RealtimeEventCatalog,
    include_in_schema=True,
    summary="[DEV] Catálogo de payloads de eventos realtime",
    description=(
        "Existe apenas para expor os schemas dos payloads WebSocket no OpenAPI e "
        "alimentar `pnpm run types:generate` (types/events.ts). Nunca deve ser "
        "chamada por clientes reais."
    ),
)
def get_realtime_events_schema():
    raise HTTPException(
        status_code=501,
        detail="Rota existe apenas para geração de schema OpenAPI.",
    )
