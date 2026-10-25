import os
from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend import config
from backend.core.dependencies import HostVerified
from backend.core.exceptions.http_exceptions import NotFoundError
from backend.core.metrics import metrics
from backend.core.runtime.user_manager import UserManager


def require_debug() -> None:
    """Lê o flag a cada requisição (e não no import), para os testes poderem trocá-lo."""
    if not config.toml.debug.enabled:
        raise NotFoundError("O modo debug está desligado.")


DebugOnly = Annotated[None, Depends(require_debug)]

debug_router = APIRouter(prefix="/api/debug", tags=["Debug"])


class MetricItem(BaseModel):
    kind: Literal["http", "socket", "engine"]
    name: str
    calls: int
    total_ms: float
    mean_ms: float
    p95_ms: float
    max_ms: float


class TrafficItem(BaseModel):
    event: str
    msgs_per_s: float
    bytes_per_s: float
    bytes_per_msg: float


class OverallItem(BaseModel):
    kind: Literal["http", "socket", "engine"]
    p95_ms: float


class EngineInfo(BaseModel):
    speed: float
    # Tempo que cabe em cada dia na velocidade pedida; vazio com a partida pausada
    budget_ms: float | None


class MetricsResponse(BaseModel):
    pid: int
    players: int
    engine: EngineInfo
    items: list[MetricItem]
    overall: list[OverallItem]
    traffic: list[TrafficItem]


@debug_router.get(
    "/metrics",
    summary="Medições de desempenho",
    description=(
        "Tempo gasto pelas requisições HTTP, pelos eventos Socket.IO recebidos e pelo "
        "motor, e o volume enviado ao navegador, sobre as últimas 1.000 medições de "
        "cada item. Só com o modo debug ligado e só para o host."
    ),
)
def get_metrics(_debug: DebugOnly, _host: HostVerified) -> MetricsResponse:
    snapshot = metrics.snapshot()
    speed = snapshot.engine_speed
    items = [
        MetricItem(
            kind=stat.kind,
            name=stat.name,
            calls=stat.calls,
            total_ms=round(stat.total_ms, 2),
            mean_ms=round(stat.mean_ms, 2),
            p95_ms=round(stat.p95_ms, 2),
            max_ms=round(stat.max_ms, 2),
        )
        for stat in snapshot.stats
    ]
    traffic = [
        TrafficItem(
            event=item.event,
            msgs_per_s=round(item.msgs_per_s, 2),
            bytes_per_s=round(item.bytes_per_s, 1),
            bytes_per_msg=round(item.bytes_per_msg, 1),
        )
        for item in snapshot.traffic
    ]
    return MetricsResponse(
        pid=os.getpid(),
        players=len(UserManager.list_active_players()),
        engine=EngineInfo(speed=speed, budget_ms=1000 / speed if speed > 0 else None),
        items=items,
        overall=[
            OverallItem(kind=kind, p95_ms=round(p95, 2))
            for kind, p95 in snapshot.overall_p95.items()
        ],
        traffic=traffic,
    )


@debug_router.post(
    "/metrics/reset",
    status_code=204,
    summary="Zerar as medições",
    description="Apaga as medições guardadas, para medir só um trecho da partida.",
)
def reset_metrics(_debug: DebugOnly, _host: HostVerified) -> None:
    metrics.reset()
