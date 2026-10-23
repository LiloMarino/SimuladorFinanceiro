import logging
from datetime import date
from decimal import Decimal
from threading import Lock
from typing import Any

from pydantic import ValidationError

from backend import config
from backend.core import repository
from backend.core.dto.preset import PRESET_FIELDS, RULE_GROUP_FIELDS, AppliedPresetDTO
from backend.core.dto.simulation import SimulationSettingsDTO
from backend.core.enum import (
    GameType,
    PlayerGrouping,
    PresetRuleGroup,
    VictoryCriterion,
)

logger = logging.getLogger(__name__)


class SettingsManager:
    """
    Gerenciador singleton das configurações pendentes de simulação.

    Armazena o SimulationSettingsDTO enquanto a simulação não foi iniciada.
    Inicializa defaults a partir de config e repository quando necessário.
    Guarda também a partida salva que o host selecionou para continuar e o
    preset de onde vieram as regras de agora.
    """

    _lock = Lock()
    _settings: SimulationSettingsDTO | None = None
    _selected_simulation_id: int | None = None
    _applied_preset_id: int | None = None

    @classmethod
    def _defaults(cls) -> SimulationSettingsDTO:
        """As regras de fábrica, inclusive o nome descartável da nova partida."""
        return cls._factory_defaults(repository.simulation.generate_default_name())

    @staticmethod
    def _factory_defaults(name: str) -> SimulationSettingsDTO:
        starting_cash = Decimal(str(config.toml.simulation.starting_cash))
        return SimulationSettingsDTO(
            name=name,
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
            monthly_expense=Decimal(str(config.toml.simulation.monthly_expense)),
            unexpected_per_year=config.toml.simulation.unexpected_per_year,
            withdrawal_rate=Decimal(str(config.toml.simulation.withdrawal_rate)),
            inflation_adjusted=False,
        )

    @staticmethod
    def _merge(
        defaults: SimulationSettingsDTO, stored: dict[str, Any]
    ) -> tuple[SimulationSettingsDTO, list[PresetRuleGroup]]:
        """
        Aplica regras guardadas aos defaults: campo que o app não conhece é
        ignorado e o que falta vem do padrão. Devolve também os grupos que
        vieram do padrão. Levanta ValidationError quando o resultado não vale.
        """
        # Nome identifica esta tentativa de partida e não a anterior.
        known = {key: value for key, value in stored.items() if key in PRESET_FIELDS}
        values: dict[str, Any] = defaults.model_dump(mode="json")
        values.update(known)
        merged = SimulationSettingsDTO.model_validate(values)
        defaulted = [
            group
            for group, fields in RULE_GROUP_FIELDS.items()
            if not any(field in known for field in fields)
        ]
        return merged, defaulted

    @classmethod
    def _load(cls, defaults: SimulationSettingsDTO) -> SimulationSettingsDTO:
        """Aplica a cópia persistida aos defaults, tolerando campos novos no app."""
        stored = repository.last_simulation_settings.get()
        if not isinstance(stored, dict):
            return defaults

        try:
            return cls._merge(defaults, stored)[0]
        except ValidationError:
            logger.warning(
                "Ignorando a última configuração da simulação: dados inválidos."
            )
            return defaults

    @classmethod
    def get(cls) -> SimulationSettingsDTO:
        with cls._lock:
            if cls._settings is None:
                cls._settings = cls._load(cls._defaults())
            return cls._settings

    @classmethod
    def update(cls, settings: SimulationSettingsDTO) -> SimulationSettingsDTO:
        with cls._lock:
            repository.last_simulation_settings.save(
                settings.model_dump(mode="json", exclude={"name"})
            )
            cls._settings = settings
            return cls._settings

    @classmethod
    def restore_defaults(cls) -> SimulationSettingsDTO:
        """Esquece a última configuração e volta aos padrões do config.toml."""
        with cls._lock:
            repository.last_simulation_settings.clear()
            cls._settings = cls._defaults()
            cls._applied_preset_id = None
            return cls._settings

    @classmethod
    def apply_preset(
        cls, preset_id: int, config: dict[str, Any]
    ) -> tuple[SimulationSettingsDTO, list[PresetRuleGroup]]:
        """
        Troca as regras da nova partida pelas do preset, mantendo o nome da
        partida. Levanta ValidationError quando as regras do preset não valem.
        """
        with cls._lock:
            defaults = cls._defaults()
            merged, defaulted = cls._merge(defaults, config)
            name = cls._settings.name if cls._settings is not None else defaults.name
            settings = merged.model_copy(update={"name": name})
            repository.last_simulation_settings.save(
                settings.model_dump(mode="json", exclude={"name"})
            )
            cls._settings = settings
            cls._applied_preset_id = preset_id
            return settings, defaulted

    @classmethod
    def mark_preset(cls, preset_id: int | None) -> None:
        """Diz de qual preset vêm as regras de agora; None quando foram montadas à mão."""
        with cls._lock:
            cls._applied_preset_id = preset_id

    @classmethod
    def applied_preset_id(cls) -> int | None:
        with cls._lock:
            return cls._applied_preset_id

    @classmethod
    def applied_preset(cls) -> AppliedPresetDTO | None:
        """O preset aplicado e o que mudou nas regras desde que foi carregado."""
        with cls._lock:
            preset_id = cls._applied_preset_id
            current = cls._settings
        if preset_id is None:
            return None
        preset = repository.preset.get(preset_id)
        if preset is None:
            cls.mark_preset(None)
            return None
        changed: list[PresetRuleGroup] = []
        if current is not None:
            try:
                saved, _ = cls._merge(
                    cls._factory_defaults(current.name), preset.config
                )
            except ValidationError:
                saved = current
            changed = [
                group
                for group, fields in RULE_GROUP_FIELDS.items()
                if any(getattr(saved, f) != getattr(current, f) for f in fields)
            ]
        return AppliedPresetDTO(
            id=preset.id, name=preset.name, built_in=preset.built_in, changed=changed
        )

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
            cls._applied_preset_id = None
