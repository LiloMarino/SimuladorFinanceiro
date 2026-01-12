"""
Simulador Financeiro - Código-fonte principal

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

from contextlib import asynccontextmanager

import socketio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend import config
from backend.core.database import engine
from backend.core.logger import setup_logger
from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.features.realtime.sse_broker import SSEBroker
from backend.features.realtime.ws_broker import SocketBroker
from backend.features.realtime.ws_handlers import register_ws_handlers
from backend.features.simulation.simulation_loop import simulation_controller
from backend.routes import register_routes

logger = setup_logger(__name__)


# ---------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    backend = engine.url.get_backend_name()
    logger.info(f"Banco de dados em uso: {backend.upper()} ({engine.url})")

    simulation_controller.start_loop()
    yield
    simulation_controller.stop_loop()
    logger.info("Aplicação finalizada.")


# ---------------------------------------------------------------------
# Criação da aplicação
# ---------------------------------------------------------------------


def create_app():
    app = FastAPI(
        title="Simulador Financeiro",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_routes(app)

    # ------------------------------------------------------------
    # 🔌 WebSocket (Socket.IO)
    # ------------------------------------------------------------
    if not config.toml.realtime.use_sse:
        logger.info("Rodando em modo WebSocket (Socket.IO).")

        sio = socketio.AsyncServer(
            async_mode="asgi",
            cors_allowed_origins="*",
        )

        register_ws_handlers(sio)
        RealtimeBrokerManager.set_broker(SocketBroker(sio))

        return socketio.ASGIApp(
            sio,
            other_asgi_app=app,
        )

    # ------------------------------------------------------------
    # 🌐 SSE
    # ------------------------------------------------------------
    else:
        logger.info("Rodando em modo SSE (Server-Sent Events).")
        RealtimeBrokerManager.set_broker(SSEBroker())
        return app


# ---------------------------------------------------------------------
# Entry point (equivalente ao socketio.run / app.run)
# ---------------------------------------------------------------------

if __name__ == "__main__":
    asgi_app = create_app()

    uvicorn.run(
        asgi_app,
        host="0.0.0.0",
        port=8000,
        reload=True,  # DEV ONLY
    )
