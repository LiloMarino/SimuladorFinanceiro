import threading
import time

from flask import Flask

from backend.core.logger import setup_logger
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.realtime import get_broker
from backend.features.realtime.ws_broker import SocketBroker

logger = setup_logger(__name__)


class SimulationLoopController:
    """Controla o loop da simulação de forma event-driven (sem polling)."""

    def __init__(self):
        self._app: Flask | None = None
        self._thread: threading.Thread | None = None
        self._start_event = threading.Event()
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    # --------------------------------------------------
    # 🔗 Bind do Flask app (feito UMA vez no boot)
    # --------------------------------------------------
    def bind_app(self, app: Flask):
        self._app = app

    # --------------------------------------------------
    # 🚀 Cria a thread (mas ela dorme bloqueada)
    # --------------------------------------------------
    def start_loop(self):
        with self._lock:
            if self._thread and self._thread.is_alive():
                return

            if not self._app:
                raise RuntimeError("SimulationLoopController: app não foi bindado.")

            self._thread = threading.Thread(
                target=self._run,
                daemon=True,
                name="simulation-loop",
            )
            self._thread.start()

    # --------------------------------------------------
    # ▶️ Start
    # --------------------------------------------------
    def trigger_start(self):
        logger.info("Evento de início da simulação recebido.")
        self._start_event.set()

    # --------------------------------------------------
    # ⛔ Stop
    # --------------------------------------------------
    def stop(self):
        self._stop_event.set()
        self._start_event.set()  # libera caso esteja bloqueado

    # --------------------------------------------------
    # 🔁 Loop interno
    # --------------------------------------------------
    def _run(self):
        assert self._app is not None

        with self._app.app_context():
            logger.info("Thread da simulação criada. Aguardando evento de start...")
            self._start_event.wait()  # Bloqueia a thread enquanto aguarda o start

            if self._stop_event.is_set():
                return

            simulation = SimulationManager.get_active_simulation()
            if not simulation:
                logger.warning("Start recebido, mas nenhuma simulação ativa.")
                return

            logger.info("Simulação iniciada.")

            try:
                while not self._stop_event.is_set():
                    speed = simulation.get_speed()

                    if speed <= 0:
                        self._sleep(0.1)
                        continue

                    try:
                        simulation.next_tick()
                    except StopIteration:
                        logger.info("Simulação finalizada.")
                        SimulationManager.clear_simulation()
                        break

                    self._sleep(1 / speed)

            except Exception:
                logger.critical("Erro fatal no loop da simulação.")
                logger.exception("Erro fatal no loop da simulação.")

    # --------------------------------------------------
    # 💤 Sleep compatível com WS / SSE
    # --------------------------------------------------
    def _sleep(self, delay: float):
        broker = get_broker()
        if isinstance(broker, SocketBroker):
            broker.socketio.sleep(delay)  # type: ignore
        else:
            time.sleep(delay)


# --------------------------------------------------
# 🌍 Instância global
# --------------------------------------------------
controller = SimulationLoopController()
