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
from backend.core.enum import CashflowEventType, VoterValue
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


FOUND_PARTY = FoundPartyRequest(
    name="Partido A",
    abbr="AAA",
    color="#dc2626",
    flags=[
        VoterValue.STABILITY,
        VoterValue.DEVELOPMENT,
        VoterValue.SAVER_PROTECTION,
    ],
)


def test_each_player_gets_only_his_own_election_panel(radio: Radio):
    sim, ana, bruno = government_match()
    radio.listen("election_update", ana, bruno)

    sim.found_party(ana, FOUND_PARTY)

    panels = {
        to: payload for event, payload, to in radio.sent if event == "election_update"
    }
    assert set(panels) == {ana.client_id, bruno.client_id}
    assert panels[ana.client_id] == sim.get_election(ana).to_json()
    assert panels[bruno.client_id] == sim.get_election(bruno).to_json()


def test_the_panel_of_a_player_who_does_not_listen_is_not_sent(radio: Radio):
    sim, ana, _bruno = government_match()
    radio.listen("map_update", ana)

    sim.found_party(ana, FOUND_PARTY)

    recipients = [to for event, _payload, to in radio.sent if event == "map_update"]
    assert recipients == [ana.client_id]


def test_a_panel_equal_to_the_last_one_sent_is_not_sent_again(radio: Radio):
    sim, ana, _bruno = government_match()
    radio.listen("election_update", ana)
    sim.found_party(ana, FOUND_PARTY)
    sent = len(radio.sent)

    sim._government_feed.publish()

    assert len(radio.sent) == sent


def test_a_player_who_stops_listening_gets_the_panel_again_when_he_returns(
    radio: Radio,
):
    sim, ana, _bruno = government_match()
    radio.listen("election_update", ana)
    sim.found_party(ana, FOUND_PARTY)
    radio.listen("election_update")
    sim._government_feed.publish()
    radio.sent.clear()

    radio.listen("election_update", ana)
    sim._government_feed.publish()

    assert radio.events() == ["election_update"]


def test_the_government_changes_send_the_new_pending_list_to_whoever_listens(
    radio: Radio,
):
    sim, ana, bruno = government_match()
    radio.listen("pending_update", ana, bruno)

    sim.found_party(ana, FOUND_PARTY)

    recipients = {to for event, _p, to in radio.sent if event == "pending_update"}
    assert recipients == {ana.client_id, bruno.client_id}


def test_the_political_cash_of_the_personal_account_sends_the_new_portfolio(
    radio: Radio,
):
    sim, ana, bruno = government_match()
    radio.listen("portfolio_update", ana, bruno)
    radio.sent.clear()

    sim._cash_moved((ana.client_id,), None, CashflowEventType.CAMPAIGN_DONATION)

    portfolios = [
        (payload, to)
        for event, payload, to in radio.sent
        if event == "portfolio_update"
    ]
    assert [to for _payload, to in portfolios] == [ana.client_id]
    assert portfolios[0][0]["portfolio"] == sim.get_portfolio(ana.client_id).to_json()


def test_the_government_status_goes_only_to_the_player_who_listens(radio: Radio):
    sim, ana, bruno = government_match()
    radio.listen("government_status_update", bruno)

    sim.next_tick()

    statuses = [
        (payload, to)
        for event, payload, to in radio.sent
        if event == "government_status_update"
    ]
    assert len(statuses) == 1
    payload, to = statuses[0]
    assert to == bruno.client_id
    assert payload == sim.get_government_status(bruno).to_json()
    assert payload["is_president"] is False
    assert sim.get_government_status(ana).to_json() == payload


def test_the_government_status_equal_to_the_last_one_sent_is_not_sent_again(
    radio: Radio,
):
    sim, ana, _bruno = government_match()
    radio.listen("government_status_update", ana)
    sim._government_feed.publish()
    sent = len(radio.sent)

    sim._government_feed.publish()

    assert len(radio.sent) == sent


def test_the_government_status_is_a_slice_of_the_government_panel(radio: Radio):
    sim, ana, _bruno = government_match()

    status = sim.get_government_status(ana)
    panel = sim.get_governance(ana)

    assert status.computer_until_inauguration == panel.computer_until_inauguration
    assert status.is_president == panel.is_president
    assert status.next_vote == panel.next_vote
    assert status.queued_measures == len(
        [m for m in panel.queue if m.status == "QUEUED"]
    )
    assert (status.approval is None) == (panel.approval is None)
    if status.approval is not None and panel.approval is not None:
        assert status.approval.value == panel.approval.value
        assert status.approval.previous == panel.approval.previous
        assert status.approval.floor == panel.approval.floor
        assert status.approval.history == panel.approval.history
    assert (status.president is None) == (
        panel.term is None or panel.term.president is None
    )
