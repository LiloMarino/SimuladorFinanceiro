import threading
import time
from datetime import date
from enum import Enum

from backend.core.exceptions import NoActiveSimulationError
from backend.core.logger import setup_logger
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.realtime import notify

logger = setup_logger(__name__)


class SimulationState(Enum):
    STOPPED = "stopped"
    RUNNING = "running"


class SimulationLoopController:
    """Controla o loop da simulação com start/stop explícitos."""

    def __init__(self):
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._lock = threading.Lock()
        self._state = SimulationState.STOPPED

    def start(self) -> None:
        """Inicia uma nova simulação criando uma thread dedicada."""
        with self._lock:
            if self._state == SimulationState.RUNNING:
                logger.warning("Tentativa de start concorrente ignorada.")
                return

            try:
                SimulationManager.get_active_simulation()
            except NoActiveSimulationError:
                # Sobe para o FastAPI retornar resposta de erro
                logger.exception("Tentativa de start sem simulação ativa.")
                raise

            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._run,
                daemon=True,
                name="simulation-loop",
            )
            self._state = SimulationState.RUNNING
            self._thread.start()
            logger.info("Thread da simulação iniciada.")

    def pause(self):
        logger.info("Simulação pausada.")
        self._pause_event.clear()

    def unpause(self):
        logger.info("Simulação retomada.")
        self._pause_event.set()

    def stop(self) -> date | None:
        """Encerra a simulação em execução e retorna a data final."""
        with self._lock:
            if self._state == SimulationState.STOPPED:
                raise ValueError("Nenhuma simulação está em execução.")

            self._stop_event.set()
            self._pause_event.set()

        if self._thread and self._thread.is_alive():
            logger.info("Aguardando thread da simulação encerrar...")
            self._thread.join(timeout=5.0)
            if self._thread.is_alive():
                logger.warning("Thread não encerrou no timeout.")

        with self._lock:
            self._state = SimulationState.STOPPED
            self._thread = None

        SimulationManager.clear_simulation()

    def _run(self):
        logger.info("Loop da simulação iniciado.")

        try:
            simulation = SimulationManager.get_active_simulation()
        except NoActiveSimulationError:
            logger.exception("Simulação não encontrada ao iniciar loop.")
            with self._lock:
                self._state = SimulationState.STOPPED
            return

        try:
            while not self._stop_event.is_set():
                speed = simulation.get_speed()

                # 🔸 PAUSE (speed == 0)
                if speed <= 0:
                    self._pause_event.wait()  # bloqueia até unpause ou stop
                    continue

                try:
                    simulation.next_tick()
                except StopIteration:
                    notify(
                        "simulation_ended",
                        {
                            "reason": "completed",
                        },
                    )
                    break

                time.sleep(1 / speed)

        except Exception:
            logger.critical("Erro fatal no loop da simulação")
            logger.exception("Detalhes do erro:")
        finally:
            with self._lock:
                self._state = SimulationState.STOPPED

    def shutdown(self):
        try:
            if self._state == SimulationState.RUNNING:
                logger.info("Encerrando simulação durante shutdown...")
                self._stop_event.set()
                if self._thread and self._thread.is_alive():
                    self._thread.join(timeout=3.0)
                SimulationManager.clear_simulation()
        except Exception:
            logger.exception("Erro durante shutdown")


# --------------------------------------------------
# 🌍 Instância global
# --------------------------------------------------
simulation_controller = SimulationLoopController()
