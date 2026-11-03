"""
Perfis do yappi para o modo debug: o tempo de cada função, gravado em `profiles/` para
abrir no snakeviz (`pnpm profile:view profiles/<arquivo>.prof`).

Dois perfis usam o mesmo `Profiler`: o das rotas (um interruptor no painel; ligado, cada
requisição às rotas da API vira um perfil) e o do motor (gravado por um botão do painel).
No Python 3.12+ o yappi conta as funções de todas as threads; o que separa cada perfil é
a etiqueta (tag) que o yappi carimba em cada chamada, lida de uma ContextVar: a de uma
requisição perfilada, a da thread do motor enquanto grava ou 0 para todo o resto. O
relógio é o de parede: a espera pelo banco entra no tempo da função que a fez.
"""

import inspect
import logging
import re
import threading
import time
from collections import deque
from collections.abc import Callable, Generator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any

import yappi
from fastapi import FastAPI
from fastapi.routing import APIRoute, RouteContext, iter_route_contexts

logger = logging.getLogger(__name__)

PROFILES_DIR = Path("profiles")
MAX_ROUTE_PROFILES = 20
# As rotas do painel se consultam a cada 2 s e ocupariam a lista sozinhas
UNPROFILED_PREFIX = "/api/debug/"

# A etiqueta das chamadas da thread em curso: a da requisição perfilada, o marcador da
# thread do motor ou 0
_UNTAGGED = 0
_ENGINE_THREAD = -1
_tag: ContextVar[int] = ContextVar("profile_tag", default=_UNTAGGED)


@dataclass(frozen=True)
class RouteProfile:
    id: int
    route: str
    created_at: datetime
    duration_ms: float
    file: Path


class Profiler:
    """O yappi fica ligado enquanto o perfil das rotas ou a gravação do motor estiver."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._routes = False
        # Etiqueta da gravação do motor em curso; 0 sem gravação
        self._engine_tag = _UNTAGGED
        self._next_tag = 1
        self._entries: deque[RouteProfile] = deque(maxlen=MAX_ROUTE_PROFILES)

    @property
    def routes_enabled(self) -> bool:
        return self._routes

    @property
    def engine_recording(self) -> bool:
        return self._engine_tag != _UNTAGGED

    def route_profiles(self) -> list[RouteProfile]:
        with self._lock:
            return list(reversed(self._entries))

    def _current_tag(self) -> int:
        tag = _tag.get()
        return self._engine_tag if tag == _ENGINE_THREAD else tag

    def _reserve_tag(self) -> int:
        tag = self._next_tag
        self._next_tag += 1
        return tag

    def _ensure_running(self) -> None:
        if yappi.is_running():
            return
        yappi.clear_stats()
        yappi.set_clock_type("wall")
        yappi.set_tag_callback(self._current_tag)
        yappi.start(builtins=True)

    def _release(self) -> None:
        if not self._routes and self._engine_tag == _UNTAGGED:
            yappi.stop()
            yappi.clear_stats()

    def set_routes_enabled(self, enabled: bool) -> None:
        with self._lock:
            self._routes = enabled
            if enabled:
                self._ensure_running()
            else:
                self._release()

    def start_engine(self) -> bool:
        """Começa a gravar o motor; falso quando já está gravando."""
        with self._lock:
            if self._engine_tag != _UNTAGGED:
                return False
            self._ensure_running()
            self._engine_tag = self._reserve_tag()
            return True

    def stop_engine(self, name: str = "motor") -> Path | None:
        """
        Para a gravação do motor e grava o arquivo; vazio quando não estava gravando ou
        quando nenhum dia rodou durante a gravação (a partida pausada).
        """
        with self._lock:
            tag = self._engine_tag
            if tag == _UNTAGGED:
                return None
            self._engine_tag = _UNTAGGED
            path = self._save(tag, name)
            self._release()
        return path

    @contextmanager
    def capture_engine(self, name: str) -> Generator[None]:
        """Grava o motor durante o bloco, se ninguém estiver gravando."""
        if not self.start_engine():
            yield
            return
        try:
            yield
        finally:
            self.stop_engine(name)

    def _save(self, tag: int, name: str) -> Path | None:
        """Grava as chamadas da etiqueta; vazio quando ela não tem nenhuma."""
        stats = yappi.get_func_stats(tag=tag)
        if stats.empty():
            return None
        PROFILES_DIR.mkdir(exist_ok=True)
        path = (
            PROFILES_DIR
            / f"{name}-{datetime.now().astimezone():%Y%m%d-%H%M%S}-{tag}.prof"
        )
        stats.save(str(path), type="pstat")
        logger.info("Perfil gravado em %s", path)
        return path

    def begin_request(self) -> int:
        """A etiqueta de uma requisição a perfilar; 0 com o perfil das rotas desligado."""
        with self._lock:
            return self._reserve_tag() if self._routes else _UNTAGGED

    def finish_request(self, tag: int, route: str, duration_ms: float) -> None:
        with self._lock:
            # Desligado no meio da requisição, o yappi já descartou as chamadas dela
            path = self._save(tag, _slug(route)) if yappi.is_running() else None
            if path is None:
                return
            if len(self._entries) == self._entries.maxlen:
                self._entries[0].file.unlink(missing_ok=True)
            self._entries.append(
                RouteProfile(tag, route, datetime.now().astimezone(), duration_ms, path)
            )


profiler = Profiler()


def mark_engine_thread() -> None:
    """As chamadas da thread em curso entram no perfil do motor enquanto ele grava."""
    _tag.set(_ENGINE_THREAD)


def _slug(route: str) -> str:
    return re.sub(r"\W+", "-", route.lower()).strip("-")


def _route_label(route: RouteContext) -> str:
    return f"{min(route.methods or {'GET'})} {route.path}"


def _profiled(function: Callable[..., Any], route: str) -> Callable[..., Any]:
    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        tag = profiler.begin_request()
        if not tag:
            return function(*args, **kwargs)
        # A etiqueta vale antes da chamada: o yappi carimba cada função ao entrar nela
        token = _tag.set(tag)
        started = time.perf_counter()
        try:
            return function(*args, **kwargs)
        finally:
            _tag.reset(token)
            profiler.finish_request(tag, route, (time.perf_counter() - started) * 1000)

    return wrapper


def profile_routes(app: FastAPI) -> None:
    """
    Faz cada handler `def` da API gravar o perfil com o perfil das rotas ligado. O perfil
    cobre só a chamada do handler: o `build_*` da rota aparece, o uvicorn não.
    """
    # `app.routes` traz as rotas dos routers incluídos agrupadas; o contexto de cada uma
    # carrega o `dependant` que a requisição executa
    for route in iter_route_contexts(app.routes):
        if not isinstance(route.original_route, APIRoute) or route.dependant is None:
            continue
        path = route.path or ""
        # A API é de handlers `def`; os `async def` (o túnel) ficam sem perfil
        if (
            path.startswith("/api/")
            and not path.startswith(UNPROFILED_PREFIX)
            and not inspect.iscoroutinefunction(route.dependant.call)
        ):
            route.dependant.call = _profiled(route.dependant.call, _route_label(route))
