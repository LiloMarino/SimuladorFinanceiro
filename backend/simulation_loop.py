import threading
import time

from flask import Flask

from backend.core.logger import setup_logger
from backend.features.realtime import get_broker
from backend.features.realtime.ws_broker import SocketBroker
from backend.features.simulation import get_simulation

logger = setup_logger(__name__)


class SimulationLoopController:
    """Gerencia o loop da simulação (thread-safe, independente de WS/SSE)."""

    def __init__(self):
        self._thread: threading.Thread | None = None
        self._running = False

    def start(self, app: Flask):
        if self._running:
            logger.warning("Loop de simulação já está em execução.")
            return
        self._running = True

        def _loop():
            with app.app_context():
                simulation = get_simulation()
                logger.info("Loop de simulação iniciado.")
                try:
                    while self._running:
                        speed = simulation.get_speed()
                        if speed > 0:
                            try:
                                simulation.next_tick()
                            except StopIteration:
                                logger.info("Fim da simulação.")
                                break

                        # Usar um método de sleep que NÃO bloqueie o servidor
                        self._non_blocking_sleep(speed)
                except Exception:
                    logger.exception("Erro no loop da simulação")
                finally:
                    self._running = False
                    logger.info("Loop de simulação encerrado.")

        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Interrompe o loop de simulação."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)

    # ------------------------
    # 🔧 Solução para o freeze
    # ------------------------
    def _non_blocking_sleep(self, speed: float):
        delay = 1 / max(speed, 1)
        broker = get_broker()
        try:
            if isinstance(broker, SocketBroker):
                broker.socketio.sleep(delay)  # type: ignore
            else:
                time.sleep(delay)
        except Exception as e:
            logger.debug(f"Erro no sleep: {e}")
            time.sleep(delay)


# Instância global do controlador
_controller = SimulationLoopController()


def start_simulation_loop(app: Flask):
    """Inicia o loop global da simulação."""
    _controller.start(app)


def stop_simulation_loop():
    """Para o loop global da simulação."""
    _controller.stop()
