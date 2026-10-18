"""
Painel de desempenho: medições em memória de onde o tempo vai numa partida.

Três origens alimentam o coletor: as requisições HTTP (o `MetricsMiddleware`, agrupadas
pela rota declarada), o Socket.IO (o tempo de cada evento recebido e o volume dos
enviados) e o motor (quanto leva para processar um dia). Só mede com o modo debug
ligado: desligado, `enabled` é falso, o middleware nem é instalado e nada é guardado.
"""

import inspect
import logging
import math
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any, Literal

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

# Nome fixo (não o do módulo): é o prefixo que a tabela AREA_LOGGERS leva ao slow.log
slow_logger = logging.getLogger("backend.metrics")

Kind = Literal["http", "socket", "engine"]

WINDOW_SIZE = 1000  # medições guardadas por item
SLOW_MS = 500.0  # uma chamada acima disso vai para o slow.log
TRAFFIC_WINDOW_SECONDS = 10.0  # janela das taxas de mensagens enviadas
ENGINE_DAY = "Processar um dia"

# O stream SSE dura a conexão inteira e o debug não se mede a si mesmo
_IGNORED_PREFIXES = ("/api/stream", "/api/debug")


@dataclass(frozen=True)
class Stat:
    kind: Kind
    name: str
    calls: int
    total_ms: float
    mean_ms: float
    p95_ms: float
    max_ms: float


@dataclass(frozen=True)
class Traffic:
    event: str
    msgs_per_s: float
    bytes_per_s: float
    bytes_per_msg: float


@dataclass(frozen=True)
class Snapshot:
    stats: list[Stat]
    traffic: list[Traffic]
    # p95 de todas as chamadas de cada origem juntas (o p95 por item não se soma)
    overall_p95: dict[Kind, float]
    engine_speed: float


def percentile_95(values: list[float]) -> float:
    """Posto mais próximo: 95% das medições levam até esse tempo."""
    ordered = sorted(values)
    return ordered[math.ceil(0.95 * len(ordered)) - 1]


def _traffic_event(event: str) -> str:
    """`stock_update:PETR4` e `stock_update:VALE3` são o mesmo evento para o painel."""
    base, separator, _ = event.partition(":")
    return f"{base}:*" if separator else event


class Metrics:
    def __init__(self) -> None:
        self.enabled = False
        self._lock = threading.Lock()
        self._durations: dict[tuple[Kind, str], deque[float]] = defaultdict(
            lambda: deque(maxlen=WINDOW_SIZE)
        )
        # event -> (instante, mensagens, bytes) de cada envio dentro da janela
        self._sent: dict[str, deque[tuple[float, int, int]]] = defaultdict(deque)
        self._sent_since: float | None = None
        self._engine_speed = 0.0

    # -- escrita ----------------------------------------------------------------

    def record(self, kind: Kind, name: str, duration_ms: float) -> None:
        if not self.enabled:
            return
        with self._lock:
            self._durations[(kind, name)].append(duration_ms)
        if duration_ms > SLOW_MS:
            slow_logger.warning(
                "Lenta: %s %s levou %.0f ms (limite %.0f ms)",
                kind,
                name,
                duration_ms,
                SLOW_MS,
            )

    def record_sent(self, event: str, messages: int, bytes_each: int) -> None:
        """Um envio de `messages` cópias de `bytes_each` bytes (uma por destinatário)."""
        if not self.enabled or messages <= 0:
            return
        now = time.monotonic()
        with self._lock:
            if self._sent_since is None:
                self._sent_since = now
            self._sent[_traffic_event(event)].append(
                (now, messages, messages * bytes_each)
            )
            self._prune(now)

    def set_engine_speed(self, speed: float) -> None:
        self._engine_speed = speed

    def reset(self) -> None:
        with self._lock:
            self._durations.clear()
            self._sent.clear()
            self._sent_since = None

    def measure(self, kind: Kind, name: str) -> "_Measure | _NoMeasure":
        """Mede o bloco, mesmo se ele levantar (o `StopIteration` do motor passa)."""
        if not self.enabled:
            return _NO_MEASURE  # modo normal: sem alocar nada por tick
        return _Measure(self, kind, name)

    def timed(self, kind: Kind, name: str) -> Callable[[Callable[..., Any]], Any]:
        """Decorator de `measure` para função síncrona ou `async`."""

        def decorate(function: Callable[..., Any]) -> Callable[..., Any]:
            if inspect.iscoroutinefunction(function):

                @wraps(function)
                async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                    with self.measure(kind, name):
                        return await function(*args, **kwargs)

                return async_wrapper

            @wraps(function)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                with self.measure(kind, name):
                    return function(*args, **kwargs)

            return wrapper

        return decorate

    # -- leitura ----------------------------------------------------------------

    def snapshot(self) -> Snapshot:
        with self._lock:
            now = time.monotonic()
            self._prune(now)
            windows = {key: list(window) for key, window in self._durations.items()}
            stats = [
                _stat(kind, name, window)
                for (kind, name), window in windows.items()
                if window
            ]
            by_kind: dict[Kind, list[float]] = defaultdict(list)
            for (kind, _), window in windows.items():
                by_kind[kind].extend(window)
            elapsed = self._traffic_elapsed(now)
            traffic = [
                _traffic(event, sends, elapsed)
                for event, sends in self._sent.items()
                if sends
            ]
        overall: dict[Kind, float] = {
            kind: percentile_95(values) for kind, values in by_kind.items() if values
        }
        return Snapshot(stats, traffic, overall, self._engine_speed)

    def _prune(self, now: float) -> None:
        limit = now - TRAFFIC_WINDOW_SECONDS
        for sends in self._sent.values():
            while sends and sends[0][0] < limit:
                sends.popleft()

    def _traffic_elapsed(self, now: float) -> float:
        # Nos primeiros segundos a janela ainda não encheu: divide pelo que já passou
        since = self._sent_since if self._sent_since is not None else now
        return max(1.0, min(TRAFFIC_WINDOW_SECONDS, now - since))


class _NoMeasure:
    """O `measure` do modo normal: um objeto só, que não faz nada."""

    def __enter__(self) -> None:
        return None

    def __exit__(self, *exc: object) -> None:
        return None


_NO_MEASURE = _NoMeasure()


class _Measure:
    def __init__(self, collector: "Metrics", kind: Kind, name: str) -> None:
        self._collector = collector
        self._kind: Kind = kind
        self._name = name
        self._start = 0.0

    def __enter__(self) -> None:
        self._start = time.perf_counter()

    def __exit__(self, *exc: object) -> None:
        elapsed = (time.perf_counter() - self._start) * 1000
        self._collector.record(self._kind, self._name, elapsed)


def _stat(kind: Kind, name: str, window: list[float]) -> Stat:
    total = sum(window)
    return Stat(
        kind=kind,
        name=name,
        calls=len(window),
        total_ms=total,
        mean_ms=total / len(window),
        p95_ms=percentile_95(window),
        max_ms=max(window),
    )


def _traffic(
    event: str, sends: deque[tuple[float, int, int]], elapsed: float
) -> Traffic:
    messages = sum(count for _, count, _ in sends)
    size = sum(total for _, _, total in sends)
    return Traffic(
        event=event,
        msgs_per_s=messages / elapsed,
        bytes_per_s=size / elapsed,
        bytes_per_msg=size / messages,
    )


metrics = Metrics()


class MetricsMiddleware:
    """
    ASGI puro, só HTTP: mede cada requisição pela rota declarada (`/api/stocks/{ticker}`,
    não o ticker) e devolve o tempo do servidor no cabeçalho `Server-Timing`, que a
    aba Rede do DevTools já mostra. Um 500 tratado pelo handler de `Exception` é
    respondido por fora daqui: conta na medição, mas fica sem o cabeçalho.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()

        async def send_with_timing(message: Message) -> None:
            if message["type"] == "http.response.start":
                elapsed = (time.perf_counter() - start) * 1000
                MutableHeaders(scope=message).append(
                    "Server-Timing", f"app;dur={elapsed:.1f}"
                )
            await send(message)

        try:
            await self.app(scope, receive, send_with_timing)
        finally:
            # O roteador grava a rota casada no mesmo `scope` que recebeu
            path = getattr(scope.get("route"), "path", None)
            if (
                isinstance(path, str)
                and path.startswith("/api/")
                and not path.startswith(_IGNORED_PREFIXES)
            ):
                elapsed = (time.perf_counter() - start) * 1000
                metrics.record("http", f"{scope['method']} {path}", elapsed)
