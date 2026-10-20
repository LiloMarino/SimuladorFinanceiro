from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.player_history import PlayerHistoryDTO
from backend.core.enum import GameType
from backend.features.simulation.goal import goal_reached
from backend.features.simulation.saved_simulation import leader_reached_goal
from backend.features.statistics.ranking import build_overview
from backend.routes.simulation import CreateSimulationRequest

GOAL = Decimal(100000)


def player(nickname: str, networth: str, team: int | None = None) -> PlayerHistoryDTO:
    return PlayerHistoryDTO(
        player_nickname=nickname,
        color="chart-1",
        simulation_id=1,
        simulation_name="Simulação #1",
        team=team,
        starting_cash=Decimal(10000),
        goal_net_worth=GOAL,
        history=[
            PatrimonialHistoryDTO(
                snapshot_date=date(2020, 1, 31),
                total_networth=Decimal(networth),
                total_equity=Decimal(0),
                total_fixed=Decimal(0),
                total_cash=Decimal(networth),
                total_contribution=Decimal(0),
            )
        ],
    )


def race(*players: PlayerHistoryDTO, in_teams: bool = False):
    return build_overview(
        list(players),
        game_type=GameType.GOAL_RACE,
        goal_net_worth=GOAL,
        in_teams=in_teams,
    )


def test_a_player_on_the_goal_ends_the_race():
    assert goal_reached({1: Decimal(100000), 2: Decimal(5)}, {}, GOAL, in_teams=False)
    assert not goal_reached({1: Decimal(99999)}, {}, GOAL, in_teams=False)


def test_in_teams_the_mean_of_the_members_must_reach_the_goal():
    """Um membro sozinho passando da meta não basta: conta a média da equipe."""
    networths = {1: Decimal(150000), 2: Decimal(40000), 3: Decimal(90000)}
    teams = {1: 1, 2: 1, 3: 2}

    assert not goal_reached(networths, teams, GOAL, in_teams=True)
    assert goal_reached({**networths, 2: Decimal(50000)}, teams, GOAL, in_teams=True)


def test_ranking_value_is_the_fraction_of_the_goal():
    report = race(player("Lilo", "25000"))

    assert report.players[0].criterion_value == Decimal("0.25")
    assert report.game_type is GameType.GOAL_RACE
    assert report.goal_net_worth == GOAL


def test_two_on_the_goal_the_same_day_the_bigger_networth_wins():
    report = race(player("Ana", "100000"), player("Bia", "120000"))

    assert [p.player_nickname for p in report.players] == ["Bia", "Ana"]


def test_nobody_on_the_goal_the_closest_wins():
    report = race(player("Ana", "40000"), player("Bia", "60000"))

    assert report.players[0].player_nickname == "Bia"
    assert report.players[1].leader_gap == Decimal("0.2")


def test_team_fraction_is_the_mean_networth_over_the_goal():
    report = race(
        player("Ana", "150000", team=1),
        player("Bia", "50000", team=1),
        player("Caio", "90000", team=2),
        in_teams=True,
    )

    assert report.teams[0].team == 1
    assert report.teams[0].criterion_value == Decimal(1)


def test_saved_race_is_finished_when_the_leader_reached_the_goal():
    assert leader_reached_goal(race(player("Ana", "100000"), player("Bia", "10")))
    assert not leader_reached_goal(race(player("Ana", "99999")))


def test_classic_match_never_finishes_by_goal():
    report = build_overview([player("Ana", "500000")])

    assert not leader_reached_goal(report)


def _request(game_type: GameType, goal: str) -> CreateSimulationRequest:
    return CreateSimulationRequest(
        name="Corrida",
        start_date=date(2020, 1, 1),
        end_date=date(2020, 12, 31),
        starting_cash=Decimal(10000),
        price_impact_k=0.02,
        price_impact_decay_days=20,
        game_type=game_type,
        goal_net_worth=Decimal(goal),
    )


def test_goal_must_be_above_the_starting_cash_in_the_race():
    with pytest.raises(ValidationError, match="maior que o saldo inicial"):
        _request(GameType.GOAL_RACE, "10000")
    assert _request(GameType.GOAL_RACE, "10001").goal_net_worth == Decimal(10001)


def test_classic_match_ignores_the_goal():
    assert _request(GameType.CLASSIC, "100").game_type is GameType.CLASSIC
