"""
Simulador Financeiro - FastAPI Application

Copyright (C) 2025 Murilo Marino

Este programa é software livre: você pode redistribuí-lo e/ou modificá-lo
sob os termos da Licença Pública Geral GNU publicada pela Free Software Foundation,
na versão 3 da licença, ou (a seu critério) qualquer versão posterior.

Este programa é distribuído na esperança de que seja útil,
mas SEM NENHUMA GARANTIA; sem mesmo a garantia implícita de
COMERCIALIZAÇÃO ou ADEQUAÇÃO A UM DETERMINADO PROPÓSITO.
Consulte a Licença Pública Geral GNU para mais detalhes.

Você deve ter recebido uma cópia da Licença Pública Geral GNU
junto com este programa. Caso não, veja <https://www.gnu.org/licenses/>.
"""

import secrets
from pathlib import Path

import socketio
import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend import config
from backend.core.database import engine
from backend.core.exceptions.http_exceptions import HTTPError
from backend.core.logger import setup_logger
from backend.features.realtime.sse_broker import SSEBroker
from backend.features.realtime.ws_broker_asgi import SocketBrokerASGI
from backend.features.realtime.ws_handlers_asgi import register_ws_handlers
from backend.features.simulation.simulation_loop import controller
from backend.routes.auth import auth_router
from backend.routes.importer import import_router
from backend.routes.operation import operation_router
from backend.routes.portfolio import portfolio_router
from backend.routes.realtime import realtime_router
from backend.routes.settings import settings_router
from backend.routes.simulation import simulation_router
from backend.routes.statistics import statistics_router
from backend.routes.timespeed import timespeed_router

SECRET_PATH = Path("secret.key")

logger = setup_logger(__name__)

# Global broker storage
_realtime_broker = None
_sio = None


def get_secret_key():
    """Garante a persistência de uma secret key local."""
    if SECRET_PATH.exists():
        return SECRET_PATH.read_text()
    secret_key = secrets.token_hex(16)
    SECRET_PATH.write_text(secret_key)
    return secret_key


def get_broker():
    """Get the global realtime broker instance."""
    if _realtime_broker is None:
        raise RuntimeError("RealtimeBroker não está inicializado")
    return _realtime_broker


def get_socket_broker():
    """Get the socket broker if using WebSocket mode."""
    broker = get_broker()
    if not isinstance(broker, SocketBrokerASGI):
        raise TypeError("Broker não é SocketBroker")
    return broker


def get_sse_broker():
    """Get the SSE broker if using SSE mode."""
    broker = get_broker()
    if not isinstance(broker, SSEBroker):
        raise TypeError("Broker não é SSEBroker")
    return broker


def create_app():
    """Create and configure the application."""
    global _realtime_broker, _sio

    backend = engine.url.get_backend_name()
    logger.info(f"Banco de dados em uso: {backend.upper()} ({engine.url})")

    # Create FastAPI app
    fastapi_app = FastAPI(
        title="Simulador Financeiro",
        description="Financial Simulator API with real-time capabilities",
        version="1.0.0",
    )

    # CORS middleware
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    fastapi_app.include_router(auth_router)
    fastapi_app.include_router(simulation_router)
    fastapi_app.include_router(portfolio_router)
    fastapi_app.include_router(operation_router)
    fastapi_app.include_router(settings_router)
    fastapi_app.include_router(timespeed_router)
    fastapi_app.include_router(statistics_router)
    fastapi_app.include_router(import_router)
    fastapi_app.include_router(realtime_router)

    # Exception handlers
    @fastapi_app.exception_handler(HTTPError)
    async def http_error_handler(request: Request, exc: HTTPError):
        """Handle custom HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "message": exc.detail,
                "data": None,
            },
        )

    @fastapi_app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions."""
        logger.exception(f"{exc.__class__.__name__}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": str(exc),
                "data": None,
            },
        )

    # Initialize broker and simulation loop
    controller.bind_app(fastapi_app)
    controller.start_loop()

    # Initialize realtime broker based on config
    if not config.toml.realtime.use_sse:
        # WebSocket mode with python-socketio ASGI
        _sio = socketio.AsyncServer(
            async_mode="asgi",
            cors_allowed_origins="*",
            logger=False,
            engineio_logger=False,
        )
        _realtime_broker = SocketBrokerASGI(_sio)
        register_ws_handlers(_sio)
        logger.info("Rodando em modo WebSocket (SocketIO ASGI).")

        # Wrap FastAPI with Socket.IO
        app = socketio.ASGIApp(_sio, other_asgi_app=fastapi_app)
    else:
        # SSE mode
        _realtime_broker = SSEBroker()
        logger.info("Rodando em modo SSE (Server-Sent Events).")
        app = fastapi_app

    return app


# Create the app at module level
app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main_fastapi:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload with socket.io
        log_level="info",
    )
