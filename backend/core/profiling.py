"""
Perfis do cProfile para o modo debug: o tempo de cada função, gravado em `profiles/`
para abrir no snakeviz (`pnpm profile:view profiles/<arquivo>.prof`).

Dois perfis usam o mesmo `Profiler`: o de uma requisição (`?profile=1` numa rota) e o do
motor (gravado por um botão do painel de desempenho). No Python 3.12+ o cProfile é do
interpretador inteiro: enquanto um perfil está ligado, ele conta as funções de todas as
threads (o motor, o event loop e as rotas), e só um perfil fica ligado por vez. O tempo
medido inclui o custo do próprio cProfile: o perfil dá as proporções entre as funções,
e a medida em milissegundos fica com o painel de desempenho.
"""

import cProfile
import inspect
import logging
import re
import threading
from collections.abc import Callable, Generator
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

from fastapi import FastAPI
from fastapi.routing import APIRoute, RouteContext, iter_route_contexts
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)

PROFILES_DIR = Path("profiles")


class Profiler:
    """Um cProfile por vez, gravado em `PROFILES_DIR/<nome>-<hora>.prof` ao parar."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._profile: cProfile.Profile | None = None
        self._name = ""

    @property
    def active(self) -> bool:
        return self._profile is not None

    def start(self, name: str) -> bool:
        """Liga o perfil; falso quando outro já está ligado."""
        with self._lock:
            if self._profile is not None:
                return False
            profile = cProfile.Profile()
            try:
                profile.enable()
            except ValueError:
                # Outra ferramenta (ex.: `python -m cProfile`) já tem o perfil do interpretador
                return False
            self._profile = profile
            self._name = name
            return True

    def stop(self) -> Path | None:
        """Desliga o perfil e grava o arquivo; vazio quando não havia perfil ligado."""
        with self._lock:
            profile, name = self._profile, self._name
            if profile is None:
                return None
            profile.disable()
            self._profile = None
        PROFILES_DIR.mkdir(exist_ok=True)
        path = PROFILES_DIR / f"{name}-{datetime.now().astimezone():%Y%m%d-%H%M%S}.prof"
        profile.dump_stats(path)
        logger.info("Perfil gravado em %s", path)
        return path

    @contextmanager
    def capture(self, name: str) -> Generator[None]:
        """Perfila o bloco, se nenhum outro perfil estiver ligado."""
        if not self.start(name):
            yield
            return
        try:
            yield
        finally:
            self.stop()


profiler = Profiler()

# Verdadeiro nas requisições que pediram `?profile=1`; vale na thread do handler
# porque o FastAPI roda o handler sync numa thread com uma cópia do contexto.
_profile_requested: ContextVar[bool] = ContextVar("profile_requested", default=False)


class ProfileRequestMiddleware:
    """ASGI puro: marca as requisições com `?profile=1` para o handler da rota se perfilar."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        query = parse_qs(scope.get("query_string", b"").decode())
        token = _profile_requested.set("1" in query.get("profile", []))
        try:
            await self.app(scope, receive, send)
        finally:
            _profile_requested.reset(token)


def _route_slug(route: RouteContext) -> str:
    method = min(route.methods or {"GET"}).lower()
    return re.sub(r"\W+", "-", f"{method}{route.path}").strip("-")


def _profiled(function: Callable[..., Any], name: str) -> Callable[..., Any]:
    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not _profile_requested.get():
            return function(*args, **kwargs)
        with profiler.capture(name):
            return function(*args, **kwargs)

    return wrapper


def profile_routes(app: FastAPI) -> None:
    """
    Faz cada handler `def` da API gravar o perfil quando a requisição traz `?profile=1`.
    O perfil cobre só a chamada do handler: o `build_*` da rota aparece, o uvicorn não.
    """
    # `app.routes` traz as rotas dos routers incluídos agrupadas; o contexto de cada uma
    # carrega o `dependant` que a requisição executa
    for route in iter_route_contexts(app.routes):
        if not isinstance(route.original_route, APIRoute) or route.dependant is None:
            continue
        # A API é de handlers `def`; os `async def` (o túnel) ficam sem `?profile=1`
        if (route.path or "").startswith("/api/") and not inspect.iscoroutinefunction(
            route.dependant.call
        ):
            route.dependant.call = _profiled(route.dependant.call, _route_slug(route))
