from flask_socketio import SocketIO

from backend import logger_utils
from backend.simulation import get_simulation

simulation_loop_started = False

logger = logger_utils.setup_logger(__name__)


def register_socketio_events(app):
    global simulation_loop_started

    socketio_instance = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")
    app.config["socketio"] = socketio_instance

    @socketio_instance.on("connect")
    def on_connect():
        simulation = get_simulation()
        socketio_instance.emit(
            "simulation_update",
            {"current_date": simulation.get_current_date_formatted()},
        )
        socketio_instance.emit("speed_update", {"speed": simulation.get_speed()})

    if not simulation_loop_started:
        simulation_loop_started = True

        def run_simulation(app):
            with app.app_context():
                simulation = get_simulation()
                while True:
                    if simulation.get_speed() > 0:
                        try:
                            simulation.next_day()
                            app.config["socketio"].emit(
                                "simulation_update",
                                {
                                    "current_date": simulation.get_current_date_formatted()
                                },
                            )
                            app.config["socketio"].emit(
                                "speed_update",
                                {"speed": simulation.get_speed()},
                            )
                        except StopIteration:
                            break
                    # Sleep cooperativo
                    app.config["socketio"].sleep(1 / max(simulation.get_speed(), 1))

        socketio_instance.start_background_task(run_simulation, app)

    return socketio_instance
