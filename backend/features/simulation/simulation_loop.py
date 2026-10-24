from __future__ import annotations

import contextlib
import logging
import threading
import time
from enum import Enum
from typing import TYPE_CHECKING, Literal

from backend.core.dto.backtest import BacktestEndedEventDTO
from backend.core.exceptions import NoActiveSimulationError
from backend.core.exceptions.http_exceptions import ServiceUnavailableError
from backend.core.metrics import ENGINE_DAY, metrics
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.realtime import notify
from backend.features.realtime.schemas import SimulationEndedEventDTO

if TYPE_CHECKING:
    from backend.features.simulation.simulation import Simulation

logger = logging.getLogger(__name__)

STOP_TIMEOUT = 5.0


class SimulationState(Enum):
    STOPPED = "stopped"
    RUNNING = "running"


class SimulationLoopController:
    """
    Controlador de lifecycle do loop de simulação.

    Responsável por:
    - Gerenciar thread dedicada para executar a simulação
    - Controlar estados (STOPPED, RUNNING) de forma thread-safe
    - Implementar pausa/retomada da simulação
    - Encerrar gracefully ao receber stop ou atingir data final
    - Notificar eventos de início, fim e erros via realtime

    O encerramento tem um dono só, a thread do loop: todo fim da partida (natural,
    pelo host, por erro ou no shutdown) passa pelo `_release`, no `finally` de `_run`.
    """

    def __init__(self):
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        # Guarda só o estado do controlador e é sempre o último lock tomado: a rota
        # de velocidade chega aqui segurando o lock da partida.
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
            self._pause_event.clear()
            self._thread = threading.Thread(
                target=self._run,
                daemon=True,
                name="simulation-loop",
            )
            self._state = SimulationState.RUNNING
            self._thread.start()
            logger.info("Simulação iniciada.")

    def pause(self):
        with self._lock:
            # Depois do stop o evento fica aberto, para a thread sair do wait e encerrar
            if self._stop_event.is_set():
                return
            logger.info("Simulação pausada.")
            self._pause_event.clear()

    def unpause(self):
        with self._lock:
            logger.info("Simulação retomada.")
            self._pause_event.set()

    def stop(self) -> None:
        """
        Encerra a simulação em execução: sinaliza a thread e espera ela liberar a
        partida. Volta só com a simulação liberada.
        """
        with self._lock:
            if self._state == SimulationState.STOPPED or self._thread is None:
                raise ValueError("Nenhuma simulação está em execução.")

            self._stop_event.set()
            self._pause_event.set()
            thread = self._thread

        logger.debug("Aguardando a thread da simulação encerrar.")
        thread.join(timeout=STOP_TIMEOUT)
        if thread.is_alive():
            # O estado segue RUNNING até a thread liberar: um stop seguinte espera de novo
            logger.warning("Thread não encerrou no timeout.")
            raise ServiceUnavailableError(
                "A partida ainda está fechando o pregão em andamento."
                " Tente encerrar de novo em instantes."
            )

    def _run(self):
        try:
            simulation = SimulationManager.get_active_simulation()
        except NoActiveSimulationError:
            logger.exception("Simulação não encontrada ao iniciar loop.")
            with self._lock:
                self._state = SimulationState.STOPPED
            return

        # O backtest corre sem pausa e sem espera entre os pregões
        backtest = SimulationManager.has_backtest()
        # Sem motivo, o fim veio do stop(), e o aviso aos jogadores sai da rota
        reason: Literal["completed", "error"] | None = None
        try:
            while not self._stop_event.is_set():
                speed = simulation.get_speed()

                # 🔸 PAUSE (speed == 0)
                if speed <= 0 and not backtest:
                    self._pause_event.wait()  # bloqueia até unpause ou stop
                    continue

                try:
                    with simulation.lock:
                        # A pausa pode ter sido pedida desde a leitura acima.
                        # Confirmá-la e iniciar um dia usam o mesmo lock.
                        if self._stop_event.is_set() or (
                            simulation.get_speed() <= 0 and not backtest
                        ):
                            continue
                        if not backtest:
                            metrics.set_engine_speed(speed)
                        with metrics.measure("engine", ENGINE_DAY):
                            simulation.next_tick()
                except StopIteration:
                    reason = "completed"
                    break

                if not backtest:
                    time.sleep(1 / speed)

        except Exception:
            logger.critical("Erro fatal no loop da simulação", exc_info=True)
            reason = "error"
        finally:
            self._release(simulation, reason, backtest)

    def _release(
        self,
        simulation: Simulation,
        reason: Literal["completed", "error"] | None,
        backtest: bool = False,
    ) -> None:
        """Fecha a partida e libera a simulação. Roda só na thread do loop."""
        try:
            # Ordem aberta não é persistida: a reserva de caixa dela volta antes do
            # flush, e a retomada parte de um caixa sem reservas.
            simulation.cancel_open_orders()
            # Operações feitas depois do último tick (ex.: com o jogo pausado) só viram
            # evento persistido no flush; a retomada parte do que estiver no banco.
            EventManager.flush()
            # O lote de snapshots pendente é gravado antes de a partida ser liberada
            if backtest:
                simulation.flush_backtest()
            # O fechamento lê a partida inteira: roda depois do último flush
            elif reason == "completed":
                simulation.end_match()
        except Exception:
            logger.critical("Erro ao fechar a partida", exc_info=True)
            reason = "error"
        finally:
            SimulationManager.clear_simulation()
            with self._lock:
                self._state = SimulationState.STOPPED
                self._thread = None

        # O loop já está parado quando o aviso sai: quem o recebe pode carregar outra
        # partida, e o start() a aceita.
        if reason is not None:
            if backtest:
                notify(
                    "backtest_ended",
                    BacktestEndedEventDTO(
                        reason=reason, simulation_id=simulation.settings.id
                    ).to_json(),
                )
                return
            notify(
                "simulation_ended",
                SimulationEndedEventDTO(
                    reason=reason, simulation_id=simulation.settings.id
                ).to_json(),
            )

    def shutdown(self):
        try:
            with contextlib.suppress(ValueError):
                self.stop()
                logger.info("Simulação encerrada durante o shutdown.")
        except Exception:
            logger.exception("Erro durante shutdown")


# --------------------------------------------------
# 🌍 Instância global
# --------------------------------------------------
simulation_controller = SimulationLoopController()
