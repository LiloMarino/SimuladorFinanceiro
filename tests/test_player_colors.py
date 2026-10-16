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

    assert "só cabem mais 3" in refusal(lambda: UserManager.apply_saved_colors(saved))


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


# =========================
# Overflow da partida salva (partida cheia para a sala)
# =========================


def saved_match(players: int) -> dict[int, str]:
    """Partida salva com `players` jogadores (ids 101...), cada um com uma cor."""
    return {101 + n: PLAYER_COLORS[n] for n in range(players)}


def room_with_newcomers(join: Join, newcomers: int) -> list[UserDTO]:
    return [join(f"Novo{n}") for n in range(newcomers)]


@pytest.mark.parametrize(
    ("saved", "newcomers"),
    [(4, 3), (8, 2), (10, 0)],
)
def test_saved_match_that_fits_the_room_is_selectable(
    join: Join, saved: int, newcomers: int
):
    players = room_with_newcomers(join, newcomers)
    colors = saved_match(saved)

    assert UserManager.room_overflow(colors) == []
    UserManager.apply_saved_colors(colors)

    # Cada novato fica com uma cor que a partida não usa
    new_colors = [color_of(p) for p in players]
    assert len(set(new_colors)) == newcomers
    assert not set(new_colors) & set(colors.values())


@pytest.mark.parametrize(("saved", "newcomers"), [(8, 3), (10, 1)])
def test_saved_match_that_does_not_fit_is_refused_with_the_names(
    join: Join, saved: int, newcomers: int
):
    players = room_with_newcomers(join, newcomers)
    before = {p.nickname: color_of(p) for p in players}
    colors = saved_match(saved)

    assert sorted(UserManager.room_overflow(colors)) == sorted(before)
    message = refusal(lambda: UserManager.apply_saved_colors(colors))

    assert all(nickname in message for nickname in before)
    # Recusada, a sala fica como estava e nada fica reservado
    assert {p.nickname: color_of(p) for p in players} == before
    assert UserManager._saved_colors == {}


def test_offline_players_of_the_saved_match_still_hold_their_slot(join: Join):
    # 10 jogaram, 6 estão offline: só 4 deles na sala, mais 1 que nunca jogou
    colors = saved_match(10)
    for user_id in list(colors)[:4]:
        user = UserDTO(
            id=user_id, client_id=client(f"P{user_id}"), nickname=f"P{user_id}"
        )
        UserManager._client_user_cache[user.client_id] = user
        UserManager.player_auth(user.client_id)
    join("Novato")

    assert UserManager.room_overflow(colors) == ["Novato"]


def test_room_filled_by_reserved_colors_explains_the_reservation(join: Join):
    UserManager.apply_saved_colors(saved_match(9))
    join("Novo")  # pega a única cor que sobra

    late = UserDTO(id=99, client_id=client("Late"), nickname="Late")
    UserManager._client_user_cache[late.client_id] = late

    assert "offline" in refusal(
        lambda: UserManager.player_auth(late.client_id), status=423
    )


# =========================
# Entrar no meio da partida (hot-join)
# =========================


class MatchStore:
    """Participantes da partida em andamento, em memória, no lugar de `simulation_players`."""

    def __init__(self, participants: dict[int, tuple[str, str]]):
        # user_id -> (apelido, cor)
        self.participants = participants

    def colors(self, _simulation_id: int) -> dict[int, str]:
        return {uid: color for uid, (_, color) in self.participants.items()}

    def participants_of(self, _simulation_id: int) -> list[UserDTO]:
        return [
            UserDTO(id=uid, client_id=client(nick), nickname=nick)
            for uid, (nick, _) in self.participants.items()
        ]

    def save(self, _simulation_id: int, colors: dict[int, str]) -> None:
        for uid, color in colors.items():
            self.participants[uid] = (f"U{uid}", color)


class FakeRunningSimulation:
    def __init__(self):
        self.added: list[UserDTO] = []

    def add_player(self, user: UserDTO) -> None:
        self.added.append(user)


type StartMatch = Callable[[dict[int, tuple[str, str]]], FakeRunningSimulation]


@pytest.fixture
def start_match(monkeypatch: pytest.MonkeyPatch, join: Join) -> StartMatch:
    """Partida em andamento com os participantes informados (`user_id -> (apelido, cor)`)."""

    def _start(participants: dict[int, tuple[str, str]]) -> FakeRunningSimulation:
        store = MatchStore(dict(participants))
        sim = FakeRunningSimulation()
        monkeypatch.setattr(SimulationManager, "_active_simulation", sim)
        monkeypatch.setattr(SimulationManager, "_simulation_id", 1)
        monkeypatch.setattr(repository.simulation_player, "colors", store.colors)
        monkeypatch.setattr(
            repository.simulation_player, "participants", store.participants_of
        )
        monkeypatch.setattr(repository.simulation_player, "save", store.save)
        return sim

    return _start


def register(nickname: str, user_id: int) -> UserDTO:
    user = UserDTO(id=user_id, client_id=client(nickname), nickname=nickname)
    UserManager._client_user_cache[user.client_id] = user
    return user


def test_late_player_authenticates_pending_without_a_slot_in_the_room(
    start_match: StartMatch,
):
    start_match({1: ("Ana", PLAYER_COLORS[0])})
    late = register("Duda", 4)

    assert UserManager.player_auth(late.client_id) == late
    assert UserManager.is_pending_join(late)
    assert UserManager.room_colors() == {}
    assert color_of(late) is None


def test_full_match_refuses_the_late_player_counting_the_offline_ones(
    start_match: StartMatch,
):
    start_match({n: (f"P{n}", PLAYER_COLORS[n - 1]) for n in range(1, 11)})
    late = register("Duda", 99)

    message = refusal(lambda: UserManager.player_auth(late.client_id), status=423)

    assert "10 jogadores" in message
    assert "10 deles offline" in message


def test_join_match_takes_the_free_color_and_the_deposit(start_match: StartMatch):
    sim = start_match({1: ("Ana", PLAYER_COLORS[0])})
    late = register("Duda", 4)
    UserManager.player_auth(late.client_id)

    UserManager.join_match(late.client_id, PLAYER_COLORS[3])

    assert sim.added == [late]
    assert color_of(late) == PLAYER_COLORS[3]
    assert not UserManager.is_pending_join(late)
    assert repository.simulation_player.colors(1)[late.id] == PLAYER_COLORS[3]


def test_join_match_with_a_taken_color_is_refused_and_nothing_is_saved(
    start_match: StartMatch,
):
    sim = start_match({1: ("Ana", PLAYER_COLORS[0])})
    late = register("Duda", 4)

    message = refusal(lambda: UserManager.join_match(late.client_id, PLAYER_COLORS[0]))

    assert message == "Ana pegou essa cor antes."
    assert sim.added == []
    assert late.id not in repository.simulation_player.colors(1)


def test_eleventh_player_cannot_join_the_match(start_match: StartMatch):
    start_match({n: (f"P{n}", PLAYER_COLORS[n - 1]) for n in range(1, 11)})
    late = register("Duda", 99)

    refusal(
        lambda: UserManager.join_match(late.client_id, PLAYER_COLORS[0]), status=423
    )

    assert late.id not in repository.simulation_player.colors(1)


def test_participant_cannot_join_twice(start_match: StartMatch):
    start_match({1: ("Ana", PLAYER_COLORS[0])})
    ana = register("Ana", 1)

    refusal(lambda: UserManager.join_match(ana.client_id, PLAYER_COLORS[5]))


def test_player_who_left_and_returned_keeps_the_match_color(
    start_match: StartMatch,
):
    start_match({1: ("Ana", PLAYER_COLORS[2])})
    ana = register("Ana", 1)
    UserManager.player_auth(ana.client_id)
    UserManager.unregister(ana.client_id)

    UserManager.player_auth(ana.client_id)

    assert color_of(ana) == PLAYER_COLORS[2]
