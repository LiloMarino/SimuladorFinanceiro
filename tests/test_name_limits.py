"""Apelido, nome de bot, de partida e de backtest cabem em 20 caracteres; a sigla do partido, em 8."""

from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from backend.core.dto.backtest import BacktestConfigDTO
from backend.core.dto.base import NAME_MAX_LENGTH
from backend.core.dto.government import PartyAbbr
from backend.routes.auth import UserRegisterRequest
from backend.routes.simulation import RoomBotRequest, SimulationRulesRequest
from tests.fakes import simulation_settings

FITS = "a" * NAME_MAX_LENGTH
TOO_LONG = "a" * (NAME_MAX_LENGTH + 1)


def backtest_body(name: str) -> dict[str, object]:
    settings = simulation_settings().model_dump(mode="json")
    return {
        "name": name,
        "start_date": settings["start_date"],
        "end_date": settings["end_date"],
        "starting_cash": settings["starting_cash"],
        "monthly_contribution": 0,
        "price_impact": "OFF",
        "participants": [
            {"nickname": "Bot", "color": "#ff0000", "strategy_key": "cdi_100"}
        ],
    }


def test_the_limit_is_twenty() -> None:
    assert NAME_MAX_LENGTH == 20


def test_register_nickname_accepts_the_limit_and_rejects_one_more() -> None:
    UserRegisterRequest(nickname=FITS)
    with pytest.raises(ValidationError):
        UserRegisterRequest(nickname=TOO_LONG)


def test_bot_nickname_accepts_the_limit_and_rejects_one_more() -> None:
    RoomBotRequest(nickname=FITS, strategy_key="cdi_100")
    with pytest.raises(ValidationError):
        RoomBotRequest(nickname=TOO_LONG, strategy_key="cdi_100")


def test_match_name_accepts_the_limit_and_rejects_one_more() -> None:
    rules = simulation_settings().model_dump(mode="json")
    rules.pop("name")
    SimulationRulesRequest.model_validate({**rules, "name": FITS})
    with pytest.raises(ValidationError):
        SimulationRulesRequest.model_validate({**rules, "name": TOO_LONG})


def test_backtest_name_accepts_the_limit_and_rejects_one_more() -> None:
    BacktestConfigDTO.model_validate(backtest_body(FITS))
    with pytest.raises(ValidationError):
        BacktestConfigDTO.model_validate(backtest_body(TOO_LONG))


@pytest.mark.parametrize("abbr", ["AB", "ABCDEFGH"])
def test_party_abbr_accepts_two_to_eight_letters(abbr: str) -> None:
    assert TypeAdapter(PartyAbbr).validate_python(abbr) == abbr


@pytest.mark.parametrize("abbr", ["A", "ABCDEFGHI"])
def test_party_abbr_rejects_outside_two_to_eight(abbr: str) -> None:
    with pytest.raises(ValidationError):
        TypeAdapter(PartyAbbr).validate_python(abbr)
