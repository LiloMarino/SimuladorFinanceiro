"""Modo em equipes nas estatísticas: o valor da equipe é a média dos membros em cada
critério, quem não tem o valor fica fora da média, o patrimônio médio desempata e
volume, IR e negócios somam."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.player_history import PlayerHistoryDTO
from backend.core.dto.statistics_report import (
    MonthlyVolumeDTO,
    PlayerOperationsDTO,
    PlayerReturnsDTO,
    PlayerScoreHistoryDTO,
    SeriesPointDTO,
)
from backend.core.enum import PlayerGrouping, TeamNaming, VictoryCriterion
from backend.features.statistics.ranking import build_overview
from backend.features.statistics.score import MIN_SCORE_DAYS, score_history
from backend.features.statistics.teams import (
    mean,
    mean_series,
    team_operations,
    team_returns,
    team_score_history,
)
from tests.conftest import SetIndicator


def history(networths: list[str]) -> list[PatrimonialHistoryDTO]:
    start = date(2020, 1, 1)
    return [
        PatrimonialHistoryDTO(
            snapshot_date=start + timedelta(days=offset),
            total_networth=Decimal(n),
            total_equity=Decimal(0),
            total_fixed=Decimal(0),
            total_cash=Decimal(n),
            total_contribution=Decimal(0),
        )
        for offset, n in enumerate(networths)
    ]


def member(
    nickname: str,
    team: int | None,
    networth: str = "10000",
    starting_cash: str = "10000",
    days: list[str] | None = None,
) -> PlayerHistoryDTO:
    return PlayerHistoryDTO(
        player_nickname=nickname,
        color="chart-1",
        simulation_id=1,
        simulation_name="Simulação #1",
        team=team,
        is_bot=False,
        starting_cash=Decimal(starting_cash),
        goal_net_worth=Decimal("100000"),
        history=history(days or [networth]),
    )


def teams_of(report):
    return {t.team: t for t in report.teams}


def test_team_score_history_ends_at_the_team_score(indicators: SetIndicator):
    """O último ponto da equipe é a nota dela no ranking, com quem ainda não tem nota fora."""
    players = [
        member("Ana", 1, days=[str(10000 + i * 5) for i in range(100)]),
        member("Bia", 1, days=[str(10000 + (i % 5) * 40) for i in range(100)]),
        member("Caio", 1, days=["10000", "12000"]),
    ]
    team = teams_of(build_overview(players, in_teams=True))[1]

    entries = [
        PlayerScoreHistoryDTO(
            player_nickname=p.player_nickname,
            color=p.color,
            simulation_id=p.simulation_id,
            simulation_name=p.simulation_name,
            team=p.team,
            is_bot=p.is_bot,
            points=score_history(p.history),
        )
        for p in players
    ]
    [series] = team_score_history(entries)

    assert team.score is not None
    assert series.points[-1].value == team.score.total


def test_team_value_is_the_mean_of_its_members():
    """Ana +10% e Bia +50% fazem a equipe 1 valer +30%; a equipe 2, só Caio, vale +25%."""
    report = build_overview(
        [
            member("Ana", 1, "11000"),
            member("Bia", 1, "15000"),
            member("Caio", 2, "12500"),
        ],
        VictoryCriterion.RETURN,
        in_teams=True,
    )

    assert [(t.position, t.team) for t in report.teams] == [(1, 1), (2, 2)]
    first = teams_of(report)[1]
    assert first.criterion_value == Decimal("0.3")
    assert first.return_percent == Decimal("0.3")
    assert first.members == 2
    assert first.measured_members == 2
    assert first.leader_gap == Decimal("0")
    assert teams_of(report)[2].leader_gap == Decimal("0.05")


def test_bigger_team_does_not_win_by_summing():
    """Três com +10% perdem de um com +50%: a média, e não a soma, decide."""
    report = build_overview(
        [
            member("Ana", 1, "11000"),
            member("Bia", 1, "11000"),
            member("Caio", 1, "11000"),
            member("Duda", 2, "15000"),
        ],
        VictoryCriterion.RETURN,
        in_teams=True,
    )

    assert [t.team for t in report.teams] == [2, 1]


def test_tie_goes_to_the_higher_mean_networth():
    """Mesmo retorno de 10%: a equipe com mais patrimônio médio vence o desempate."""
    report = build_overview(
        [
            member("Ana", 1, "11000"),
            member("Bia", 2, "110000", starting_cash="100000"),
        ],
        VictoryCriterion.RETURN,
        in_teams=True,
    )

    assert [t.team for t in report.teams] == [2, 1]


def test_member_without_a_value_stays_out_of_the_mean(indicators: SetIndicator):
    """Sem 63 pregões não há nota: a equipe fica com a nota de quem tem ('1 de 2')."""
    scored = member("Ana", 1, days=["10000"] * (MIN_SCORE_DAYS + 1))
    unscored = member("Bia", 1, days=["10000", "12000"])

    report = build_overview([scored, unscored], in_teams=True)

    team = teams_of(report)[1]
    alone = next(p for p in report.players if p.player_nickname == "Ana")
    assert team.members == 2
    assert team.measured_members == 1
    assert team.criterion_value == alone.criterion_value
    assert team.score is not None
    assert team.score.total == alone.criterion_value


def test_team_without_any_value_ranks_after_the_ones_with_value(
    indicators: SetIndicator,
):
    scored = member("Ana", 1, days=["10000"] * (MIN_SCORE_DAYS + 1))
    unscored = member("Bia", 2, days=["10000", "12000"])

    report = build_overview([unscored, scored], in_teams=True)

    assert [t.team for t in report.teams] == [1, 2]
    assert teams_of(report)[2].criterion_value is None
    assert teams_of(report)[2].score is None


def test_member_contribution_is_the_distance_to_the_team_mean():
    """Média +30%: Bia (+50%) puxa para cima +20 pontos, Ana (+10%) para baixo."""
    report = build_overview(
        [member("Ana", 1, "11000"), member("Bia", 1, "15000")],
        VictoryCriterion.RETURN,
        in_teams=True,
    )

    contributions = {p.player_nickname: p.team_contribution for p in report.players}
    assert contributions == {"Bia": Decimal("0.2"), "Ana": Decimal("-0.2")}
    puller = teams_of(report)[1].top_puller
    assert puller is not None
    assert puller.player_nickname == "Bia"
    assert puller.contribution == Decimal("0.2")
    assert puller.axis is None


def test_team_of_one_has_no_puller():
    report = build_overview(
        [member("Ana", 1, "11000"), member("Bia", 2, "12000")],
        VictoryCriterion.RETURN,
        in_teams=True,
    )

    assert all(t.top_puller is None for t in report.teams)


def test_every_member_below_the_mean_leaves_no_puller():
    """Todos iguais: ninguém passa da média."""
    report = build_overview(
        [member("Ana", 1, "11000"), member("Bia", 1, "11000")],
        VictoryCriterion.RETURN,
        in_teams=True,
    )

    assert teams_of(report)[1].top_puller is None


def test_individual_game_has_no_teams():
    report = build_overview(
        [member("Ana", None, "11000"), member("Bia", None, "15000")]
    )

    assert report.teams == []
    assert all(p.team_contribution is None for p in report.players)
    assert report.team_naming is TeamNaming.COLOR


def test_mean_ignores_missing_values():
    assert mean([Decimal(10), None, Decimal(20)]) == Decimal(15)
    assert mean([None, None]) is None


def test_mean_series_averages_the_members_present_each_day():
    """Quem entrou depois só conta a partir do dia em que tem ponto."""
    first = date(2020, 1, 1)
    second = date(2020, 1, 2)
    series = mean_series(
        [
            [
                SeriesPointDTO(date=first, value=Decimal(2)),
                SeriesPointDTO(date=second, value=Decimal(4)),
            ],
            [SeriesPointDTO(date=second, value=Decimal(8))],
        ]
    )

    assert [(p.date, p.value) for p in series] == [
        (first, Decimal(2)),
        (second, Decimal(6)),
    ]


def returns_row(
    nickname: str, team: int | None, values: list[int], above: int
) -> PlayerReturnsDTO:
    day = date(2020, 1, 1)
    points = [
        SeriesPointDTO(date=day + timedelta(days=i), value=Decimal(v))
        for i, v in enumerate(values)
    ]
    return PlayerReturnsDTO(
        player_nickname=nickname,
        color="chart-1",
        simulation_id=1,
        simulation_name="A",
        team=team,
        is_bot=False,
        networth=points,
        cumulative_return=points,
        capital_provided=Decimal(10000),
        annual_return=None,
        months_above_cdi=above,
        positive_months=above,
        months=12,
        monthly_returns=[],
        credit_cost=None,
    )


def test_team_returns_average_curves_and_month_counts():
    """7 e 8 meses acima do CDI viram 7,5 na equipe; a curva é a média dia a dia."""
    teams = team_returns(
        [
            returns_row("Ana", 1, [10, 20], 7),
            returns_row("Bia", 1, [30, 40], 8),
            returns_row("Caio", None, [1, 1], 1),
        ]
    )

    assert len(teams) == 1
    assert teams[0].months_above_cdi == Decimal("7.5")
    assert [p.value for p in teams[0].cumulative_return] == [Decimal(20), Decimal(30)]
    assert teams[0].annual_return is None


def operations_row(
    nickname: str, team: int, volume: str, tax: str, buys: int, turnover: str | None
) -> PlayerOperationsDTO:
    return PlayerOperationsDTO(
        player_nickname=nickname,
        color="chart-1",
        simulation_id=1,
        simulation_name="A",
        team=team,
        is_bot=False,
        buy_trades=buys,
        sell_trades=1,
        traded_volume=Decimal(volume),
        turnover=Decimal(turnover) if turnover else None,
        turnover_style=None,
        income_tax_paid=Decimal(tax),
        impact_cost=None,
        monthly_volume=[
            MonthlyVolumeDTO(
                month=date(2020, 1, 1),
                bought=Decimal(volume),
                sold=Decimal(0),
                buy_count=buys,
                sell_count=0,
            )
        ],
    )


def test_team_operations_sum_totals_and_average_turnover():
    """Volume, IR e negócios são totais da equipe; o giro é desempenho, então é média."""
    teams = team_operations(
        [
            operations_row("Ana", 1, "1000", "10", 2, "1.0"),
            operations_row("Bia", 1, "3000", "30", 4, None),
        ]
    )

    team = teams[0]
    assert team.traded_volume == Decimal(4000)
    assert team.income_tax_paid == Decimal(40)
    assert team.buy_trades == 6
    assert team.sell_trades == 2
    assert team.turnover == Decimal("1.0")
    assert team.impact_cost is None
    assert team.monthly_volume[0].bought == Decimal(4000)
    assert team.monthly_volume[0].buy_count == 6


def test_report_says_it_is_in_teams_even_without_players():
    """Antes do primeiro pregão não há equipes para listar, mas a tela precisa saber o modo."""
    report = build_overview([], in_teams=True)

    assert report.teams == []
    assert report.player_grouping is PlayerGrouping.TEAMS
    assert build_overview([]).player_grouping is PlayerGrouping.INDIVIDUAL
