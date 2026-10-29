"""
O painel do orçamento: a conta do mês, os impostos, a dívida com a projeção até o fim
do mandato e o efeito de cada medida na conta do governo.
"""

from collections.abc import Iterable
from datetime import date, timedelta
from decimal import Decimal

from backend.core.dto.budget import (
    BudgetAmountsDTO,
    BudgetDTO,
    BudgetEffectDTO,
    BudgetMonthDTO,
    BudgetTaxDTO,
    InitialAccountDTO,
    InitialAccountOptionDTO,
    PremiumPointDTO,
    QueueBudgetDTO,
)
from backend.core.enum import InitialAccount, MeasureKind
from backend.features.government import budget as budget_rules
from backend.features.government import measures as rules
from backend.features.government import spending
from backend.features.government.budget import BudgetCourse, BudgetMonth, TaxRow
from backend.features.government.spending import SpendingTimeline
from backend.features.government.state import Measure
from backend.features.tax_policy import TaxPolicy

ZERO = Decimal(0)
# Sem mandato em curso, a projeção olha quatro anos adiante
FALLBACK_PROJECTION = timedelta(days=4 * 365)

# O imposto que cada medida geral atinge
ROW_OF_KIND: dict[MeasureKind, str] = {
    MeasureKind.STOCK_PROFIT_RATE: "STOCK_PROFIT",
    MeasureKind.STOCK_EXEMPTION: "STOCK_PROFIT",
    MeasureKind.DAY_TRADE_RATE: "DAY_TRADE",
    MeasureKind.FIXED_INCOME_TABLE: "FIXED_INCOME",
    MeasureKind.LCI_LCA_RATE: "LCI_LCA",
}


def month_dto(month: BudgetMonth) -> BudgetMonthDTO:
    return BudgetMonthDTO(
        month_end=month.month_end,
        revenue=month.revenue,
        spending=month.spending,
        primary=month.primary,
        interest=month.interest,
        result=month.result,
        debt=month.debt,
        premium=month.premium,
        gdp=month.gdp,
        closed=month.closed,
    )


def tax_dto(row: TaxRow) -> BudgetTaxDTO:
    return BudgetTaxDTO(
        key=row.key,
        name=row.name,
        rate=row.rate,
        default_rate=row.default_rate,
        revenue=row.revenue,
        difference=row.difference,
        top_rate=row.top_rate,
        floor_rate=row.floor_rate,
        default_top_rate=row.default_top_rate,
        default_floor_rate=row.default_floor_rate,
    )


def projection_end(term_end: date | None, today: date) -> date:
    return term_end if term_end is not None else today + FALLBACK_PROJECTION


def build_budget(
    course: BudgetCourse, policy: TaxPolicy, today: date, term_end: date | None
) -> BudgetDTO:
    month = course.latest(today)
    end = projection_end(term_end, today)
    return BudgetDTO(
        today=today,
        month=month_dto(month),
        amounts=BudgetAmountsDTO(
            revenue=month.monthly(month.revenue),
            spending=month.monthly(month.spending),
            primary=month.monthly(month.primary),
            interest=month.monthly(month.interest),
            result=month.monthly(month.result),
            debt=month.debt * month.gdp,
        ),
        taxes=[tax_dto(row) for row in budget_rules.tax_rows(policy)],
        fixed_revenue=course.fixed_revenue(),
        total_revenue=course.fixed_revenue() + budget_rules.game_revenue(policy),
        total_difference=(
            budget_rules.game_revenue(policy) - budget_rules.DEFAULT_GAME_REVENUE
        ),
        history=[month_dto(m) for m in course.months_until(today)],
        projection=[month_dto(m) for m in course.project(today, end)],
        projection_end=end,
        premium_curve=[
            PremiumPointDTO(debt=debt, premium=premium)
            for debt, premium in budget_rules.premium_curve()
        ],
        premium_floor=budget_rules.PREMIUM_FLOOR,
    )


def initial_account_option(
    start: date, kind: InitialAccount
) -> InitialAccountOptionDTO:
    account = budget_rules.initial_account(start, kind)
    return InitialAccountOptionDTO(
        debt=account.debt,
        primary=account.primary,
        primary_amount=account.primary * account.gdp,
        premium=budget_rules.premium(account.debt),
    )


def build_initial_account(start: date) -> InitialAccountDTO:
    return InitialAccountDTO(
        year=start.year,
        playable=initial_account_option(start, InitialAccount.PLAYABLE),
        realistic=initial_account_option(start, InitialAccount.REALISTIC),
    )


def current_result(course: BudgetCourse, today: date) -> Decimal:
    """O resultado por ano em vigor: o do último fechamento, ou o do primeiro mês projetado antes dele."""
    month = course.latest(today)
    if month.closed:
        return month.result
    following = course.project(today, today + timedelta(days=31))
    return following[0].result if following else month.result


def _row_of(rows: Iterable[TaxRow], measure: Measure) -> TaxRow | None:
    if measure.kind.is_spending:
        return None
    if measure.kind.is_sector:
        name = f"{measure.segment or measure.sector} · setor"
        return next((r for r in rows if r.key == "SECTOR" and r.name == name), None)
    key = ROW_OF_KIND[measure.kind]
    return next((r for r in rows if r.key == key), None)


def spending_change(measure: Measure) -> Decimal:
    """Quanto a medida muda o gasto no primeiro ano, em fração do PIB por ano; zero nos impostos."""
    if not measure.kind.is_spending:
        return ZERO
    return spending.cost_change(measure.kind, measure.value, measure.before)


def result_change(policy_before: TaxPolicy, measure: Measure) -> Decimal:
    """Quanto a medida muda o resultado do governo: a receita a mais menos o gasto a mais."""
    return budget_rules.measure_effect(policy_before, measure) - spending_change(
        measure
    )


def measure_budget(
    course: BudgetCourse,
    policy_before: TaxPolicy,
    timeline: SpendingTimeline,
    measure: Measure,
    today: date,
    effective: date,
    term_end: date | None,
) -> BudgetEffectDTO:
    """O efeito da medida na conta, se ela passar e valer em `effective`."""
    change = budget_rules.measure_effect(policy_before, measure)
    outlay = spending_change(measure)
    before_row = _row_of(budget_rules.tax_rows(policy_before), measure)
    after_row = _row_of(
        budget_rules.tax_rows(rules.apply_measure(policy_before, measure)), measure
    )
    affected = after_row or before_row
    end = projection_end(term_end, today)
    without = course.project(today, end)
    with_measure = course.project(
        today,
        end,
        change,
        effective,
        timeline.with_measure(measure, effective).spending_on
        if measure.kind.is_spending
        else None,
    )
    latest_debt = course.latest(today).debt
    result_now = current_result(course, today)
    gdp = course.latest(today).gdp
    return BudgetEffectDTO(
        revenue_change=change,
        revenue_change_amount=change * gdp,
        spending_change=outlay,
        spending_change_amount=outlay * gdp,
        spending_before=timeline.spending_on(effective),
        spending_after=timeline.spending_on(effective) + outlay,
        tax_name=affected.name if affected else "",
        rate_before=before_row.rate if before_row else None,
        rate_after=after_row.rate if after_row else None,
        tax_revenue_before=before_row.revenue if before_row else ZERO,
        tax_revenue_after=after_row.revenue if after_row else ZERO,
        result_before=result_now,
        result_after=result_now + change - outlay,
        debt_end=end,
        debt_before=without[-1].debt if without else latest_debt,
        debt_after=with_measure[-1].debt if with_measure else latest_debt,
    )


def queue_budget(
    course: BudgetCourse, policy: TaxPolicy, queued: Iterable[Measure], today: date
) -> QueueBudgetDTO:
    """A fila inteira aplicada em ordem sobre a política de hoje: a receita a mais menos o gasto a mais."""
    final = policy
    outlay = ZERO
    for measure in sorted(queued, key=lambda m: m.id):
        final = rules.apply_measure(final, measure)
        outlay += spending_change(measure)
    total = (
        budget_rules.game_revenue(final) - budget_rules.game_revenue(policy) - outlay
    )
    now = current_result(course, today)
    return QueueBudgetDTO(total=total, result_now=now, result_if_passes=now + total)
