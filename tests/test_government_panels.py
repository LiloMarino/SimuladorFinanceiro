"""Os painéis do país ao vivo: orçamento, economia e base do Congresso saem por evento a quem os escuta."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from uuid import UUID

import pytest

from backend.core import repository
from backend.core.dto.government import FoundPartyRequest
from backend.core.dto.user import UserDTO
from backend.core.enum import VoterValue
from backend.core.player_colors import PLAYER_COLORS
from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.simulation.simulation import Simulation
from backend.features.simulation.simulation_loader import SimulationLoader
from tests.fakes import simulation_settings
from tests.test_simulation_loader import new_user, started  # noqa: F401

START = date(2004, 3, 1)
CASH = Decimal(10000)
PANELS = ("economy_update", "budget_update", "base_update")


class Radio:
    """O tempo real da partida: quem assina cada evento e o que saiu, com o destinatário."""

    def __init__(self) -> None:
        self.listeners: dict[str, set[UUID]] = {}
        self.sent: list[tuple[str, dict, UUID | None]] = []

    def listen(self, event: str, *clients: UserDTO) -> None:
        self.listeners[event] = {c.client_id for c in clients}

    def events(self) -> list[str]:
        return [event for event, _payload, _to in self.sent]


@pytest.fixture
def radio(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> Radio:
    """O tempo real mudo da sala vazia (fixture `started`), trocado por este que registra o envio."""
    request.getfixturevalue("started")
    radio = Radio()
    monkeypatch.setattr(
        RealtimeBrokerManager,
        "get_broker",
        lambda: SimpleNamespace(
            subscribed_clients=lambda event: radio.listeners.get(event, set()),
            notify=lambda event, payload, to=None: radio.sent.append(
                (event, payload, to)
            ),
        ),
    )
    return radio


def government_match(*, government: bool = True) -> tuple[Simulation, UserDTO, UserDTO]:
    """Partida com Ana e Bruno, com ou sem a expansão Governo & Política."""
    ana, bruno = new_user("Ana"), new_user("Bruno")
    for player in (ana, bruno):
        UserManager.player_auth(player.client_id)
    rules = simulation_settings().model_copy(
        update={
            "start_date": START,
            "end_date": date(2009, 12, 31),
            "starting_cash": CASH,
            "government_enabled": government,
            "first_election": date(2006, 10, 1),
        }
    )
    simulation_id = repository.simulation.create_simulation(rules)
    repository.simulation_player.save(
        simulation_id, {p.id: PLAYER_COLORS[i] for i, p in enumerate((ana, bruno))}
    )
    repository.portfolio.open(simulation_id, [ana.id, bruno.id], START, CASH)
    summary = repository.simulation.get_simulation(simulation_id)
    assert summary is not None
    SimulationLoader.load(summary)
    return SimulationManager.get_active_simulation(), ana, bruno


def test_the_close_of_the_day_sends_the_three_panels_to_whoever_listens(radio: Radio):
    sim, ana, _bruno = government_match()
    for event in PANELS:
        radio.listen(event, ana)

    sim.next_tick()

    assert sorted(e for e in radio.events() if e in PANELS) == sorted(PANELS)
    payloads = {event: payload for event, payload, _to in radio.sent}
    assert payloads["budget_update"] == sim.get_budget().to_json()
    assert payloads["economy_update"] == sim.get_economy_panel().to_json()
    assert payloads["base_update"] == sim.get_base(ana).to_json()


def test_nothing_is_built_without_listeners(radio: Radio):
    sim, _ana, _bruno = government_match()

    sim.next_tick()

    assert [e for e in radio.events() if e in PANELS] == []


def test_a_match_without_the_government_sends_only_the_economy(radio: Radio):
    sim, ana, _bruno = government_match(government=False)
    for event in PANELS:
        radio.listen(event, ana)

    sim.next_tick()

    assert [e for e in radio.events() if e in PANELS] == ["economy_update"]


def test_the_base_goes_only_to_the_player_who_listens(radio: Radio):
    sim, _ana, bruno = government_match()
    radio.listen("base_update", bruno)

    sim.next_tick()

    bases = [
        (payload, to) for event, payload, to in radio.sent if event == "base_update"
    ]
    assert len(bases) == 1
    payload, to = bases[0]
    assert to == bruno.client_id
    assert payload == sim.get_base(bruno).to_json()


def test_a_government_action_sends_the_panels_at_once(radio: Radio):
    sim, ana, _bruno = government_match()
    for event in PANELS:
        radio.listen(event, ana)

    sim.found_party(
        ana,
        FoundPartyRequest(
            name="Partido A",
            abbr="AAA",
            color="#dc2626",
            flags=[
                VoterValue.STABILITY,
                VoterValue.DEVELOPMENT,
                VoterValue.SAVER_PROTECTION,
            ],
        ),
    )

    assert sorted(e for e in radio.events() if e in PANELS) == sorted(PANELS)
