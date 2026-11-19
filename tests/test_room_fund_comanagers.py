"""Co-gestão combinada no lobby: quem funda convida até três, o convidado responde e só o aceito segue para a partida."""

from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal

import pytest
from fastapi import HTTPException

from backend.core.dto.preparation import FundIdentityDTO, MyPreparationDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import FundPreparationComanagerStatus, FundPreparationKind
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.government.room_preparation import RoomPreparation
from backend.features.simulation.room_fund_preparation import RoomFundPreparation
from tests.fakes import client, simulation_settings

ANA = UserDTO(id=1, client_id=client("ana"), nickname="Ana")
BIA = UserDTO(id=2, client_id=client("bia"), nickname="Bia")
CAIO = UserDTO(id=3, client_id=client("caio"), nickname="Caio")
DUDA = UserDTO(id=4, client_id=client("duda"), nickname="Duda")
EVA = UserDTO(id=5, client_id=client("eva"), nickname="Eva")
HUMANS = [ANA, BIA, CAIO, DUDA, EVA]
Status = FundPreparationComanagerStatus
TWENTY = Decimal("0.2")


def refusal(action: Callable[[], object], status: int = 409) -> str:
    with pytest.raises(HTTPException) as error:
        action()
    assert error.value.status_code == status
    return str(error.value.detail)


def found(user: UserDTO, name: str, ticker: str) -> None:
    RoomFundPreparation.choose(
        user, FundPreparationKind.FOUND, FundIdentityDTO(name=name, ticker=ticker)
    )


def invite(owner: UserDTO, guest: UserDTO, share: Decimal = TWENTY) -> None:
    RoomFundPreparation.invite_comanager(owner, HUMANS, guest.nickname, share)


def mine(user: UserDTO) -> MyPreparationDTO:
    return RoomFundPreparation.with_mine(
        RoomPreparation.mine(user, HUMANS), user, HUMANS
    )


@pytest.fixture(autouse=True)
def lobby(monkeypatch: pytest.MonkeyPatch) -> None:
    """Lobby de partida nova, com a expansão Gestoras ligada e Ana fundando a Aurora."""
    rules = simulation_settings().model_copy(update={"funds_enabled": True})
    monkeypatch.setattr(SettingsManager, "_settings", rules)
    monkeypatch.setattr(SettingsManager, "_selected_simulation_id", None)
    monkeypatch.setattr(SimulationManager, "_active_simulation", None)
    monkeypatch.setattr(RoomPreparation, "_entries", {})
    monkeypatch.setattr(RoomPreparation, "_left", {})
    monkeypatch.setattr(RoomFundPreparation, "_entries", {})
    monkeypatch.setattr(RoomFundPreparation, "_comanagers", {})
    found(ANA, "Aurora", "AURA11")


def test_invite_is_seen_by_the_founder_and_the_guest_only():
    invite(ANA, BIA)

    [sent] = mine(ANA).fund_comanagers
    assert (sent.nickname, sent.share, sent.status) == ("Bia", TWENTY, Status.INVITED)
    [received] = mine(BIA).fund_comanager_invites
    assert (received.owner, received.fund_name, received.share, received.accepted) == (
        "Ana",
        "Aurora",
        TWENTY,
        False,
    )
    assert mine(CAIO).fund_comanager_invites == []
    assert mine(CAIO).fund_comanagers == []


def test_accepted_guest_goes_to_the_match_and_the_pending_one_does_not():
    invite(ANA, BIA)
    invite(ANA, CAIO, Decimal("0.3"))
    RoomFundPreparation.answer_comanager(BIA, HUMANS, "Ana", True)

    assert RoomFundPreparation.accepted_comanagers(HUMANS) == {ANA.id: [(BIA, TWENTY)]}
    assert mine(BIA).fund_comanager_invites[0].accepted is True


def test_a_guest_can_accept_more_than_one_fund():
    found(CAIO, "Cais", "CAIS11")
    invite(ANA, BIA)
    invite(CAIO, BIA)

    RoomFundPreparation.answer_comanager(BIA, HUMANS, "Ana", True)
    RoomFundPreparation.answer_comanager(BIA, HUMANS, "Caio", True)

    assert [i.accepted for i in mine(BIA).fund_comanager_invites] == [True, True]


def test_limit_counts_pending_and_accepted_but_not_the_declined():
    for guest in (BIA, CAIO, DUDA):
        invite(ANA, guest, Decimal("0.1"))

    assert "já tem 3 co-gestores" in refusal(lambda: invite(ANA, EVA))

    RoomFundPreparation.answer_comanager(DUDA, HUMANS, "Ana", False)
    invite(ANA, EVA)
    assert [c.status for c in mine(ANA).fund_comanagers] == [
        Status.INVITED,
        Status.INVITED,
        Status.DECLINED,
        Status.INVITED,
    ]


def test_declined_guest_can_be_invited_again():
    invite(ANA, BIA)
    RoomFundPreparation.answer_comanager(BIA, HUMANS, "Ana", False)

    invite(ANA, BIA, Decimal("0.4"))

    [sent] = mine(ANA).fund_comanagers
    assert (sent.status, sent.share) == (Status.INVITED, Decimal("0.4"))


def test_shares_leave_a_part_to_the_manager():
    invite(ANA, BIA, Decimal("0.6"))

    refusal(lambda: invite(ANA, CAIO, Decimal("0.4")), status=422)


def test_only_a_founder_invites_and_never_themselves_or_twice():
    assert "Só quem funda" in refusal(lambda: invite(BIA, CAIO))
    assert "já é o gestor" in refusal(lambda: invite(ANA, ANA))
    invite(ANA, BIA)
    assert "já é co-gestor" in refusal(lambda: invite(ANA, BIA))
    refusal(
        lambda: RoomFundPreparation.invite_comanager(ANA, HUMANS, "Zed", TWENTY),
        status=404,
    )


def test_founder_withdraws_cancels_and_removes():
    invite(ANA, BIA)
    RoomFundPreparation.withdraw_comanager(ANA, HUMANS, "Bia")
    assert mine(ANA).fund_comanagers == []
    refusal(
        lambda: RoomFundPreparation.withdraw_comanager(ANA, HUMANS, "Bia"), status=404
    )


def test_answer_without_invite_is_refused():
    refusal(
        lambda: RoomFundPreparation.answer_comanager(BIA, HUMANS, "Ana", True),
        status=404,
    )
    invite(ANA, BIA)
    RoomFundPreparation.answer_comanager(BIA, HUMANS, "Ana", True)
    refusal(
        lambda: RoomFundPreparation.answer_comanager(BIA, HUMANS, "Ana", False),
        status=404,
    )


def test_invites_fall_when_the_founder_stops_founding_or_the_guest_leaves():
    invite(ANA, BIA)
    invite(ANA, CAIO)

    RoomFundPreparation.drop(BIA.id)
    assert [c.nickname for c in mine(ANA).fund_comanagers] == ["Caio"]

    RoomFundPreparation.choose(ANA, FundPreparationKind.NONE, None)
    assert mine(CAIO).fund_comanager_invites == []
    assert RoomFundPreparation.accepted_comanagers(HUMANS) == {}


def test_locked_lobby_refuses_the_invite(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(SettingsManager, "_selected_simulation_id", 7)

    assert "Partida salva" in refusal(lambda: invite(ANA, BIA))
