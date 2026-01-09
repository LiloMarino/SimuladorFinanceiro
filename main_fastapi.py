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
    # 🔌 Modo SocketIO (WebSocket) - TODO: Implement ASGI version
    # ------------------------------------------------------------
    if not config.toml.realtime.use_sse:
        # Placeholder - will be implemented in Phase 4
        logger.warning(
            "WebSocket mode with FastAPI not yet implemented. Using SSE mode temporarily."
        )
        RealtimeBrokerManager.set_broker(SSEBroker())
        logger.info("Rodando em modo SSE (Server-Sent Events) - temporário.")

    # ------------------------------------------------------------
    # 🌐 Modo SSE (Server-Sent Events)
    # ------------------------------------------------------------
    else:
        RealtimeBrokerManager.set_broker(SSEBroker())
        logger.info("Rodando em modo SSE (Server-Sent Events).")

    # Run with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
