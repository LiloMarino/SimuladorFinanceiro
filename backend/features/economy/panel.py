"""
O painel da economia: a SELIC, o IPCA e o juro real desde o primeiro dia da
partida, só com o que o jogador já conhece em `today`.
"""

from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal

from backend.core import repository
from backend.core.dto.economy import (
    CopomChangeDTO,
    DebtSummaryDTO,
    EconomyPanelDTO,
    EconomyPointDTO,
    GrowthPartsDTO,
)
from backend.core.enum import IndicatorSeries
from backend.core.indicators import (
    annual_index_rate,
    annualize_daily,
    inflation_target,
    inflation_tolerance,
    last_known_value,
)
from backend.features.economy.growth import (
    NEUTRAL_REAL_RATE,
    MacroCourse,
    growth_aim,
)
from backend.features.government.budget import BudgetCourse

# Degrau mínimo para contar como mudança da SELIC (0.1 ponto); abaixo disso é ruído da série
MIN_COPOM_STEP = Decimal("0.001")


def month_ends(start: date, end: date) -> list[date]:
    """O primeiro dia, o fim de cada mês entre os dois e o último dia, sem repetir."""
    days = [start]
    year, month = start.year, start.month
    while True:
        last = date(year, month, monthrange(year, month)[1])
        if last >= end:
            break
        if last > start:
            days.append(last)
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    if end > start:
        days.append(end)
    return days


def point_on(
    day: date, macro: MacroCourse, budget: BudgetCourse | None
) -> EconomyPointDTO:
    selic = annual_index_rate(IndicatorSeries.SELIC, day)
    ipca = annual_index_rate(IndicatorSeries.IPCA, day)
    country = macro.latest(day)
    account = budget.latest(day) if budget is not None else None
    return EconomyPointDTO(
        date=day,
        selic=selic,
        ipca=ipca,
        real_rate=selic - ipca,
        target=inflation_target(day),
        tolerance=inflation_tolerance(day),
        growth=country.growth,
        unemployment=country.unemployment,
        debt=account.debt if account is not None else None,
        premium=account.premium if account is not None else None,
    )


def copom_changes(start: date, end: date) -> list[CopomChangeDTO]:
    """Os dias entre `start` e `end` em que a SELIC mudou de nível."""
    history = repository.economic.get_history(IndicatorSeries.SELIC)
    before = last_known_value(IndicatorSeries.SELIC, start - timedelta(days=1))
    level = None if before is None else annualize_daily(before)

    changes: list[CopomChangeDTO] = []
    for day in history.dates:
        if day < start or day > end:
            continue
        annual = annualize_daily(history.values[day])
        if level is None:
            level = annual
        elif abs(annual - level) >= MIN_COPOM_STEP:
            changes.append(
                CopomChangeDTO(date=day, change=annual - level, selic=annual)
            )
            level = annual
    return changes


def debt_summary(budget: BudgetCourse, today: date) -> DebtSummaryDTO:
    month = budget.latest(today)
    return DebtSummaryDTO(
        month_end=month.month_end,
        debt=month.debt,
        premium=month.premium,
        debt_amount=month.debt * month.gdp,
        gdp=month.gdp,
        month_result=month.monthly(month.result) if month.closed else None,
    )


def growth_parts(macro: MacroCourse, today: date) -> GrowthPartsDTO:
    """As partes do alvo do crescimento com o que o jogador conhece hoje, e onde o crescimento está."""
    aim = growth_aim(today)
    return GrowthPartsDTO(
        trend=aim.trend,
        real_rate=aim.real_rate,
        real_rate_part=aim.real_rate_part,
        neutral_real_rate=NEUTRAL_REAL_RATE,
        stocks=aim.stocks,
        stocks_part=aim.stocks_part,
        target=aim.value,
        growth=macro.latest(today).growth,
    )


def build_economy_panel(
    start: date,
    today: date,
    macro: MacroCourse,
    budget: BudgetCourse | None = None,
) -> EconomyPanelDTO:
    """`budget` só existe nas partidas com a expansão Governo; sem ele a dívida fica de fora."""
    # Antes do primeiro pregão o painel já mostra o dia de partida
    end = max(start, today)
    changes = copom_changes(start, end)
    # Um ponto por mês e um em cada mudança da SELIC: o degrau cai sobre a linha
    days = sorted({*month_ends(start, end), *(change.date for change in changes)})
    return EconomyPanelDTO(
        points=[point_on(day, macro, budget) for day in days],
        copom_changes=changes,
        growth_parts=growth_parts(macro, today),
        debt=debt_summary(budget, today) if budget is not None else None,
    )
