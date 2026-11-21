from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.player_history import PlayerHistoryDTO
from backend.core.enum import GameType, VictoryCriterion
from backend.features.statistics.ranking import build_overview
from backend.routes.auth import UserRegisterRequest

FELL = date(2020, 1, 20)


def player(
    nickname: str, networth: str, contribution: str = "0", starting_cash: str = "10000"
) -> PlayerHistoryDTO:
    snapshot = PatrimonialHistoryDTO(
        snapshot_date=date(2020, 1, 31),
        total_networth=Decimal(networth),
        total_equity=Decimal(0),
        total_fixed=Decimal(0),
        total_cash=Decimal(networth),
        total_contribution=Decimal(contribution),
    )
    return PlayerHistoryDTO(
        player_nickname=nickname,
        color="chart-1",
        simulation_id=1,
        simulation_name="Simulação #1",
        starting_cash=Decimal(starting_cash),
        goal_net_worth=Decimal("100000"),
        history=[snapshot],
    )


def test_return_is_measured_over_starting_cash_plus_contributions():
    """O aporte mensal entra no capital: patrimônio igual ao aportado é retorno zero."""
    report = build_overview([player("Lilo", networth="12000", contribution="2000")])

    entry = report.players[0]
    assert entry.total_networth == Decimal("12000")
    assert entry.return_value == Decimal("0")
    assert entry.return_percent == Decimal("0")


def test_zero_networth_is_a_total_loss():
    """Patrimônio zerado é perda de 100% do capital."""
    report = build_overview([player("Lilo", networth="0")])

    assert report.players[0].return_value == Decimal("-10000")
    assert report.players[0].return_percent == Decimal("-1")


def test_players_are_ranked_by_return_percent():
    """O ranking ordena pelo retorno percentual, do melhor para o pior, numerando as posições."""
    report = build_overview(
        [
            player("Ana", networth="11000"),
            player("Bia", networth="15000"),
            player("Caio", networth="9000"),
        ]
    )

    assert [(p.position, p.player_nickname) for p in report.players] == [
        (1, "Bia"),
        (2, "Ana"),
        (3, "Caio"),
    ]
    assert report.players[0].return_percent == Decimal("0.5")


def test_average_return_is_the_mean_of_player_returns():
    """A média da sala é a média simples dos retornos percentuais."""
    report = build_overview(
        [player("Ana", networth="11000"), player("Bia", networth="15000")]
    )

    assert report.average_return == Decimal("0.3")


def test_empty_report_has_no_average():
    """Sem jogadores não há média a exibir."""
    report = build_overview([])

    assert report.players == []
    assert report.average_return is None


def test_nickname_rejects_hash_separator():
    """O nickname recusa '#', que separa jogador e simulação nos rótulos da comparação."""
    with pytest.raises(ValidationError):
        UserRegisterRequest(nickname="Lilo#1")

    assert UserRegisterRequest(nickname="Lilo").nickname == "Lilo"


def test_networth_criterion_ranks_by_final_networth():
    """Com aporte maior, Ana tem mais patrimônio e menos retorno: o critério decide."""
    lilo = player("Lilo", networth="12000")
    ana = player("Ana", networth="15000", contribution="10000")

    by_return = build_overview([lilo, ana], VictoryCriterion.RETURN)
    by_networth = build_overview([lilo, ana], VictoryCriterion.NETWORTH)

    assert [p.player_nickname for p in by_return.players] == ["Lilo", "Ana"]
    assert [p.player_nickname for p in by_networth.players] == ["Ana", "Lilo"]
    assert by_networth.criterion is VictoryCriterion.NETWORTH


def test_leader_gap_is_the_distance_to_first_in_the_criterion():
    """Pelo patrimônio, quem tem R$ 11 mil fica a R$ 4 mil do líder com R$ 15 mil."""
    report = build_overview(
        [player("Ana", networth="11000"), player("Bia", networth="15000")],
        VictoryCriterion.NETWORTH,
    )

    gaps = {p.player_nickname: p.leader_gap for p in report.players}
    assert gaps == {"Bia": Decimal("0"), "Ana": Decimal("4000")}


def test_unexpected_count_follows_the_player_and_defaults_to_zero():
    report = build_overview(
        [player("Ana", networth="11000"), player("Bia", networth="12000")],
        unexpected={(1, "Ana"): 4},
    )

    counts = {p.player_nickname: p.unexpected_count for p in report.players}
    assert counts == {"Ana": 4, "Bia": 0}


def test_the_last_active_human_survives_even_when_an_eliminated_one_ranks_higher():
    """Com a Bia eliminada (patrimônio maior, congelado), a Ana é a única humana ativa e fica em 1º."""
    report = build_overview(
        [player("Ana", networth="11000"), player("Bia", networth="15000")],
        game_type=GameType.FUND_TAKEOVER,
        eliminated={(1, "Bia"): FELL},
    )

    assert [(p.player_nickname, p.eliminated, p.position) for p in report.players] == [
        ("Ana", False, 1),
        ("Bia", True, 2),
    ]
    assert report.survivor_nickname == "Ana"


def test_takeover_ranks_the_eliminated_from_the_last_to_fall_to_the_first():
    """Quem caiu por último vem logo depois do sobrevivente, mesmo com patrimônio menor."""
    report = build_overview(
        [
            player("Ana", networth="10000"),
            player("Bia", networth="30000"),
            player("Caio", networth="20000"),
            player("Duda", networth="25000"),
        ],
        game_type=GameType.FUND_TAKEOVER,
        eliminated={
            (1, "Bia"): date(2020, 1, 5),
            (1, "Caio"): date(2020, 1, 20),
            (1, "Duda"): date(2020, 1, 12),
        },
    )

    assert [p.player_nickname for p in report.players] == ["Ana", "Caio", "Duda", "Bia"]
    assert report.survivor_nickname == "Ana"


def test_takeover_breaks_a_tie_on_the_elimination_day_by_networth():
    report = build_overview(
        [
            player("Ana", networth="10000"),
            player("Bia", networth="20000"),
            player("Caio", networth="30000"),
        ],
        game_type=GameType.FUND_TAKEOVER,
        eliminated={(1, "Bia"): FELL, (1, "Caio"): FELL},
    )

    assert [p.player_nickname for p in report.players] == ["Ana", "Caio", "Bia"]


def test_takeover_gap_is_empty_for_an_eliminated_player_above_the_survivor():
    """Quem caiu com patrimônio maior não está atrás do 1º no valor: sem distância."""
    report = build_overview(
        [player("Ana", networth="10000"), player("Bia", networth="30000")],
        game_type=GameType.FUND_TAKEOVER,
        eliminated={(1, "Bia"): FELL},
    )

    assert [p.leader_gap for p in report.players] == [Decimal("0"), None]


def test_classic_ranking_follows_the_criterion_without_eliminations():
    """Sem eliminados (todas as partidas fora da aquisição hostil) o ranking segue só o critério."""
    players = [player("Ana", networth="11000"), player("Bia", networth="15000")]

    report = build_overview(players, VictoryCriterion.NETWORTH)

    assert [p.player_nickname for p in report.players] == ["Bia", "Ana"]
    assert report.survivor_nickname is None


def test_without_eliminated_players_nobody_is_the_survivor():
    report = build_overview([player("Ana", networth="11000")])

    assert report.survivor_nickname is None


def test_two_active_humans_left_means_no_survivor_yet():
    report = build_overview(
        [
            player("Ana", networth="11000"),
            player("Bia", networth="15000"),
            player("Caio", networth="9000"),
        ],
        eliminated={(1, "Caio"): FELL},
    )

    assert report.survivor_nickname is None
