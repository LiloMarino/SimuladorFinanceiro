from datetime import date
from decimal import Decimal
from threading import Lock

from backend import config
from backend.core import repository
from backend.core.dto.simulation import SimulationSettingsDTO
from backend.core.enum import VictoryCriterion


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
                    starting_cash=Decimal(str(config.toml.simulation.starting_cash)),
                    monthly_contribution=Decimal(
                        str(config.toml.simulation.monthly_contribution)
                    ),
                    price_impact_enabled=config.toml.simulation.price_impact_enabled,
                    price_impact_k=config.toml.simulation.price_impact_k,
                    price_impact_decay_days=config.toml.simulation.price_impact_decay_days,
                    victory_criterion=VictoryCriterion(
                        config.toml.simulation.victory_criterion
                    ),
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
