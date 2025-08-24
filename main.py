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

from backend import logger_utils
from backend.database import DB_PATH, engine
from backend.models.models import Base
from backend.routes import routes
from backend.websocket import register_socketio_events

BACKEND_DIR = Path("backend")
SECRET_PATH = Path("secret.key")

logger = logger_utils.setup_logger(__name__)


def init_db_once():
    if engine.url.get_backend_name() == "sqlite" and not DB_PATH.exists():
        print("Criando banco SQLite pela primeira vez...")
        Base.metadata.create_all(bind=engine)


def get_secret_key():
    if SECRET_PATH.exists():
        return SECRET_PATH.read_text()
    secret_key = secrets.token_hex(16)
    SECRET_PATH.write_text(secret_key)
    return secret_key


def create_app():
    app = Flask(
        __name__,
        template_folder=BACKEND_DIR / "templates",
        static_folder=BACKEND_DIR / "static",
    )
    app.secret_key = get_secret_key()
    app.register_blueprint(routes)
    return app


if __name__ == "__main__":
    init_db_once()
    backend = engine.url.get_backend_name()
    logger.info(f"Banco de dados em uso: {backend.upper()} ({engine.url})")

    app = create_app()
    socketio = register_socketio_events(app)  # Injeta WebSocket
    socketio.run(app, debug=False)
