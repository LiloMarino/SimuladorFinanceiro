import os
from datetime import UTC, datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend import config
from backend.core.dependencies import HostVerified
from backend.core.exceptions.http_exceptions import ConflictError, NotFoundError
from backend.core.metrics import metrics
from backend.core.profiling import profiler
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
    # Taxas dos últimos `traffic_window_s` segundos
    msgs_per_s: float
    bytes_per_s: float
    # Desde o boot ou o último reset; um envio vira uma mensagem por destinatário
    sends: int
    unheard: int
    total_bytes: int
    # Sobre os últimos 1.000 envios; vazios enquanto ninguém recebeu o evento
    typical_bytes: float | None
    p95_bytes: float | None
    queue_p95_ms: float | None
    last_sent_at: datetime | None


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
    traffic_window_s: float


def _round(value: float | None, digits: int) -> float | None:
    return round(value, digits) if value is not None else None


@debug_router.get(
    "/metrics",
    summary="Medições de desempenho",
    description=(
        "Tempo gasto pelas requisições HTTP, pelos eventos Socket.IO recebidos e pelo "
        "motor, sobre as últimas 1.000 medições de cada item, e os eventos enviados ao "
        "navegador: a taxa recente e a contagem acumulada desde o último reset. Só com "
        "o modo debug ligado e só para o host."
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
            sends=item.sends,
            unheard=item.unheard,
            total_bytes=item.total_bytes,
            typical_bytes=_round(item.typical_bytes, 1),
            p95_bytes=_round(item.p95_bytes, 1),
            queue_p95_ms=_round(item.queue_p95_ms, 2),
            last_sent_at=(
                datetime.fromtimestamp(item.last_sent_at, UTC)
                if item.last_sent_at is not None
                else None
            ),
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
        traffic_window_s=round(snapshot.traffic_window_s, 1),
    )


@debug_router.post(
    "/metrics/reset",
    status_code=204,
    summary="Zerar as medições",
    description="Apaga as medições guardadas, para medir só um trecho da partida.",
)
def reset_metrics(_debug: DebugOnly, _host: HostVerified) -> None:
    metrics.reset()


class EngineProfileStatus(BaseModel):
    recording: bool


class EngineProfileSaved(BaseModel):
    # Caminho do .prof, para abrir com `pnpm profile:view <arquivo>`
    file: str


@debug_router.get(
    "/profile/engine",
    summary="Estado da gravação do perfil do motor",
    description="Diz se um perfil está sendo gravado agora.",
)
def get_engine_profile(_debug: DebugOnly, _host: HostVerified) -> EngineProfileStatus:
    return EngineProfileStatus(recording=profiler.active)


@debug_router.post(
    "/profile/engine/start",
    status_code=204,
    summary="Começar a gravar o perfil do motor",
    description=(
        "Liga o cProfile: ele conta o tempo de cada função de todas as threads (o dia, "
        "o event loop e as rotas) até a gravação parar. Só um perfil por vez."
    ),
)
def start_engine_profile(_debug: DebugOnly, _host: HostVerified) -> None:
    if not profiler.start("motor"):
        raise ConflictError("Já há um perfil sendo gravado.")


@debug_router.post(
    "/profile/engine/stop",
    summary="Parar e gravar o perfil do motor",
    description="Desliga o cProfile e grava o arquivo `.prof` na pasta `profiles/`.",
)
def stop_engine_profile(_debug: DebugOnly, _host: HostVerified) -> EngineProfileSaved:
    path = profiler.stop()
    if path is None:
        raise ConflictError("Nenhum perfil está sendo gravado.")
    return EngineProfileSaved(file=path.as_posix())
