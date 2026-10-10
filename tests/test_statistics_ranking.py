from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.player_history import PlayerHistoryDTO
from backend.core.enum import VictoryCriterion
from backend.features.statistics.ranking import build_overview
from backend.routes.auth import UserRegisterRequest


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
        simulation_id=1,
        simulation_name="Simulação #1",
        starting_cash=Decimal(starting_cash),
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
