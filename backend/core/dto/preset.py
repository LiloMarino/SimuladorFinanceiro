from datetime import datetime

from backend.core.dto.base import BaseDTO
from backend.core.dto.simulation import SimulationSettingsDTO
from backend.core.enum import PresetRuleGroup

PRESET_NAME_MAX_LENGTH = 60

# Cada campo das regras pertence a um grupo; o nome da partida fica fora do preset
RULE_GROUP_FIELDS: dict[PresetRuleGroup, tuple[str, ...]] = {
    PresetRuleGroup.PERIOD: ("start_date", "end_date"),
    PresetRuleGroup.STARTING_CASH: ("starting_cash",),
    PresetRuleGroup.MONTHLY_CONTRIBUTION: ("monthly_contribution",),
    PresetRuleGroup.GROUPING: ("player_grouping", "team_naming"),
    PresetRuleGroup.GAME_TYPE: ("game_type",),
    PresetRuleGroup.VICTORY: ("victory_criterion",),
    PresetRuleGroup.GOAL: ("goal_net_worth",),
    PresetRuleGroup.LIFE: (
        "monthly_salary",
        "monthly_expense",
        "unexpected_per_year",
        "withdrawal_rate",
        "inflation_adjusted",
    ),
    PresetRuleGroup.ASSISTANCES: ("show_equivalent_rate", "show_maturity_projection"),
    PresetRuleGroup.PRICE_IMPACT: (
        "price_impact_enabled",
        "price_impact_k",
        "price_impact_decay_days",
    ),
    PresetRuleGroup.EXPANSIONS: (
        "government_enabled",
        "first_election",
        "computer_difficulty",
    ),
}

PRESET_FIELDS = frozenset(f for fields in RULE_GROUP_FIELDS.values() for f in fields)


class PresetDTO(BaseDTO):
    id: int
    name: str
    # Os prontos vêm com o app e não se renomeiam nem se apagam
    built_in: bool
    created_at: datetime
    # As regras guardadas, sem o nome da partida; o que faltar vem do padrão
    config: dict[str, object]


class AppliedPresetDTO(BaseDTO):
    """O preset de onde vieram as regras de agora e o que mudou desde que foi carregado."""

    id: int
    name: str
    built_in: bool
    changed: list[PresetRuleGroup]


class PresetLoadResponse(BaseDTO):
    settings: SimulationSettingsDTO
    applied: AppliedPresetDTO
    # O que o preset não trazia e veio do padrão (preset salvo numa versão antiga)
    defaulted: list[PresetRuleGroup]


class PresetAppliedEventDTO(BaseDTO):
    """Nulo quando as regras não vêm de preset (ou o preset carregado foi apagado)."""

    applied: AppliedPresetDTO | None
