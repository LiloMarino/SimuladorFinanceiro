"""
Simulador Financeiro - FastAPI Main Application

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

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from backend import config
from backend.core.database import engine
from backend.core.logger import setup_logger
from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.features.realtime.sse_broker import SSEBroker
from backend.features.simulation.simulation_loop import controller

SECRET_PATH = Path("secret.key")

logger = setup_logger(__name__)


def get_secret_key():
    """Garante a persistência de uma secret key local."""
    if SECRET_PATH.exists():
        return SECRET_PATH.read_text()
    secret_key = secrets.token_hex(16)
    SECRET_PATH.write_text(secret_key)
    return secret_key


def create_app() -> FastAPI:
    """Cria e configura a aplicação FastAPI."""
    app = FastAPI(
        title="Simulador Financeiro API",
        description="API para simulação financeira com suporte a múltiplos usuários",
        version="1.0.0",
    )

    # Import and register routers
    from backend.routes.fastapi_auth import router as auth_router
    from backend.routes.fastapi_importer import router as importer_router
    from backend.routes.fastapi_operation import router as operation_router
    from backend.routes.fastapi_portfolio import router as portfolio_router
    from backend.routes.fastapi_realtime import router as realtime_router
    from backend.routes.fastapi_settings import router as settings_router
    from backend.routes.fastapi_simulation import router as simulation_router
    from backend.routes.fastapi_statistics import router as statistics_router
    from backend.routes.fastapi_timespeed import router as timespeed_router

    app.include_router(operation_router)
    app.include_router(portfolio_router)
    app.include_router(settings_router)
    app.include_router(importer_router)
    app.include_router(realtime_router)
    app.include_router(timespeed_router)
    app.include_router(auth_router)
    app.include_router(statistics_router)
    app.include_router(simulation_router)

    # Exception handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        Handle FastAPI HTTPException with standardized response format.
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "message": exc.detail,
                "data": None,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        Handle all other exceptions as Internal Server Error.
        """
        logger.exception(f"{exc.__class__.__name__}: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(exc),
                "data": None,
            },
        )

    return app


if __name__ == "__main__":
    import uvicorn

    backend = engine.url.get_backend_name()
    logger.info(f"Banco de dados em uso: {backend.upper()} ({engine.url})")

    app = create_app()
    controller.start_loop()

    # ------------------------------------------------------------
    # 🔌 Modo SocketIO (WebSocket) - ASGI Implementation
    # ------------------------------------------------------------
    if not config.toml.realtime.use_sse:
        import socketio

        from backend.features.realtime.async_ws_broker import AsyncSocketBroker
        from backend.features.realtime.async_ws_handlers import (
            register_async_ws_handlers,
        )

        # Create ASGI socketio server
        sio = socketio.AsyncServer(
            async_mode="asgi",
            cors_allowed_origins="*",
            logger=False,
            engineio_logger=False,
        )

        # Create broker and register handlers
        broker = AsyncSocketBroker(sio)
        RealtimeBrokerManager.set_broker(broker)
        register_async_ws_handlers(sio, broker)

        # Mount socketio to FastAPI app
        socket_app = socketio.ASGIApp(sio, app)

        logger.info("Rodando em modo WebSocket (ASGI SocketIO).")

        # Run with uvicorn
        uvicorn.run(socket_app, host="0.0.0.0", port=8000, log_level="info")

    # ------------------------------------------------------------
    # 🌐 Modo SSE (Server-Sent Events)
    # ------------------------------------------------------------
    else:
        RealtimeBrokerManager.set_broker(SSEBroker())
        logger.info("Rodando em modo SSE (Server-Sent Events).")

        # Run with uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
