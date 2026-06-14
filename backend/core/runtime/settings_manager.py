from datetime import date
from threading import Lock

from backend import config
from backend.core import repository
from backend.core.dto.simulation import SimulationSettingsDTO


class SettingsManager:
    """
    Gerenciador singleton das configurações pendentes de simulação.

    Armazena o SimulationSettingsDTO enquanto a simulação não foi iniciada.
    Inicializa defaults a partir de config e repository quando necessário.
    """

    _lock = Lock()
    _settings: SimulationSettingsDTO | None = None

    @classmethod
    def get(cls) -> SimulationSettingsDTO:
        with cls._lock:
            if cls._settings is None:
                cls._settings = SimulationSettingsDTO(
                    name=repository.simulation.generate_default_name(),
                    start_date=date.fromisoformat(config.toml.simulation.start_date),
                    end_date=date.fromisoformat(config.toml.simulation.end_date),
                    starting_cash=config.toml.simulation.starting_cash,
                    monthly_contribution=config.toml.simulation.monthly_contribution,
                )
            return cls._settings

    @classmethod
    def update(cls, settings: SimulationSettingsDTO) -> SimulationSettingsDTO:
        with cls._lock:
            cls._settings = settings
            return cls._settings

    @classmethod
    def clear(cls) -> None:
        with cls._lock:
            cls._settings = None
