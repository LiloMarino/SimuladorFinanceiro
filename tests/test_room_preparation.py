"""Preparação da sala no lobby: travas, ligações que caem com quem sai, convite privado, a última escolha e conflitos no Iniciar."""

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
    monkeypatch.setattr(RoomPreparation, "_left", {})


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
    assert ana.candidate == "Bia"
    assert RoomPreparation.mine(ANA, HUMANS).invited == "Caio"


def test_the_pending_invite_is_seen_only_by_the_two_players():
    choose(ANA, PreparationKind.FOUND, identity=party(), vice="Caio")

    snapshot = RoomPreparation.snapshot(HUMANS)
    assert (snapshot.players[0].vice, snapshot.pending_invites) == (None, 1)
    invite = RoomPreparation.mine(CAIO, HUMANS).invite
    assert invite is not None
    assert (invite.owner, invite.abbr, invite.candidate) == ("Ana", "ALF", "Ana")
    assert RoomPreparation.mine(BIA, HUMANS).invite is None

    RoomPreparation.answer_vice(CAIO, True)
    snapshot = RoomPreparation.snapshot(HUMANS)
    assert (snapshot.players[0].vice, snapshot.pending_invites) == ("Caio", 0)
    assert RoomPreparation.mine(ANA, HUMANS).invited is None


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


def test_the_member_learns_the_party_left_until_the_next_choice():
    choose(ANA, PreparationKind.FOUND, identity=party())
    choose(BIA, PreparationKind.JOIN, founder="Ana")

    choose(ANA, PreparationKind.NONE)
    assert RoomPreparation.mine(BIA, HUMANS).left_party == "ALF"

    choose(BIA, PreparationKind.NONE)
    assert RoomPreparation.mine(BIA, HUMANS).left_party is None


def test_the_founder_of_the_last_room_comes_back_founding():
    assert RoomPreparation.restore(ANA, HUMANS, party()) is True
    ana = RoomPreparation.snapshot(HUMANS).players[0]
    assert (ana.kind, ana.candidate, ana.vice) == (PreparationKind.FOUND, "Ana", None)

    assert RoomPreparation.restore(ANA, HUMANS, party("OUT")) is False
    assert RoomPreparation.snapshot(HUMANS).players[0].party == party()


def test_the_member_whose_party_left_is_not_put_back_founding():
    choose(ANA, PreparationKind.FOUND, identity=party())
    choose(BIA, PreparationKind.JOIN, founder="Ana")
    RoomPreparation.drop(ANA.id)

    assert RoomPreparation.restore(BIA, HUMANS, party("BET")) is False


def test_computer_parties_carry_their_flags():
    reserved = RoomPreparation.snapshot(HUMANS).reserved

    assert all(len(p.flags) > 0 for p in reserved)


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


# Federação no lobby


def two_founders() -> None:
    choose(ANA, PreparationKind.FOUND, identity=party("ALF"))
    choose(BIA, PreparationKind.FOUND, identity=party("BET", "#2563eb", "Beta"))


def combined(user: UserDTO):
    return next(
        p
        for p in RoomPreparation.snapshot(HUMANS).players
        if p.nickname == user.nickname
    ).federation


def test_a_proposal_waits_for_the_answer_and_becomes_a_federation_when_accepted():
    two_founders()

    RoomPreparation.propose_federation(ANA, HUMANS, "Bia", "Frente", "Bia")

    assert RoomPreparation.mine(ANA, HUMANS).federation_invited == "Bia"
    invite = RoomPreparation.mine(BIA, HUMANS).federation_invite
    assert invite is not None
    assert (invite.name, invite.candidate) == ("Frente", "Bia")
    assert combined(ANA) is None

    RoomPreparation.answer_federation(BIA, True)

    for user, partner in ((ANA, "Bia"), (BIA, "Ana")):
        federation = combined(user)
        assert federation is not None
        assert (federation.partner, federation.name, federation.candidate) == (
            partner,
            "Frente",
            "Bia",
        )
    assert RoomPreparation.mine(ANA, HUMANS).federation_invited is None


def test_the_federation_name_defaults_to_the_abbreviations():
    two_founders()

    RoomPreparation.propose_federation(ANA, HUMANS, "Bia", None, None)
    RoomPreparation.answer_federation(BIA, True)

    federation = combined(ANA)
    assert federation is not None
    assert (federation.name, federation.candidate) == ("Federação ALF–BET", "Ana")  # noqa: RUF001


def test_declining_clears_the_proposal():
    two_founders()
    RoomPreparation.propose_federation(ANA, HUMANS, "Bia", None, None)

    RoomPreparation.answer_federation(BIA, False)

    assert RoomPreparation.mine(ANA, HUMANS).federation_invited is None
    assert RoomPreparation.mine(BIA, HUMANS).federation_invite is None
    assert combined(ANA) is None


def test_either_founder_undoes_the_combined_federation():
    two_founders()
    RoomPreparation.propose_federation(ANA, HUMANS, "Bia", None, None)
    RoomPreparation.answer_federation(BIA, True)

    RoomPreparation.propose_federation(BIA, HUMANS, None, None, None)

    assert combined(ANA) is None
    assert combined(BIA) is None


def test_the_proposer_withdraws_the_open_proposal():
    two_founders()
    RoomPreparation.propose_federation(ANA, HUMANS, "Bia", None, None)

    RoomPreparation.propose_federation(ANA, HUMANS, None, None, None)

    assert RoomPreparation.mine(BIA, HUMANS).federation_invite is None


def test_only_a_founder_proposes_and_only_to_another_founder():
    choose(ANA, PreparationKind.FOUND, identity=party("ALF"))
    choose(BIA, PreparationKind.JOIN, founder="Ana")

    assert "Só quem funda" in refusal(
        lambda: RoomPreparation.propose_federation(BIA, HUMANS, "Ana", None, None)
    )
    assert "não preparou" in refusal(
        lambda: RoomPreparation.propose_federation(ANA, HUMANS, "Caio", None, None),
        404,
    )
    assert "próprio partido" in refusal(
        lambda: RoomPreparation.propose_federation(ANA, HUMANS, "Ana", None, None)
    )


def test_one_proposal_at_a_time_per_party():
    two_founders()
    choose(CAIO, PreparationKind.FOUND, identity=party("GAM", "#16a34a", "Gama"))
    RoomPreparation.propose_federation(ANA, HUMANS, "Bia", None, None)

    assert "já tem uma proposta" in refusal(
        lambda: RoomPreparation.propose_federation(CAIO, HUMANS, "Bia", None, None)
    )
    assert "já tem uma proposta" in refusal(
        lambda: RoomPreparation.propose_federation(ANA, HUMANS, "Caio", None, None)
    )


def test_the_candidate_belongs_to_one_of_the_two_parties():
    two_founders()
    choose(CAIO, PreparationKind.JOIN, founder="Bia")

    assert "candidato" in refusal(
        lambda: RoomPreparation.propose_federation(ANA, HUMANS, "Bia", None, "Dana"),
        422,
    )
    RoomPreparation.propose_federation(ANA, HUMANS, "Bia", None, "Caio")


def test_answering_without_a_proposal_is_refused():
    two_founders()

    assert "para responder" in refusal(
        lambda: RoomPreparation.answer_federation(BIA, True), 404
    )


def test_the_federation_falls_when_the_partner_stops_founding():
    two_founders()
    RoomPreparation.propose_federation(ANA, HUMANS, "Bia", None, None)
    RoomPreparation.answer_federation(BIA, True)

    choose(BIA, PreparationKind.JOIN, founder="Ana")

    assert combined(ANA) is None
    assert RoomPreparation.mine(ANA, HUMANS).federation_invited is None


def test_the_federation_falls_when_the_partner_leaves_the_room():
    two_founders()
    RoomPreparation.propose_federation(ANA, HUMANS, "Bia", None, None)
    RoomPreparation.answer_federation(BIA, True)

    assert combined(ANA) is not None
    present = [ANA, CAIO]
    assert RoomPreparation.snapshot(present).players[0].federation is None
