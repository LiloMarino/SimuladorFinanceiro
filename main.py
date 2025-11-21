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

import secrets
from pathlib import Path

from flask import Flask
from flask_socketio import SocketIO

from backend.database import engine
from backend.features.realtime.sse_broker import SSEBroker
from backend.features.realtime.ws_broker import SocketBroker
from backend.features.realtime.ws_handlers import register_ws_handlers
from backend.routes import register_routes
from backend.shared.utils.logger import setup_logger
from backend.simulation_loop import start_simulation_loop

BACKEND_DIR = Path("backend")
SECRET_PATH = Path("secret.key")
USE_SSE = False

logger = setup_logger(__name__)


def get_secret_key():
    """Garante a persistência de uma secret key local."""
    if SECRET_PATH.exists():
        return SECRET_PATH.read_text()
    secret_key = secrets.token_hex(16)
    SECRET_PATH.write_text(secret_key)
    return secret_key


def create_app():
    """Cria e configura a aplicação Flask."""
    app = Flask(
        __name__,
        template_folder=BACKEND_DIR / "templates",
        static_folder=BACKEND_DIR / "static",
    )
    app.secret_key = get_secret_key()
    register_routes(app)
    return app


if __name__ == "__main__":
    backend = engine.url.get_backend_name()
    logger.info(f"Banco de dados em uso: {backend.upper()} ({engine.url})")

    app = create_app()

    # ------------------------------------------------------------
    # 🔌 Modo SocketIO (WebSocket)
    # ------------------------------------------------------------
    if not USE_SSE:
        socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")
        socketio.init_app(app)
        app.config["realtime_broker"] = SocketBroker(socketio)
        logger.info("Rodando em modo WebSocket (SocketIO).")
        register_ws_handlers(socketio)
        start_simulation_loop(app)
        socketio.run(app, debug=True)

    # ------------------------------------------------------------
    # 🌐 Modo SSE (Server-Sent Events)
    # ------------------------------------------------------------
    else:
        app.config["realtime_broker"] = SSEBroker()
        logger.info("Rodando em modo SSE (Server-Sent Events).")
        start_simulation_loop(app)
        app.run(debug=True, threaded=True)
