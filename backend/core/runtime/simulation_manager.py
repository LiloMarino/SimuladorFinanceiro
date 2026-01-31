from datetime import date
from threading import Lock

from backend import config
from backend.core.dto.simulation import SimulationDTO
from backend.core.exceptions import NoActiveSimulationError
from backend.features.simulation.simulation import Simulation


class SimulationManager:
    """
    Gerenciador singleton de configurações e lifecycle da simulação.

    Responsável por:
    - Armazenar configurações pendentes da simulação (datas, capital inicial)
    - Criar e manter referência à simulação ativa
    - Fornecer acesso thread-safe à simulação para toda a aplicação
    - Gerenciar lifecycle (criação, consulta, limpeza)
    """

    _lock = Lock()
    _pending_settings: SimulationDTO | None = None
    _active_simulation: Simulation | None = None

    # =========================
    # Settings (pré-simulação)
    # =========================

    @classmethod
    def get_settings(cls) -> SimulationDTO:
        with cls._lock:
            if cls._pending_settings:
                return cls._pending_settings

            cls._pending_settings = SimulationDTO(
                start_date=date.fromisoformat(config.toml.simulation.start_date),
                end_date=date.fromisoformat(config.toml.simulation.end_date),
                starting_cash=config.toml.simulation.starting_cash,
                monthly_contribution=config.toml.simulation.monthly_contribution,
            )
            return cls._pending_settings

    @classmethod
    def update_settings(cls, simulation_settings: SimulationDTO) -> SimulationDTO:
        with cls._lock:
            cls._pending_settings = simulation_settings
            return cls._pending_settings

    # =========================
    # Simulation lifecycle
    # =========================

    @classmethod
    def create_simulation(cls, simulation_settings: SimulationDTO) -> Simulation:
        with cls._lock:
            sim = Simulation(simulation_settings)
            cls._active_simulation = sim
            return sim

    @classmethod
    def get_active_simulation(cls) -> Simulation:
        sim = cls._active_simulation
        if not sim:
            raise NoActiveSimulationError()
        return sim

    @classmethod
    def clear_simulation(cls) -> None:
        with cls._lock:
            cls._active_simulation = None
