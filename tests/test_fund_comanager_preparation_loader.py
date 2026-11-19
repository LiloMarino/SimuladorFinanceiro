"""A co-gestão combinada no lobby chega à partida: o aceito entra ativo, com a parte já valendo, e o convite sem resposta cai."""

from __future__ import annotations

from decimal import Decimal

import pytest

from backend.core.dto.preparation import FundIdentityDTO
from backend.core.enum import FundComanagerStatus, FundPreparationComanagerStatus
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.simulation.room_fund_preparation import RoomFundPreparation
from backend.features.simulation.simulation_loader import SimulationLoader
from tests.test_bots import person, room, rules  # noqa: F401
from tests.test_simulation_loader import started  # noqa: F401

Status = FundPreparationComanagerStatus


@pytest.fixture(autouse=True)
def lobby(room, monkeypatch: pytest.MonkeyPatch) -> None:  # noqa: F811
    monkeypatch.setattr(RoomFundPreparation, "_entries", {})
    monkeypatch.setattr(RoomFundPreparation, "_comanagers", {})
    monkeypatch.setattr(SettingsManager, "_settings", rules(funds_enabled=True))


def test_accepted_comanager_starts_active_with_the_share_in_force():
    ana, bia, caio = person("Ana"), person("Bia"), person("Caio")
    RoomFundPreparation._entries[ana.id] = FundIdentityDTO(
        name="Aurora", ticker="AURA11"
    )
    RoomFundPreparation._comanagers[ana.id] = {
        bia.id: (Decimal("0.2"), Status.ACCEPTED),
        caio.id: (Decimal("0.3"), Status.INVITED),
    }

    SimulationLoader.create(rules(funds_enabled=True))

    sim = SimulationManager.get_active_simulation()
    assert sim._funds is not None
    [fund] = sim._funds.funds()
    [comanager] = fund.comanagers
    assert comanager.user_id == bia.id
    assert comanager.status is FundComanagerStatus.ACTIVE
    assert (comanager.share, comanager.pending_share) == (Decimal("0.2"), None)
    assert comanager.since == comanager.invited_on
    assert RoomFundPreparation.accepted_comanagers([ana, bia, caio]) == {}
