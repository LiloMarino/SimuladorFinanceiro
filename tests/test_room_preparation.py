"""Preparação da sala no lobby: travas, ligações que caem com quem sai e conflitos no Iniciar."""

from __future__ import annotations

from collections.abc import Callable

import pytest
from fastapi import HTTPException

from backend.core.dto.preparation import PartyIdentityDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import PreparationKind, VoterValue
from backend.core.runtime.room_preparation import RoomPreparation
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from tests.fakes import client, simulation_settings

ANA = UserDTO(id=1, client_id=client("ana"), nickname="Ana")
BIA = UserDTO(id=2, client_id=client("bia"), nickname="Bia")
CAIO = UserDTO(id=3, client_id=client("caio"), nickname="Caio")
HUMANS = [ANA, BIA, CAIO]
FLAGS = [VoterValue.STABILITY, VoterValue.DEVELOPMENT, VoterValue.SAVER_PROTECTION]


def party(abbr: str = "ALF", color: str = "#dc2626", name: str = "Partido Alfa"):
    return PartyIdentityDTO(name=name, abbr=abbr, color=color, flags=FLAGS)


def refusal(action: Callable[[], object], status: int = 409) -> str:
    with pytest.raises(HTTPException) as error:
        action()
    assert error.value.status_code == status
    return str(error.value.detail)


@pytest.fixture(autouse=True)
def lobby(monkeypatch: pytest.MonkeyPatch) -> None:
    """Lobby de partida nova com a expansão ligada e ninguém preparado."""
    rules = simulation_settings().model_copy(update={"government_enabled": True})
    monkeypatch.setattr(SettingsManager, "_settings", rules)
    monkeypatch.setattr(SettingsManager, "_selected_simulation_id", None)
    monkeypatch.setattr(SimulationManager, "_active_simulation", None)
    monkeypatch.setattr(RoomPreparation, "_entries", {})


def choose(
    user: UserDTO,
    kind: PreparationKind,
    *,
    identity: PartyIdentityDTO | None = None,
    founder: str | None = None,
    candidate: str | None = None,
    vice: str | None = None,
    humans: list[UserDTO] = HUMANS,
) -> None:
    RoomPreparation.choose(
        user,
        kind,
        humans,
        identity=identity,
        founder=founder,
        candidate=candidate,
        vice=vice,
    )


def test_player_founds_and_another_joins():
    choose(ANA, PreparationKind.FOUND, identity=party())
    choose(BIA, PreparationKind.JOIN, founder="Ana")

    players = {p.nickname: p for p in RoomPreparation.snapshot(HUMANS).players}
    assert players["Ana"].kind is PreparationKind.FOUND
    assert players["Ana"].candidate == "Ana"
    assert (players["Bia"].kind, players["Bia"].founder) == (
        PreparationKind.JOIN,
        "Ana",
    )


def test_fixed_without_saved_party_is_refused():
    assert "Meu partido" in refusal(lambda: choose(ANA, PreparationKind.FOUND))


def test_joining_a_party_nobody_prepared_is_refused():
    refusal(lambda: choose(BIA, PreparationKind.JOIN, founder="Ana"), status=404)


def test_ticket_candidate_is_the_founder_or_a_member():
    choose(ANA, PreparationKind.FOUND, identity=party())
    refusal(
        lambda: choose(ANA, PreparationKind.FOUND, identity=party(), candidate="Bia"),
        status=422,
    )

    choose(BIA, PreparationKind.JOIN, founder="Ana")
    choose(ANA, PreparationKind.FOUND, identity=party(), candidate="Bia", vice="Caio")

    ana = next(
        p for p in RoomPreparation.snapshot(HUMANS).players if p.nickname == "Ana"
    )
    assert (ana.candidate, ana.vice, ana.vice_accepted) == ("Bia", "Caio", False)


def test_invited_vice_accepts_and_refuses():
    choose(ANA, PreparationKind.FOUND, identity=party(), vice="Bia")

    RoomPreparation.answer_vice(BIA, True)
    assert RoomPreparation.snapshot(HUMANS).players[0].vice_accepted is True

    choose(ANA, PreparationKind.FOUND, identity=party(), vice="Caio")
    RoomPreparation.answer_vice(CAIO, False)
    ana = RoomPreparation.snapshot(HUMANS).players[0]
    assert (ana.vice, ana.vice_accepted) == (None, False)
    refusal(lambda: RoomPreparation.answer_vice(CAIO, True), status=404)


def test_changing_the_vice_resets_the_acceptance():
    choose(ANA, PreparationKind.FOUND, identity=party(), vice="Bia")
    RoomPreparation.answer_vice(BIA, True)

    choose(ANA, PreparationKind.FOUND, identity=party(), vice="Bia")
    assert RoomPreparation.snapshot(HUMANS).players[0].vice_accepted is True

    choose(ANA, PreparationKind.FOUND, identity=party(), vice="Caio")
    assert RoomPreparation.snapshot(HUMANS).players[0].vice_accepted is False


def test_vice_of_another_ticket_is_refused():
    choose(ANA, PreparationKind.FOUND, identity=party(), vice="Caio")

    message = refusal(
        lambda: choose(
            BIA,
            PreparationKind.FOUND,
            identity=party("BET", "#2563eb", "Beta"),
            vice="Caio",
        )
    )
    assert "Caio" in message


def test_leaving_the_room_drops_memberships_and_invites():
    choose(ANA, PreparationKind.FOUND, identity=party(), vice="Caio")
    choose(BIA, PreparationKind.JOIN, founder="Ana")

    RoomPreparation.drop(CAIO.id)
    ana = next(
        p for p in RoomPreparation.snapshot(HUMANS).players if p.nickname == "Ana"
    )
    assert ana.vice is None

    RoomPreparation.drop(ANA.id)
    assert RoomPreparation.snapshot(HUMANS).players == []


def test_absent_player_is_left_out_of_the_match():
    choose(ANA, PreparationKind.FOUND, identity=party(), vice="Caio")

    prepared = RoomPreparation.prepared([ANA, BIA])

    assert [p.user_id for p in prepared] == [ANA.id]
    assert RoomPreparation.snapshot([ANA, BIA]).players[0].vice is None


def test_preparation_is_locked_with_a_saved_match_without_the_expansion_or_running(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(SettingsManager, "_selected_simulation_id", 7)
    assert "salva" in refusal(
        lambda: choose(ANA, PreparationKind.FOUND, identity=party())
    )
    assert RoomPreparation.prepared(HUMANS) == []

    monkeypatch.setattr(SettingsManager, "_selected_simulation_id", None)
    off = simulation_settings().model_copy(update={"government_enabled": False})
    monkeypatch.setattr(SettingsManager, "_settings", off)
    assert "desligada" in refusal(
        lambda: choose(ANA, PreparationKind.FOUND, identity=party())
    )


def test_start_is_refused_when_two_parties_share_the_abbreviation():
    choose(ANA, PreparationKind.FOUND, identity=party("ALF"))
    choose(BIA, PreparationKind.FOUND, identity=party("ALF", "#2563eb", "Outro"))

    assert "mesma sigla" in refusal(lambda: RoomPreparation.ensure_ready(HUMANS))


def test_start_is_refused_when_the_party_takes_a_computer_abbreviation():
    choose(ANA, PreparationKind.FOUND, identity=party("UPR"))

    assert "computador" in refusal(lambda: RoomPreparation.ensure_ready(HUMANS))


def test_start_passes_with_distinct_parties():
    choose(ANA, PreparationKind.FOUND, identity=party("ALF"))
    choose(BIA, PreparationKind.FOUND, identity=party("BET", "#2563eb", "Beta"))

    RoomPreparation.ensure_ready(HUMANS)
