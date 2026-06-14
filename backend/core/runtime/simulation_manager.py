from datetime import date
from threading import Lock

from backend import config
from backend.core import repository
from backend.core.dto.simulation import SimulationDTO, SimulationSettingsDTO
from backend.core.exceptions import NoActiveSimulationError
from backend.core.runtime.active_context import ActiveContext
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
    _pending_settings: SimulationSettingsDTO | None = None
    _active_simulation: Simulation | None = None

    # =========================
    # Settings (pré-simulação)
    # =========================

    @classmethod
    def get_settings(cls) -> SimulationSettingsDTO:
        with cls._lock:
            if cls._pending_settings:
                return cls._pending_settings

            cls._pending_settings = SimulationSettingsDTO(
                name=repository.simulation.generate_default_name(),
                start_date=date.fromisoformat(config.toml.simulation.start_date),
                end_date=date.fromisoformat(config.toml.simulation.end_date),
                starting_cash=config.toml.simulation.starting_cash,
                monthly_contribution=config.toml.simulation.monthly_contribution,
            )
            return cls._pending_settings

    @classmethod
    def update_settings(
        cls, simulation_settings: SimulationSettingsDTO
    ) -> SimulationSettingsDTO:
        with cls._lock:
            cls._pending_settings = simulation_settings
            return cls._pending_settings

    # =========================
    # Simulation lifecycle
    # =========================

    @classmethod
    def create_simulation(cls, simulation_settings: SimulationDTO) -> Simulation:
        with cls._lock:
            ActiveContext.set_active_simulation_id(simulation_settings.id)
            sim = Simulation(simulation_settings)
            cls._active_simulation = sim
            cls._pending_settings = None
            return sim

    @classmethod
    def get_active_simulation(cls) -> Simulation:
        sim = cls._active_simulation
        if not sim:
            raise NoActiveSimulationError()
        return sim

    @classmethod
    def get_active_simulation_id(cls) -> int:
        return ActiveContext.get_active_simulation_id()

    @classmethod
    def clear_simulation(cls) -> None:
        with cls._lock:
            cls._active_simulation = None
            ActiveContext.set_active_simulation_id(None)
