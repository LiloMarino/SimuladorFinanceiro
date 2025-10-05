import logging
import threading
import time
import traceback

from flask import Flask

from backend.realtime.realtime_base import RealtimeManagerBase
from backend.simulation import get_simulation

logger = logging.getLogger(__name__)


class SimulationLoopController:
    """Gerencia o loop da simulação (thread-safe, independente de WS/SSE)."""

    def __init__(self):
        self._thread: threading.Thread | None = None
        self._running = False

    def start(self, app: Flask, manager: RealtimeManagerBase):
        if self._running:
            logger.warning("Loop de simulação já está em execução.")
            return
        self.manager = manager
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
                                simulation.next_day()
                                current_date = simulation.get_current_date_formatted()
                                stocks = simulation.get_stocks()

                                # Broadcast genérico (SSE ou WS)
                                manager.broadcast(
                                    "simulation_update",
                                    {"current_date": current_date},
                                )
                                manager.broadcast("stocks_update", {"stocks": stocks})

                            except StopIteration:
                                logger.info("Fim da simulação.")
                                break

                        # Usar um método de sleep que NÃO bloqueie o servidor
                        self._non_blocking_sleep(speed)
                except Exception:
                    logger.error(
                        "Erro no loop da simulação:\n%s", traceback.format_exc()
                    )
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
        manager = getattr(self, "manager", None)
        try:
            if manager and hasattr(manager, "socketio"):
                manager.socketio.sleep(delay)
            else:
                time.sleep(delay)
        except Exception as e:
            logger.debug(f"Erro no sleep: {e}")
            time.sleep(delay)


# Instância global do controlador
_controller = SimulationLoopController()


def start_simulation_loop(app: Flask, manager: RealtimeManagerBase):
    """Inicia o loop global da simulação."""
    _controller.start(app, manager)


def stop_simulation_loop():
    """Para o loop global da simulação."""
    _controller.stop()
