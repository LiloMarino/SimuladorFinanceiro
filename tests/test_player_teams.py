"""Equipes da sala: cada um escolhe a sua, "distribuir" completa quem falta, a partida só
começa com todo mundo numa equipe e quem já jogou a partida salva não troca."""

from __future__ import annotations

from collections.abc import Callable

import pytest
from fastapi import HTTPException

from backend.core.enum import PlayerGrouping
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.user_manager import UserManager
from tests.conftest import Join
from tests.fakes import simulation_settings


def refusal(action: Callable[[], object], status: int = 409) -> str:
    with pytest.raises(HTTPException) as error:
        action()
    assert error.value.status_code == status
    return str(error.value.detail)


def test_each_player_picks_their_own_team(team_room: Join):
    ana, bia = team_room("Ana"), team_room("Bia")

    UserManager.set_team(ana.client_id, 3)
    UserManager.set_team(bia.client_id, 3)

    assert UserManager.room_teams() == {ana.id: 3, bia.id: 3}
    assert UserManager.get_team(ana.id) == 3


def test_new_players_start_without_a_team(team_room: Join):
    ana = team_room("Ana")

    assert UserManager.get_team(ana.id) is None
    assert UserManager.room_teams() == {}


def test_a_team_that_does_not_exist_is_refused(team_room: Join):
    ana = team_room("Ana")

    refusal(lambda: UserManager.set_team(ana.client_id, 0), status=422)
    refusal(lambda: UserManager.set_team(ana.client_id, 11), status=422)


def test_individual_game_has_no_teams(team_room: Join, monkeypatch: pytest.MonkeyPatch):
    ana = team_room("Ana")
    monkeypatch.setattr(
        SettingsManager, "_settings", simulation_settings(PlayerGrouping.INDIVIDUAL)
    )

    refusal(lambda: UserManager.set_team(ana.client_id, 1))
    assert UserManager.get_team(ana.id) is None
    assert UserManager.room_teams() == {}


def test_distribute_puts_everyone_on_the_smallest_team(team_room: Join):
    ana, bia, caio, duda = (team_room(n) for n in ("Ana", "Bia", "Caio", "Duda"))
    UserManager.set_team(ana.client_id, 2)

    UserManager.distribute_teams()

    teams = UserManager.room_teams()
    assert teams[ana.id] == 2
    assert teams[bia.id] == 1
    # Quatro jogadores em duas equipes ficam 2 contra 2
    assert teams[caio.id] == 1
    assert teams[duda.id] == 2


def test_distribute_without_teams_opens_the_first_two(team_room: Join):
    players = [team_room(n) for n in ("Ana", "Bia", "Caio")]

    UserManager.distribute_teams()

    assert [UserManager.get_team(p.id) for p in players] == [1, 2, 1]


def test_distribute_with_one_team_formed_opens_another(team_room: Join):
    ana, bia = team_room("Ana"), team_room("Bia")
    UserManager.set_team(ana.client_id, 5)

    UserManager.distribute_teams()

    assert UserManager.get_team(ana.id) == 5
    assert UserManager.get_team(bia.id) == 1


def test_switching_back_to_individual_clears_the_teams(team_room: Join):
    ana = team_room("Ana")
    UserManager.set_team(ana.client_id, 4)

    UserManager.reset_teams()

    assert UserManager.get_team(ana.id) is None


def test_start_is_refused_while_someone_has_no_team(team_room: Join):
    ana, _ = team_room("Ana"), team_room("Bia")
    UserManager.set_team(ana.client_id, 1)

    message = refusal(lambda: UserManager.ensure_teams_ready({}))

    assert "Bia" in message
    assert "Ana" not in message


def test_start_needs_at_least_two_teams(team_room: Join):
    ana, bia = team_room("Ana"), team_room("Bia")
    UserManager.set_team(ana.client_id, 1)
    UserManager.set_team(bia.client_id, 1)

    message = refusal(lambda: UserManager.ensure_teams_ready({}))

    assert "pelo menos duas" in message


def test_start_with_two_teams_passes(team_room: Join):
    ana, bia = team_room("Ana"), team_room("Bia")
    UserManager.set_team(ana.client_id, 1)
    UserManager.set_team(bia.client_id, 2)

    UserManager.ensure_teams_ready({})


def test_saved_match_players_count_their_saved_team(team_room: Join):
    """Quem já jogou a partida salva traz a equipe dela; ausente conta para as duas equipes."""
    ana = team_room("Ana")
    UserManager.set_team(ana.client_id, 1)

    UserManager.ensure_teams_ready({ana.id: 1, 99: 2})


def test_player_of_the_saved_match_cannot_switch_team(team_room: Join):
    ana, bia = team_room("Ana"), team_room("Bia")

    UserManager.apply_saved_colors({ana.id: "chart-1"}, {ana.id: 2})

    assert UserManager.get_team(ana.id) == 2
    assert UserManager.get_team(bia.id) is None
    refusal(lambda: UserManager.set_team(ana.client_id, 1))
    UserManager.set_team(bia.client_id, 1)


def test_releasing_the_selection_unlocks_the_team(team_room: Join):
    ana = team_room("Ana")
    UserManager.apply_saved_colors({ana.id: "chart-1"}, {ana.id: 2})

    UserManager.release_saved_colors()

    UserManager.set_team(ana.client_id, 1)
    assert UserManager.get_team(ana.id) == 1


def test_team_survives_a_reconnection(team_room: Join):
    ana = team_room("Ana")
    UserManager.set_team(ana.client_id, 3)

    UserManager.unregister(ana.client_id)
    team_room("Ana")

    assert UserManager.get_team(ana.id) == 3
