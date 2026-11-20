"""As regras do modo aquisição hostil: padrões, faixas e a dependência da expansão Gestoras."""

from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.core.dto.preset import PRESET_FIELDS
from backend.core.dto.simulation import SimulationSettingsDTO
from backend.core.enum import GameType, PlayerGrouping
from tests.fakes import simulation_settings


def rules(**overrides) -> SimulationSettingsDTO:
    return SimulationSettingsDTO(**simulation_settings().model_dump() | overrides)


def test_takeover_starts_off_with_one_year_of_grace_and_half_the_quotas_to_the_market():
    settings = simulation_settings()
    assert settings.is_fund_takeover is False
    assert settings.fund_grace_months == 12
    assert settings.fund_min_market_share == Decimal("0.50")


def test_takeover_needs_the_funds_expansion():
    with pytest.raises(ValidationError, match="exige a expansão Gestoras"):
        rules(game_type=GameType.FUND_TAKEOVER, funds_enabled=False)
    assert rules(game_type=GameType.FUND_TAKEOVER, funds_enabled=True).is_fund_takeover


def test_takeover_needs_the_individual_mode():
    with pytest.raises(ValidationError, match="exige o modo individual"):
        rules(
            game_type=GameType.FUND_TAKEOVER,
            funds_enabled=True,
            player_grouping=PlayerGrouping.TEAMS,
        )


def test_grace_and_market_share_stay_inside_their_ranges():
    with pytest.raises(ValidationError):
        rules(fund_grace_months=0)
    with pytest.raises(ValidationError):
        rules(fund_grace_months=121)
    with pytest.raises(ValidationError):
        rules(fund_min_market_share=Decimal("0.09"))
    with pytest.raises(ValidationError):
        rules(fund_min_market_share=Decimal("0.91"))
    assert rules(fund_grace_months=1, fund_min_market_share=Decimal("0.10"))


def test_the_new_rules_travel_with_the_presets():
    assert {
        "fund_grace_months",
        "fund_min_market_share",
    } <= PRESET_FIELDS
