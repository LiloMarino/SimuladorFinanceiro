from __future__ import annotations

from threading import Lock
from typing import TYPE_CHECKING

from backend.core.exceptions import NoActiveSimulationError

if TYPE_CHECKING:
    from backend.features.simulation.simulation import Simulation


class SimulationManager:
    """
    Gerenciador singleton do lifecycle da simulação ativa.

    Responsável por:
    - Registrar e manter referência à simulação em execução
    - Fornecer acesso thread-safe à simulação e ao simulation_id
    """

    _lock = Lock()
    _active_simulation: Simulation | None = None
    _simulation_id: int | None = None

    @classmethod
    def register_simulation(cls, sim: Simulation) -> None:
        with cls._lock:
            cls._active_simulation = sim
            cls._simulation_id = sim.settings.id

    @classmethod
    def get_active_simulation(cls) -> Simulation:
        sim = cls._active_simulation
        if not sim:
            raise NoActiveSimulationError()
        return sim

    @classmethod
    def get_active_simulation_id(cls) -> int:
        with cls._lock:
            if cls._simulation_id is None:
                raise NoActiveSimulationError()
            return cls._simulation_id

    @classmethod
    def clear_simulation(cls) -> None:
        with cls._lock:
            cls._active_simulation = None
            cls._simulation_id = None
