"""Atividade de cada jogador na sala: guardada por aba, mostrada pela mais relevante e
avisada à sala só quando o selo muda."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

from backend.core.dto.user import UserDTO
from backend.core.enum import PlayerActivity
from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.routes.simulation import get_active_players
from tests.conftest import _SilentRealtimeBroker
from tests.fakes import client, simulation_settings

type Join = Callable[[str], UserDTO]
type Sent = list[tuple[str, dict[str, Any]]]

LOBBY = PlayerActivity.LOBBY
SETTINGS = PlayerActivity.SETTINGS
AWAY = PlayerActivity.AWAY


class _RecordingBroker(_SilentRealtimeBroker):
    def __init__(self, sent: Sent) -> None:
        self.sent = sent

    def notify(self, *args: Any, **_kwargs: object) -> None:
        event, payload = args[:2]
        self.sent.append((event, payload))


@pytest.fixture
def sent(monkeypatch: pytest.MonkeyPatch) -> Sent:
    """Eventos realtime emitidos, na ordem, com a sala vazia e sem partida."""
    events: Sent = []
    monkeypatch.setattr(UserManager, "_active_players", {})
    monkeypatch.setattr(UserManager, "_colors", {})
    monkeypatch.setattr(UserManager, "_saved_colors", {})
    monkeypatch.setattr(UserManager, "_teams", {})
    monkeypatch.setattr(UserManager, "_saved_teams", {})
    monkeypatch.setattr(UserManager, "_activities", {})
    monkeypatch.setattr(SettingsManager, "_settings", simulation_settings())
    monkeypatch.setattr(SettingsManager, "_selected_simulation_id", None)
    monkeypatch.setattr(SimulationManager, "_active_simulation", None)
    monkeypatch.setattr(SimulationManager, "_simulation_id", None)
    monkeypatch.setattr(
        RealtimeBrokerManager, "get_broker", lambda: _RecordingBroker(events)
    )
    return events


@pytest.fixture
def join(sent: Sent) -> Join:
    users: dict[str, UserDTO] = {}

    def _join(nickname: str) -> UserDTO:
        user = users.setdefault(
            nickname,
            UserDTO(id=len(users) + 1, client_id=client(nickname), nickname=nickname),
        )
        UserManager._client_user_cache[user.client_id] = user
        UserManager.player_auth(user.client_id)
        return user

    return _join


def activity_of(user: UserDTO) -> PlayerActivity | None:
    return UserManager.room_activities()[user.id]


def activity_events(sent: Sent) -> list[tuple[str, str | None]]:
    return [
        (payload["nickname"], payload["activity"])
        for event, payload in sent
        if event == "player_activity"
    ]


def test_player_without_a_notice_is_online(join: Join):
    ana = join("Ana")

    assert activity_of(ana) is None


def test_notice_sets_the_activity_and_tells_the_room(join: Join, sent: Sent):
    ana = join("Ana")

    UserManager.set_activity(ana.client_id, "tab-1", LOBBY)

    assert activity_of(ana) is LOBBY
    assert activity_events(sent) == [("Ana", "lobby")]


def test_repeating_the_same_notice_does_not_tell_the_room_again(join: Join, sent: Sent):
    ana = join("Ana")

    UserManager.set_activity(ana.client_id, "tab-1", LOBBY)
    UserManager.set_activity(ana.client_id, "tab-1", LOBBY)

    assert activity_events(sent) == [("Ana", "lobby")]


def test_activity_event_carries_color_and_team(join: Join, sent: Sent):
    ana = join("Ana")

    UserManager.set_activity(ana.client_id, "tab-1", LOBBY)

    _, payload = sent[-1]
    assert payload["color"] == UserManager.get_color(ana.id)
    assert payload["team"] is None


def test_notice_before_joining_the_room_shows_up_on_join(join: Join, sent: Sent):
    # A aba avisa assim que conecta, antes de a autenticação pôr o jogador na sala
    UserManager.set_activity(client("Ana"), "tab-1", SETTINGS)

    ana = join("Ana")

    assert activity_of(ana) is SETTINGS
    join_payload = next(p for e, p in sent if e == "player_join")
    assert join_payload["activity"] == "settings"
    assert activity_events(sent) == []


def test_other_presence_events_carry_the_activity(join: Join, sent: Sent):
    ana = join("Ana")
    UserManager.set_activity(ana.client_id, "tab-1", LOBBY)

    UserManager.set_color(ana.client_id, "chart-5")

    color_payload = next(p for e, p in sent if e == "player_color")
    assert color_payload["activity"] == "lobby"


def test_tab_in_view_wins_over_an_away_tab(join: Join):
    ana = join("Ana")

    UserManager.set_activity(ana.client_id, "tab-1", LOBBY)
    UserManager.set_activity(ana.client_id, "tab-2", AWAY)

    assert activity_of(ana) is LOBBY


def test_latest_notice_wins_among_tabs_in_view(join: Join):
    ana = join("Ana")

    UserManager.set_activity(ana.client_id, "tab-1", LOBBY)
    UserManager.set_activity(ana.client_id, "tab-2", SETTINGS)
    assert activity_of(ana) is SETTINGS

    UserManager.set_activity(ana.client_id, "tab-1", LOBBY)
    assert activity_of(ana) is LOBBY


def test_all_tabs_away_is_away(join: Join):
    ana = join("Ana")

    UserManager.set_activity(ana.client_id, "tab-1", AWAY)
    UserManager.set_activity(ana.client_id, "tab-2", AWAY)

    assert activity_of(ana) is AWAY


def test_closing_a_tab_hands_the_badge_to_the_ones_left(join: Join, sent: Sent):
    ana = join("Ana")
    UserManager.set_activity(ana.client_id, "tab-1", LOBBY)
    UserManager.set_activity(ana.client_id, "tab-2", SETTINGS)

    UserManager.drop_activity(ana.client_id, "tab-2")

    assert activity_of(ana) is LOBBY
    assert activity_events(sent)[-1] == ("Ana", "lobby")


def test_closing_a_tab_that_is_not_showing_stays_quiet(join: Join, sent: Sent):
    ana = join("Ana")
    UserManager.set_activity(ana.client_id, "tab-1", LOBBY)
    UserManager.set_activity(ana.client_id, "tab-2", AWAY)
    before = len(sent)

    UserManager.drop_activity(ana.client_id, "tab-2")

    assert len(sent) == before


def test_dropping_an_unknown_tab_changes_nothing(join: Join, sent: Sent):
    ana = join("Ana")

    UserManager.drop_activity(ana.client_id, "tab-9")

    assert activity_of(ana) is None
    assert activity_events(sent) == []


def test_leaving_the_room_forgets_the_activity(join: Join):
    ana = join("Ana")
    UserManager.set_activity(ana.client_id, "tab-1", LOBBY)

    UserManager.unregister(ana.client_id)
    join("Ana")

    assert activity_of(ana) is None


def test_logout_forgets_the_activity(join: Join):
    ana = join("Ana")
    UserManager.set_activity(ana.client_id, "tab-1", LOBBY)

    UserManager.player_logout(ana.client_id)
    join("Ana")

    assert activity_of(ana) is None


def test_activity_of_each_player_is_independent(join: Join):
    ana, bia = join("Ana"), join("Bia")

    UserManager.set_activity(ana.client_id, "tab-1", LOBBY)

    assert UserManager.room_activities() == {ana.id: LOBBY, bia.id: None}


def test_room_list_route_returns_the_activity_of_each_player(join: Join):
    ana, _ = join("Ana"), join("Bia")
    UserManager.set_activity(ana.client_id, "tab-1", LOBBY)

    players = {p.nickname: p.activity for p in get_active_players()}

    assert players == {"Ana": LOBBY, "Bia": None}
