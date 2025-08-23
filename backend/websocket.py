import threading
import time

from flask_socketio import SocketIO

from backend.simulation import get_simulation

socketio = SocketIO(cors_allowed_origins="*")


def register_socketio_events(app):
    """Registra eventos do WebSocket e inicia o loop da simulação."""
    socketio.init_app(app)

    simulation = get_simulation()

    @socketio.on("connect")
    def on_connect():
        # Envia estado inicial ao cliente
        socketio.emit(
            "simulation_update",
            {
                "speed": simulation.speed,
                "current_date": simulation.current_date.strftime("%Y-%m-%d"),
            },
        )

    # 🔹 Só backend → frontend, então nada de set_speed aqui.
    # O controle de velocidade pode vir via REST se você quiser.

    def run_simulation():
        """Loop que avança a simulação e envia atualizações via WebSocket."""
        while True:
            if simulation.speed > 0:
                try:
                    simulation.next_day()
                    socketio.emit(
                        "simulation_update",
                        {
                            "speed": simulation.speed,
                            "current_date": simulation.current_date.strftime(
                                "%Y-%m-%d"
                            ),
                        },
                    )
                except StopIteration:
                    break
            time.sleep(1 / max(simulation.speed, 1))

    threading.Thread(target=run_simulation, daemon=True).start()
    return socketio
