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
)
from backend.features.fixed_income.accrual import income_tax_rate
from backend.features.government import approval as approval_rules
from backend.features.government import congress
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
    promise=3,
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


# Régua e peso na aprovação


@pytest.mark.parametrize(
    ("built", "band", "impact"),
    [
        (measure(MeasureKind.STOCK_PROFIT_RATE, "0.05", "0.15"), 1, 1),
        (measure(MeasureKind.STOCK_PROFIT_RATE, "0.15", "0.20"), 1, 1),
        (measure(MeasureKind.STOCK_PROFIT_RATE, "0", "0.15"), 1, 2),
        (measure(MeasureKind.SECTOR_EXEMPT, sector="Energia"), 2, 2),
        (measure(MeasureKind.SECTOR_TAX, "0.05", sector="Bancos"), 4, -3),
        (measure(MeasureKind.DAY_TRADE_RATE, "0.225", "0.20"), 5, -3),
        (measure(MeasureKind.DAY_TRADE_RATE, "0.50", "0.20"), 5, -5),
        (measure(MeasureKind.STOCK_EXEMPTION, "0", "20000"), 5, -3),
        (measure(MeasureKind.STOCK_EXEMPTION, "30000", "20000"), 1, 2),
    ],
)
def test_ruler_band_and_approval_impact(built: Measure, band: int, impact: int):
    assert rules.ruler_band(built) == band
    assert rules.approval_impact(built) == impact


def test_new_tax_effect_fades_in_six_months_and_a_cut_does_not():
    tax = measure(MeasureKind.DAY_TRADE_RATE, "0.225", "0.20")
    cut = measure(MeasureKind.SECTOR_EXEMPT, sector="Energia")

    assert rules.current_effect(tax, DAY) == -3
    assert rules.current_effect(tax, date(2022, 5, 1)) == -2
    assert rules.current_effect(tax, date(2022, 7, 30)) == 0
    assert rules.current_effect(cut, date(2023, 1, 1)) == 2


# Aprovação


def market(inflation: str, stocks: str | None, target: str = "0.04"):
    return approval_rules.Market(
        inflation=Decimal(inflation),
        stocks=None if stocks is None else Decimal(stocks),
        target=Decimal(target),
    )


def test_approval_starts_at_fifty_and_adds_the_factors_of_the_card():
    waiting = measure(
        MeasureKind.SECTOR_TAX,
        "0.05",
        sector="Bancos",
        effective=date(2022, 5, 29),
        id=3,
    )
    cut = measure(MeasureKind.SECTOR_EXEMPT, sector="Energia", effective=DAY)
    tax = measure(MeasureKind.DAY_TRADE_RATE, "0.225", "0.20", effective=DAY, id=2)

    result = approval_rules.assess(
        TERM, [cut, tax, waiting], market("0.038", "0.18"), DAY
    )

    points = {f.kind: f.points for f in result.factors}
    assert points[ApprovalFactorKind.BASE] == 50
    # Inflação dentro da meta soma 4; bolsa +18% soma 1 a cada 5%
    assert points[ApprovalFactorKind.INFLATION] == 4
    assert points[ApprovalFactorKind.STOCKS] == 3
    assert points[ApprovalFactorKind.TAX_CUT] == 2
    assert points[ApprovalFactorKind.NEW_TAX] == -3
    # Marca (2 + 5 + 4) / 3 = 3,67 contra a promessa 3: 0,67 faixa x 3 = -2
    assert points[ApprovalFactorKind.PROMISE] == -2
    assert result.value == 54
    assert [m.id for m in result.upcoming] == [3]


def test_inflation_above_target_costs_three_points_per_point():
    result = approval_rules.inflation_factor(market("0.07", None, "0.04"))

    assert result.points == 4 - 9


def test_stocks_factor_is_capped_at_six_points_each_way():
    rise = approval_rules.stocks_factor(market("0.04", "0.80"))
    fall = approval_rules.stocks_factor(market("0.04", "-0.60"))

    assert rise is not None and rise.points == 6
    assert fall is not None and fall.points == -6
    assert approval_rules.stocks_factor(market("0.04", "0.03")) is None


def test_approval_never_leaves_zero_to_one_hundred():
    low = approval_rules.assess(TERM, [], market("0.30", "-0.9"), DAY)
    high = approval_rules.assess(TERM, [], market("0.01", "0.9"), DAY)

    assert low.value == 0
    assert high.value == 60


def test_each_government_counts_only_its_own_measures():
    other = Term(
        party_id=1,
        president_id=2,
        vice_id=None,
        start=date(2022, 4, 29),
        consecutive=1,
        promise=3,
        succession=True,
    )
    tax = measure(MeasureKind.DAY_TRADE_RATE, "0.225", "0.20")

    result = approval_rules.assess(other, [tax], market("0.03", None), date(2022, 5, 2))

    assert {f.kind for f in result.factors} == {
        ApprovalFactorKind.BASE,
        ApprovalFactorKind.INFLATION,
    }


def test_inflation_target_follows_the_official_year_and_falls_back_to_three():
    assert approval_rules.inflation_target(date(2021, 6, 1)) == Decimal("0.0375")
    assert approval_rules.inflation_target(date(2031, 6, 1)) == Decimal("0.03")


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
