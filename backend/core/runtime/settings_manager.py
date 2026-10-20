from datetime import date
from decimal import Decimal
from threading import Lock

from backend import config
from backend.core import repository
from backend.core.dto.simulation import SimulationSettingsDTO
from backend.core.enum import GameType, PlayerGrouping, VictoryCriterion


class SettingsManager:
    """
    Gerenciador singleton das configurações pendentes de simulação.

    Armazena o SimulationSettingsDTO enquanto a simulação não foi iniciada.
    Inicializa defaults a partir de config e repository quando necessário.
    Guarda também a partida salva que o host selecionou para continuar.
    """

    _lock = Lock()
    _settings: SimulationSettingsDTO | None = None
    _selected_simulation_id: int | None = None

    @classmethod
    def get(cls) -> SimulationSettingsDTO:
        with cls._lock:
            if cls._settings is None:
                starting_cash = Decimal(str(config.toml.simulation.starting_cash))
                cls._settings = SimulationSettingsDTO(
                    name=repository.simulation.generate_default_name(),
                    start_date=date.fromisoformat(config.toml.simulation.start_date),
                    end_date=date.fromisoformat(config.toml.simulation.end_date),
                    starting_cash=starting_cash,
                    monthly_contribution=Decimal(
                        str(config.toml.simulation.monthly_contribution)
                    ),
                    price_impact_enabled=config.toml.simulation.price_impact_enabled,
                    price_impact_k=config.toml.simulation.price_impact_k,
                    price_impact_decay_days=config.toml.simulation.price_impact_decay_days,
                    victory_criterion=VictoryCriterion(
                        config.toml.simulation.victory_criterion
                    ),
                    game_type=GameType.CLASSIC,
                    goal_net_worth=starting_cash * config.toml.simulation.goal_multiple,
                    monthly_salary=Decimal(str(config.toml.simulation.monthly_salary)),
                    monthly_expense=Decimal(
                        str(config.toml.simulation.monthly_expense)
                    ),
                    unexpected_per_year=config.toml.simulation.unexpected_per_year,
                    withdrawal_rate=Decimal(
                        str(config.toml.simulation.withdrawal_rate)
                    ),
                    inflation_adjusted=False,
                )
            return cls._settings

    @classmethod
    def update(cls, settings: SimulationSettingsDTO) -> SimulationSettingsDTO:
        with cls._lock:
            cls._settings = settings
            return cls._settings

    @classmethod
    def get_selected_simulation_id(cls) -> int | None:
        with cls._lock:
            return cls._selected_simulation_id

    @classmethod
    def select_simulation(cls, simulation_id: int | None) -> None:
        with cls._lock:
            cls._selected_simulation_id = simulation_id

    @classmethod
    def effective_grouping(cls) -> PlayerGrouping:
        """Como a sala joga: a partida salva selecionada manda; sem ela, as regras da nova."""
        selected_id = cls.get_selected_simulation_id()
        if selected_id is not None:
            summary = repository.simulation.get_simulation(selected_id)
            if summary is not None:
                return summary.player_grouping
        return cls.get().player_grouping

    @classmethod
    def clear(cls) -> None:
        with cls._lock:
            cls._settings = None
            cls._selected_simulation_id = None
