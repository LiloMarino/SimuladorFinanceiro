"""Regras puras do governo: política de impostos, régua, aprovação e calendário do Congresso."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.sector import StockSegmentDTO
from backend.core.enum import (
    ApprovalFactorKind,
    AssetClass,
    EquityEventType,
    FixedIncomeType,
    MeasureKind,
    MeasureStatus,
    VoterGroup,
)
from backend.core.indicators import inflation_target
from backend.features.fixed_income.accrual import income_tax_rate
from backend.features.government import approval as approval_rules
from backend.features.government import congress, voters
from backend.features.government import measures as rules
from backend.features.government.state import Measure, Term
from backend.features.tax_policy import DEFAULT_TAX_POLICY, LossPool, TaxPolicy
from backend.features.variable_income.income_tax import assess
from tests.fakes import USER_ID

DAY = date(2022, 1, 31)
CLASSES = {"TAEE11": AssetClass.STOCK, "ITUB4": AssetClass.STOCK}
SECTORS = {
    "TAEE11": StockSegmentDTO(sector="Energia", segment="Transmissão"),
    "ITUB4": StockSegmentDTO(sector="Bancos", segment="Bancos"),
}
TERM = Term(
    party_id=1,
    president_id=1,
    vice_id=None,
    start=date(2022, 1, 3),
    consecutive=1,
)


def measure(
    kind: MeasureKind,
    value: str | None = None,
    before: str | None = None,
    *,
    sector: str | None = None,
    segment: str | None = None,
    effective: date | None = DAY,
    status: MeasureStatus = MeasureStatus.APPROVED,
    id: int = 1,
) -> Measure:
    return Measure(
        id=id,
        kind=kind,
        value=None if value is None else Decimal(value),
        before=None if before is None else Decimal(before),
        sector=sector,
        segment=segment,
        proposer_id=1,
        term_start=TERM.start,
        proposed=date(2022, 1, 5),
        status=status,
        effective=effective,
    )


def trade(kind: EquityEventType, ticker: str, day: date, price: str) -> EquityEventDTO:
    return EquityEventDTO(
        simulation_id=1,
        user_id=USER_ID,
        event_date=day,
        ticker=ticker,
        event_type=kind,
        quantity=Decimal(1000),
        price=Decimal(price),
    )


def march_tax(policy: TaxPolicy, ticker: str) -> Decimal:
    """O IR de março de quem comprou a 25 e vendeu a 30 (R$ 5.000 de lucro, R$ 30.000 vendidos)."""
    events = [
        trade(EquityEventType.BUY, ticker, date(2022, 2, 10), "25"),
        trade(EquityEventType.SELL, ticker, date(2022, 3, 10), "30"),
    ]
    months = assess(events, CLASSES, date(2022, 3, 31), lambda _day: policy, SECTORS)
    return next(m.tax for m in months if (m.year, m.month) == (2022, 3))


# Política de impostos


def test_default_policy_matches_the_law():
    assert march_tax(DEFAULT_TAX_POLICY, "TAEE11") == Decimal("750.00")
    assert income_tax_rate(FixedIncomeType.CDB, 100) == Decimal("0.225")
    assert income_tax_rate(FixedIncomeType.CDB, 800) == Decimal("0.15")
    assert income_tax_rate(FixedIncomeType.LCI, 100) == 0


def test_stock_rate_measure_changes_the_tax():
    policy = rules.apply_measure(
        DEFAULT_TAX_POLICY,
        measure(MeasureKind.STOCK_PROFIT_RATE, "0.20", "0.15"),
    )

    assert march_tax(policy, "TAEE11") == Decimal("1000.00")


def test_exempt_sector_leaves_the_tax_calculation():
    policy = rules.apply_measure(
        DEFAULT_TAX_POLICY,
        measure(MeasureKind.SECTOR_EXEMPT, sector="Energia"),
    )

    assert march_tax(policy, "TAEE11") == 0
    assert march_tax(policy, "ITUB4") == Decimal("750.00")


def test_taxed_sector_adds_points_to_the_rate_of_its_gain_only():
    policy = rules.apply_measure(
        DEFAULT_TAX_POLICY,
        measure(MeasureKind.SECTOR_TAX, "0.05", sector="Bancos"),
    )

    assert march_tax(policy, "ITUB4") == Decimal("1000.00")
    assert march_tax(policy, "TAEE11") == Decimal("750.00")


def test_segment_rule_beats_the_sector_rule():
    policy = rules.apply_measure(
        DEFAULT_TAX_POLICY, measure(MeasureKind.SECTOR_EXEMPT, sector="Energia")
    )
    policy = rules.apply_measure(
        policy,
        measure(
            MeasureKind.SECTOR_TAX, "0.05", sector="Energia", segment="Transmissão"
        ),
    )

    assert march_tax(policy, "TAEE11") == Decimal("1000.00")


def test_single_table_measure_replaces_the_regressive_brackets():
    policy = rules.apply_measure(
        DEFAULT_TAX_POLICY, measure(MeasureKind.FIXED_INCOME_TABLE, "0.15", "0.225")
    )

    assert income_tax_rate(FixedIncomeType.CDB, 100, policy) == Decimal("0.15")
    assert policy.fixed_income_top_rate == Decimal("0.15")


def test_lci_lca_measure_ends_the_exemption():
    policy = rules.apply_measure(
        DEFAULT_TAX_POLICY, measure(MeasureKind.LCI_LCA_RATE, "0.10", "0")
    )

    assert income_tax_rate(FixedIncomeType.LCI, 100, policy) == Decimal("0.10")


def test_policy_timeline_switches_on_the_effective_day():
    timeline = rules.PolicyTimeline(
        [
            measure(
                MeasureKind.STOCK_PROFIT_RATE,
                "0.20",
                "0.15",
                effective=date(2022, 5, 1),
            ),
            measure(
                MeasureKind.STOCK_PROFIT_RATE,
                "0.25",
                "0.20",
                effective=date(2022, 8, 1),
                id=2,
            ),
            measure(
                MeasureKind.DAY_TRADE_RATE,
                "0.30",
                "0.20",
                effective=date(2022, 9, 1),
                status=MeasureStatus.REJECTED,
                id=3,
            ),
        ]
    )

    common = LossPool.COMMON
    assert timeline.on(date(2022, 4, 30)).rates[common] == Decimal("0.15")
    assert timeline.on(date(2022, 5, 1)).rates[common] == Decimal("0.20")
    assert timeline.on(date(2022, 9, 1)).rates[common] == Decimal("0.25")
    assert timeline.on(date(2022, 9, 1)).rates[LossPool.DAY_TRADE] == Decimal("0.20")


# Aprovação por grupo


def market(
    inflation: str = "0.04",
    stocks: str | None = "0.05",
    target: str = "0.04",
    selic: str = "0.10",
    unemployment: str = "0.09",
    premium: str = "0",
):
    """Por padrão o mercado no ponto neutro: inflação na meta, SELIC em 10%, bolsa em 5%, desemprego em 9% e prêmio zero."""
    return approval_rules.Market(
        inflation=Decimal(inflation),
        selic=Decimal(selic),
        stocks=None if stocks is None else Decimal(stocks),
        target=Decimal(target),
        unemployment=Decimal(unemployment),
        premium=Decimal(premium),
    )


def points(result: approval_rules.GroupTarget) -> dict[ApprovalFactorKind, Decimal]:
    return {f.kind: f.points for f in result.factors}


def test_target_starts_at_the_neutral_point_and_adds_what_each_group_reads():
    # Aposentados: 4 pontos por ponto de inflação abaixo da meta somada a 1,5
    result = approval_rules.group_target(
        VoterGroup.RETIREES, market("0.03", "0.15"), [], DAY
    )

    assert points(result)[ApprovalFactorKind.BASE] == 50
    assert points(result)[ApprovalFactorKind.INFLATION] == Decimal("10")
    assert points(result)[ApprovalFactorKind.SELIC] == 0
    assert points(result)[ApprovalFactorKind.STOCKS] == 1
    assert result.target == 61


def test_a_good_and_a_bad_result_move_the_target_by_the_same_amount():
    # O ponto neutro da inflação é a meta mais 1,5: 4% fica 1,5 abaixo dele e 7%, 1,5 acima
    good = approval_rules.inflation_factor(VoterGroup.RETIREES, market("0.04"))
    bad = approval_rules.inflation_factor(VoterGroup.RETIREES, market("0.07"))

    assert (good.points, bad.points) == (6, -6)


def test_each_result_is_capped_in_both_directions():
    retirees = VoterGroup.RETIREES
    investors = VoterGroup.INVESTORS

    assert approval_rules.inflation_factor(retirees, market("0.30")).points == -20
    assert approval_rules.inflation_factor(retirees, market("0.00")).points == 20
    assert approval_rules.selic_factor(retirees, market(selic="0.30")).points == 9
    assert approval_rules.selic_factor(retirees, market(selic="0.00")).points == -9
    rise = approval_rules.stocks_factor(investors, market(stocks="0.90"))
    fall = approval_rules.stocks_factor(investors, market(stocks="-0.80"))
    assert rise is not None and rise.points == 24
    assert fall is not None and fall.points == -24
    assert approval_rules.stocks_factor(investors, market(stocks=None)) is None


def test_unemployment_above_the_neutral_weighs_most_on_formal_workers_and_welfare():
    high = market(unemployment="0.12")

    formal = approval_rules.unemployment_factor(VoterGroup.FORMAL_WORKERS, high)
    welfare = approval_rules.unemployment_factor(VoterGroup.WELFARE, high)
    retirees = approval_rules.unemployment_factor(VoterGroup.RETIREES, high)

    assert formal.points == welfare.points == -3
    assert retirees.points == Decimal("-0.75")
    assert formal.kind is ApprovalFactorKind.UNEMPLOYMENT


def test_unemployment_below_the_neutral_pleases_and_is_capped():
    low = approval_rules.unemployment_factor(
        VoterGroup.FORMAL_WORKERS, market(unemployment="0.05")
    )
    extreme = approval_rules.unemployment_factor(
        VoterGroup.FORMAL_WORKERS, market(unemployment="0.18")
    )

    assert low.points == 4
    assert extreme.points == -4


def test_risk_premium_irritates_investors_and_spares_public_servants():
    premium = market(premium="0.019")

    investors = approval_rules.premium_factor(VoterGroup.INVESTORS, premium)
    servants = approval_rules.premium_factor(VoterGroup.PUBLIC_SERVANTS, premium)

    assert investors.points == Decimal("-3.8")
    assert servants.points == 0
    assert investors.kind is ApprovalFactorKind.RISK_PREMIUM


def test_risk_premium_has_no_effect_at_zero_and_is_capped_at_six_points():
    none = approval_rules.premium_factor(VoterGroup.INVESTORS, market())
    huge = approval_rules.premium_factor(VoterGroup.INVESTORS, market(premium="0.20"))

    assert none.points == 0
    assert huge.points == -12


def test_the_same_result_pleases_one_group_and_irritates_another():
    high_rate = market(selic="0.16")

    retirees = approval_rules.selic_factor(VoterGroup.RETIREES, high_rate)
    entrepreneurs = approval_rules.selic_factor(VoterGroup.ENTREPRENEURS, high_rate)

    assert retirees.points == 9
    assert entrepreneurs.points == -12


def test_target_never_leaves_zero_to_one_hundred():
    pleasing = [
        measure(MeasureKind.DAY_TRADE_RATE, "0.125", "0.225", id=i)
        for i in range(1, 12)
    ]
    irritating = [
        measure(MeasureKind.DAY_TRADE_RATE, "0.325", "0.225", id=i)
        for i in range(1, 12)
    ]

    high = approval_rules.group_target(VoterGroup.INVESTORS, market(), pleasing, DAY)
    low = approval_rules.group_target(VoterGroup.INVESTORS, market(), irritating, DAY)

    assert (low.target, high.target) == (0, 100)


def test_a_measure_pleases_and_irritates_groups_by_their_positions():
    # Cortar 10 pontos do day trade: 1 passo, que avança Mercado livre e recua Justiça social
    cut = measure(MeasureKind.DAY_TRADE_RATE, "0.125", "0.225")

    assert approval_rules.measure_reaction(VoterGroup.INVESTORS, cut) == 9
    assert approval_rules.measure_reaction(VoterGroup.WELFARE, cut) == Decimal("-7.8")


def test_a_measure_weighs_in_full_when_it_takes_effect_and_halves_every_six_months():
    cut = measure(MeasureKind.DAY_TRADE_RATE, "0.125", "0.225", effective=DAY)

    def target(today: date) -> Decimal:
        result = approval_rules.group_target(
            VoterGroup.INVESTORS, market(), [cut], today
        )
        return points(result)[ApprovalFactorKind.MEASURE]

    assert target(DAY) == 9
    assert float(target(date(2022, 8, 1))) == pytest.approx(4.5, abs=0.05)
    assert float(target(date(2023, 2, 1))) == pytest.approx(2.25, abs=0.05)


def test_a_measure_not_yet_in_force_does_not_weigh():
    cut = measure(MeasureKind.DAY_TRADE_RATE, "0.125", "0.225", effective=DAY)

    result = approval_rules.group_target(
        VoterGroup.INVESTORS, market(), [cut], date(2022, 1, 1)
    )

    assert ApprovalFactorKind.MEASURE not in points(result)


def test_measure_impact_is_the_effect_on_the_target_weighted_by_group_size():
    cut = measure(MeasureKind.DAY_TRADE_RATE, "0.125", "0.225")
    weighted = sum(
        (
            voters.WEIGHTS[g] * approval_rules.measure_reaction(g, cut)
            for g in VoterGroup
        ),
        Decimal(0),
    )

    assert approval_rules.measure_impact(cut) == approval_rules.rounded(weighted)


def test_satisfaction_walks_a_third_of_the_way_to_the_target_each_month():
    value = Decimal(40)
    path = []
    for _ in range(3):
        value = approval_rules.next_satisfaction(value, Decimal(70))
        path.append(round(value))

    assert path == [50, 57, 61]


def test_overall_approval_averages_the_groups_by_their_weight():
    flat = dict.fromkeys(VoterGroup, Decimal(60))
    assert approval_rules.overall(flat) == 60
    only_investors = {g: Decimal(0) for g in VoterGroup} | {
        VoterGroup.INVESTORS: Decimal(100)
    }
    assert approval_rules.overall(only_investors) == 8


def test_the_floor_only_counts_after_the_first_twelve_months():
    assert approval_rules.in_grace(TERM, date(2022, 1, 1))
    assert approval_rules.in_grace(TERM, date(2022, 12, 1))
    assert not approval_rules.in_grace(TERM, date(2023, 1, 1))
    assert approval_rules.grace_end(TERM) == date(2022, 12, 31)
    mid_year = Term(
        party_id=1,
        president_id=2,
        vice_id=None,
        start=date(2022, 11, 28),
        consecutive=1,
        succession=True,
    )
    assert approval_rules.grace_end(mid_year) == date(2023, 10, 31)


def test_each_government_counts_only_its_own_measures():
    other = Term(
        party_id=1,
        president_id=2,
        vice_id=None,
        start=date(2022, 4, 29),
        consecutive=1,
        succession=True,
    )
    tax = measure(MeasureKind.DAY_TRADE_RATE, "0.225", "0.20")
    satisfaction = dict.fromkeys(VoterGroup, Decimal(50))

    result = approval_rules.assess(
        other, satisfaction, [tax], market(), date(2022, 5, 2)
    )

    for target in result.targets.values():
        assert ApprovalFactorKind.MEASURE not in points(target)


def test_upcoming_lists_approved_measures_that_will_weigh_when_they_take_effect():
    waiting = measure(
        MeasureKind.SECTOR_TAX,
        "0.05",
        sector="Bancos",
        effective=date(2022, 5, 29),
        id=3,
    )
    satisfaction = dict.fromkeys(VoterGroup, Decimal(50))

    result = approval_rules.assess(TERM, satisfaction, [waiting], market(), DAY)

    assert [m.id for m in result.upcoming] == [3]
    assert result.value == 50


def test_inflation_target_follows_the_official_year_and_falls_back_to_three():
    assert inflation_target(date(2021, 6, 1)) == Decimal("0.0375")
    assert inflation_target(date(2031, 6, 1)) == Decimal("0.03")


# Calendário do Congresso


@pytest.mark.parametrize(
    ("day", "vote"),
    [
        (date(2022, 1, 31), date(2022, 1, 31)),
        (date(2022, 4, 15), date(2022, 4, 29)),
        (date(2022, 4, 30), date(2022, 5, 31)),
        (date(2022, 12, 31), date(2023, 1, 31)),
    ],
)
def test_next_vote_is_the_last_business_day_of_the_month(day: date, vote: date):
    assert congress.next_vote_date(day) == vote


def test_vote_draw_is_deterministic_and_follows_the_approval():
    draws = [congress.passes(7, DAY, measure_id, 56) for measure_id in range(1, 2001)]

    assert draws == [congress.passes(7, DAY, i, 56) for i in range(1, 2001)]
    assert 0.5 < sum(draws) / len(draws) < 0.62
    assert not any(congress.passes(7, DAY, i, 0) for i in range(1, 200))
    assert all(congress.passes(7, DAY, i, 100) for i in range(1, 200))


def test_titles_read_in_portuguese():
    assert (
        rules.title(measure(MeasureKind.DAY_TRADE_RATE, "0.225", "0.20"))
        == "Ações: IR do day trade em 22,5%"
    )
    assert (
        rules.title(measure(MeasureKind.STOCK_EXEMPTION, "0", "20000"))
        == "Isenção de vendas de ações acaba"
    )
    assert (
        rules.title(measure(MeasureKind.SECTOR_TAX, "0.05", sector="Bancos"))
        == "Bancos: +5 pontos no IR das vendas com lucro"
    )
