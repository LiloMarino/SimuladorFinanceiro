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

from backend import config
from backend.core.logger import setup_logging

setup_logging(
    level=config.toml.logging.logging_level,
    logs_path=config.toml.logging.logs_path,
)
# flake8: noqa: E402 - Setup de logging deve ser o primeiro para capturar logs de importação

import asyncio
import logging
import sys
import webbrowser
from contextlib import asynccontextmanager
from threading import Thread, Timer

import socketio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.database import get_engine
from backend.core.migration import MigrationError, migrate
from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.core.runtime.tunnel_manager import TunnelManager
from backend.features.import_data.indicators import refresh_indicators
from backend.features.realtime.sse_broker import SSEBroker
from backend.features.realtime.ws_broker import SocketBroker
from backend.features.realtime.ws_handlers import register_ws_handlers
from backend.features.simulation.simulation_loop import simulation_controller
from backend.routes import register_routes

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine()
    backend = engine.url.get_backend_name()
    logger.info(f"Banco de dados em uso: {backend.upper()} ({engine.url})")

    # --------------------------------------------------
    # 🔌 Inicialização do TunnelProvider (LAN)
    # --------------------------------------------------
    if config.toml.server.provider == "lan":
        logger.info("🌐 Inicializando LANProvider no startup...")
        await TunnelManager._provider.start(config.toml.server.port)

    # --------------------------------------------------
    # 🔌 Vincula o event loop ao broker WS
    # --------------------------------------------------
    try:
        broker = RealtimeBrokerManager.get_broker()
        if isinstance(broker, SocketBroker):
            broker.bind_event_loop(asyncio.get_running_loop())
            logger.info("Event loop vinculado ao SocketBroker.")
    except Exception as e:
        logger.warning(f"Não foi possível vincular o event loop ao SocketBroker: {e}")

    # --------------------------------------------------
    # Indicadores econômicos: o boot segue sem esperar a rede
    # --------------------------------------------------
    Thread(target=refresh_indicators, name="indicators-refresh", daemon=True).start()

    logger.info("Acesse localmente: http://localhost:8000")
    yield

    # --------------------------------------------------
    # Shutdown
    # --------------------------------------------------
    simulation_controller.shutdown()
    logger.info("Aplicação finalizada.")


# ---------------------------------------------------------------------
# Criação da aplicação
# ---------------------------------------------------------------------


def create_api() -> FastAPI:
    """As rotas HTTP; o `create_app` acrescenta o canal de tempo real por cima."""
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
    return app


def create_app():
    app = create_api()

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
    # O app sobe com o banco já no head das migrations
    try:
        migrate(config.env.postgres_url)
    except MigrationError as error:
        logger.critical(error)
        if getattr(sys, "frozen", False):
            input("Pressione Enter para fechar.")
        sys.exit(1)

    asgi_app = create_app()
    local_url = f"http://localhost:{config.toml.server.port}"

    logger.info(f"Abrindo navegador em {local_url}")
    Timer(1.0, lambda: webbrowser.open(local_url)).start()

    uvicorn.run(
        asgi_app,
        host="0.0.0.0",
        port=config.toml.server.port,
        reload=False,
    )
