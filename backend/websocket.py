from __future__ import annotations

from typing import TYPE_CHECKING

from flask_socketio import SocketIO

from backend import logger_utils
from backend.simulation import get_simulation

if TYPE_CHECKING:
    from flask import Flask

logger = logger_utils.setup_logger(__name__)

# Alterar para Eventlet na produção e desativar o debug
socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")

simulation_loop_started = False


@socketio.on("connect")
def on_connect():
    simulation = get_simulation()
    socketio.emit(
        "simulation_update",
        {"current_date": simulation.get_current_date_formatted()},
    )
    socketio.emit("speed_update", {"speed": simulation.get_speed()})


def run_simulation(app: Flask):
    with app.app_context():
        simulation = get_simulation()
        while True:
            if simulation.get_speed() > 0:
                try:
                    simulation.next_day()
                    socketio.emit(
                        "simulation_update",
                        {"current_date": simulation.get_current_date_formatted()},
                    )
                    socketio.emit("speed_update", {"speed": simulation.get_speed()})
                except StopIteration:
                    break
            socketio.sleep(1 / max(simulation.get_speed(), 1))


def init_socketio(app: Flask):
    """Inicializa o SocketIO e garante que o loop da simulação rode uma vez só."""
    global simulation_loop_started
    socketio.init_app(app)  # conecta o Flask aqui
    app.config["socketio"] = socketio

    if not simulation_loop_started:
        simulation_loop_started = True
        socketio.start_background_task(run_simulation, app)

    return socketio
