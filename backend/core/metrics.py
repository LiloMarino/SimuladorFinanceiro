"""
Painel de desempenho: medições em memória de onde o tempo vai numa partida.

Três origens alimentam o coletor: as requisições HTTP (o `MetricsMiddleware`, agrupadas
pela rota declarada), o Socket.IO (o tempo de cada evento recebido e, dos enviados, a
contagem, o tamanho e o atraso na fila) e o motor (quanto leva para processar um dia).
Só mede com o modo debug ligado: desligado, `enabled` é falso, o middleware nem é
instalado e nada é guardado.
"""

import inspect
import logging
import math
import statistics
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable, Iterable
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
# Etapas do ENGINE_DAY: cada uma mede um bloco do tick e já está dentro do tempo do dia
ENGINE_PRICES = "Preços e impacto"
ENGINE_FIXED_INCOME = "Renda fixa"
ENGINE_BOTS = "Bots e estratégias"
ENGINE_CONTRIBUTION = "Aporte e crédito"
ENGINE_GOVERNMENT = "Governo e eleição"
ENGINE_TAXES = "Imposto e caixa"
ENGINE_NEWS = "Notícias"
ENGINE_BACKTEST_DAY = "Dia do backtest"
ENGINE_SNAPSHOTS = "Snapshots do dia"
ENGINE_PUBLISH = "Publicar o dia"  # monta e envia os eventos do dia
ENGINE_GOAL = "Meta"
ENGINE_SUMMARIES = "Retrospectiva do ano"
ENGINE_ACHIEVEMENTS = "Conquistas"

# O debug não se mede a si mesmo
_IGNORED_PREFIXES = ("/api/debug",)


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
    # Taxas da janela recente
    msgs_per_s: float
    bytes_per_s: float
    # Acumulado desde o boot ou o último reset
    sends: int
    unheard: int
    total_bytes: int
    # Sobre as últimas WINDOW_SIZE amostras; vazio enquanto ninguém recebeu o evento
    typical_bytes: float | None
    p95_bytes: float | None
    queue_p95_ms: float | None
    last_sent_at: float | None


@dataclass(frozen=True)
class Snapshot:
    stats: list[Stat]
    traffic: list[Traffic]
    # p95 de todas as chamadas de cada origem juntas (o p95 por item não se soma)
    overall_p95: dict[Kind, float]
    engine_speed: float
    # Segundos que as taxas de `traffic` cobrem
    traffic_window_s: float


def percentile_95(values: Iterable[float]) -> float:
    """Posto mais próximo: 95% das medições levam até esse tempo."""
    ordered = sorted(values)
    return ordered[math.ceil(0.95 * len(ordered)) - 1]


def _traffic_event(event: str) -> str:
    """`stock_update:PETR4` e `stock_update:VALE3` são o mesmo evento para o painel."""
    base, separator, _ = event.partition(":")
    return f"{base}:*" if separator else event


class _SentLog:
    """Tudo o que se sabe de um evento enviado; a janela esvazia, o resto fica."""

    def __init__(self) -> None:
        # (instante, mensagens, bytes) de cada envio dentro da janela
        self.window: deque[tuple[float, int, int]] = deque()
        self.sends = 0
        self.unheard = 0
        self.total_bytes = 0
        self.sizes: deque[float] = deque(maxlen=WINDOW_SIZE)
        self.lags: deque[float] = deque(maxlen=WINDOW_SIZE)
        self.last_sent_at: float | None = None


class Metrics:
    def __init__(self) -> None:
        self.enabled = False
        self._lock = threading.Lock()
        self._durations: dict[tuple[Kind, str], deque[float]] = defaultdict(
            lambda: deque(maxlen=WINDOW_SIZE)
        )
        self._sent: dict[str, _SentLog] = defaultdict(_SentLog)
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
        """
        Um envio de `messages` cópias de `bytes_each` bytes (uma por destinatário).
        Zero cópias é um envio que ninguém assinava: conta só como envio sem ninguém.
        """
        if not self.enabled:
            return
        now = time.monotonic()
        with self._lock:
            log = self._sent[_traffic_event(event)]
            log.sends += 1
            if messages <= 0:
                log.unheard += 1
                return
            if self._sent_since is None:
                self._sent_since = now
            size = messages * bytes_each
            log.window.append((now, messages, size))
            log.total_bytes += size
            log.sizes.append(bytes_each)
            log.last_sent_at = time.time()
            self._prune(now)

    def record_queue(self, event: str, lag_ms: float) -> None:
        """Tempo entre o `notify` e a mensagem entregue ao socket de um destinatário."""
        if not self.enabled:
            return
        with self._lock:
            self._sent[_traffic_event(event)].lags.append(lag_ms)

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
                _traffic(event, log, elapsed) for event, log in self._sent.items()
            ]
        overall: dict[Kind, float] = {
            kind: percentile_95(values) for kind, values in by_kind.items() if values
        }
        return Snapshot(stats, traffic, overall, self._engine_speed, elapsed)

    def _prune(self, now: float) -> None:
        limit = now - TRAFFIC_WINDOW_SECONDS
        for log in self._sent.values():
            while log.window and log.window[0][0] < limit:
                log.window.popleft()

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


def _traffic(event: str, log: _SentLog, elapsed: float) -> Traffic:
    messages = sum(count for _, count, _ in log.window)
    size = sum(total for _, _, total in log.window)
    return Traffic(
        event=event,
        msgs_per_s=messages / elapsed,
        bytes_per_s=size / elapsed,
        sends=log.sends,
        unheard=log.unheard,
        total_bytes=log.total_bytes,
        typical_bytes=statistics.median(log.sizes) if log.sizes else None,
        p95_bytes=percentile_95(log.sizes) if log.sizes else None,
        queue_p95_ms=percentile_95(log.lags) if log.lags else None,
        last_sent_at=log.last_sent_at,
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
