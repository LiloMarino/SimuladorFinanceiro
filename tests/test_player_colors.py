"""Cor exclusiva por jogador: a sala nunca repete cor, recusa o 11º e trava as cores
de quem já jogou a partida salva selecionada."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlalchemy import Engine, text

from backend.core import repository
from backend.core.dto.simulation import SimulationSettingsDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import VictoryCriterion
from backend.core.player_colors import MAX_PLAYERS, PLAYER_COLORS
from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from tests.conftest import _SilentRealtimeBroker
from tests.fakes import client

type Join = Callable[[str], UserDTO]


@pytest.fixture
def join(monkeypatch: pytest.MonkeyPatch) -> Join:
    """Sala vazia e sem partida; `join("Ana")` conecta um jogador e devolve o usuário."""
    monkeypatch.setattr(UserManager, "_active_players", {})
    monkeypatch.setattr(UserManager, "_colors", {})
    monkeypatch.setattr(UserManager, "_saved_colors", {})
    monkeypatch.setattr(SimulationManager, "_active_simulation", None)
    monkeypatch.setattr(SimulationManager, "_simulation_id", None)
    monkeypatch.setattr(
        RealtimeBrokerManager, "get_broker", lambda: _SilentRealtimeBroker()
    )
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


def color_of(user: UserDTO) -> str | None:
    return UserManager.get_color(user.id)


def refusal(action: Callable[[], object], status: int = 409) -> str:
    with pytest.raises(HTTPException) as error:
        action()
    assert error.value.status_code == status
    return str(error.value.detail)


def test_each_player_joins_with_a_different_color(join: Join):
    players = [join(name) for name in ("Ana", "Bia", "Caio")]

    assert [color_of(p) for p in players] == list(PLAYER_COLORS[:3])


def test_color_taken_by_another_player_is_refused_and_the_previous_stays(join: Join):
    ana, bia = join("Ana"), join("Bia")
    assert color_of(ana) == PLAYER_COLORS[0]

    message = refusal(lambda: UserManager.set_color(bia.client_id, PLAYER_COLORS[0]))

    assert message == "Ana pegou essa cor antes."
    assert color_of(bia) == PLAYER_COLORS[1]


def test_free_color_is_taken_and_the_old_one_is_released(join: Join):
    ana, bia = join("Ana"), join("Bia")

    UserManager.set_color(ana.client_id, PLAYER_COLORS[5])
    UserManager.set_color(bia.client_id, PLAYER_COLORS[0])

    assert (color_of(ana), color_of(bia)) == (PLAYER_COLORS[5], PLAYER_COLORS[0])


def test_color_outside_the_palette_is_rejected(join: Join):
    ana = join("Ana")

    with pytest.raises(HTTPException) as error:
        UserManager.set_color(ana.client_id, "chart-11")

    assert error.value.status_code == 422


def test_eleventh_player_is_refused(join: Join):
    players = [join(f"P{n}") for n in range(MAX_PLAYERS)]
    assert len({color_of(p) for p in players}) == MAX_PLAYERS

    late = UserDTO(id=99, client_id=client("Late"), nickname="Late")
    UserManager._client_user_cache[late.client_id] = late

    assert "sala está cheia" in refusal(
        lambda: UserManager.player_auth(late.client_id), status=423
    )


def test_leaving_frees_the_color(join: Join):
    ana, bia = join("Ana"), join("Bia")
    UserManager.unregister(ana.client_id)

    carol = join("Carol")

    assert color_of(carol) == PLAYER_COLORS[0]
    assert color_of(bia) == PLAYER_COLORS[1]


def test_saved_match_restores_colors_and_locks_who_played(join: Join):
    ana, bia, caio = join("Ana"), join("Bia"), join("Caio")
    # Ana e Bia jogaram a partida; Caio nunca entrou; Duda jogou e está ausente
    saved = {ana.id: PLAYER_COLORS[2], bia.id: PLAYER_COLORS[0], 4: PLAYER_COLORS[1]}

    UserManager.apply_saved_colors(saved)

    assert color_of(ana) == PLAYER_COLORS[2]
    assert color_of(bia) == PLAYER_COLORS[0]
    # Caio tinha chart-3, que agora é da Ana: ganha a primeira livre depois das reservadas
    assert color_of(caio) == PLAYER_COLORS[3]
    assert "partida selecionada" in refusal(
        lambda: UserManager.set_color(ana.client_id, PLAYER_COLORS[7])
    )
    # A cor da Duda ausente continua reservada para ela
    assert "partida selecionada" in refusal(
        lambda: UserManager.set_color(caio.client_id, PLAYER_COLORS[1])
    )
    UserManager.set_color(caio.client_id, PLAYER_COLORS[7])
    assert color_of(caio) == PLAYER_COLORS[7]


def test_releasing_the_selection_unlocks_the_colors(join: Join):
    ana = join("Ana")
    UserManager.apply_saved_colors({ana.id: PLAYER_COLORS[4]})

    UserManager.release_saved_colors()
    UserManager.set_color(ana.client_id, PLAYER_COLORS[8])

    assert color_of(ana) == PLAYER_COLORS[8]


def test_selection_that_does_not_fit_the_palette_is_refused(join: Join):
    for n in range(4):
        join(f"Novo{n}")
    saved = {100 + n: PLAYER_COLORS[n] for n in range(MAX_PLAYERS - 3)}

    assert "passa de" in refusal(lambda: UserManager.apply_saved_colors(saved))


def new_simulation(name: str) -> int:
    return repository.simulation.create_simulation(
        SimulationSettingsDTO(
            name=name,
            start_date=date(2020, 1, 1),
            end_date=date(2020, 12, 31),
            starting_cash=Decimal(1000),
            monthly_contribution=Decimal(0),
            price_impact_enabled=False,
            price_impact_k=0.0,
            price_impact_decay_days=1,
            victory_criterion=VictoryCriterion.SCORE,
        )
    )


def test_only_the_room_players_are_participants_with_the_deposit(database: Engine):
    ana = repository.user.create_user(client("Ana"), "Ana")
    bia = repository.user.create_user(client("Bia"), "Bia")
    repository.user.create_user(client("Caio"), "Caio")  # conta fora da sala
    simulation_id = new_simulation("Partida")

    repository.simulation_player.save(
        simulation_id, {ana.id: PLAYER_COLORS[3], bia.id: PLAYER_COLORS[0]}
    )
    repository.user.seed_simulation_users(
        simulation_id, [ana.id, bia.id], date(2020, 1, 1), Decimal(1000)
    )

    assert repository.simulation_player.colors(simulation_id) == {
        ana.id: PLAYER_COLORS[3],
        bia.id: PLAYER_COLORS[0],
    }
    assert {
        p.nickname for p in repository.simulation_player.participants(simulation_id)
    } == {
        "Ana",
        "Bia",
    }
    with database.connect() as connection:
        deposits = connection.execute(
            text("SELECT count(*) FROM event_cashflow WHERE simulation_id = :id"),
            {"id": simulation_id},
        ).scalar_one()
    assert deposits == 2


def test_saving_again_changes_the_color_of_who_is_already_a_participant(
    database: Engine,
):
    ana = repository.user.create_user(client("Ana"), "Ana")
    simulation_id = new_simulation("Partida")

    repository.simulation_player.save(simulation_id, {ana.id: PLAYER_COLORS[0]})
    repository.simulation_player.save(simulation_id, {ana.id: PLAYER_COLORS[6]})

    assert repository.simulation_player.colors(simulation_id) == {
        ana.id: PLAYER_COLORS[6]
    }
