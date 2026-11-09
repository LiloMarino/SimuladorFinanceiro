"""
O painel da economia: a SELIC, o IPCA e o juro real desde o primeiro dia da
partida, só com o que o jogador já conhece em `today`.
"""

import math
from calendar import monthrange
from collections.abc import Iterable
from datetime import date, timedelta
from decimal import Decimal

from backend.core import repository
from backend.core.dto.economy import (
    ActiveEffectDTO,
    CopomChangeDTO,
    DebtCausesDTO,
    DebtSummaryDTO,
    EconomyPanelDTO,
    EconomyPointDTO,
    GrowthPartsDTO,
    LinkEffectDTO,
)
from backend.core.enum import EconomyLink, IndicatorSeries
from backend.core.indicators import (
    annual_index_rate,
    annualize_daily,
    inflation_target,
    inflation_tolerance,
    last_known_rate,
    last_known_value,
)
from backend.core.rates import Percent
from backend.features.economy.debt import nominal_growth, stabilizing_primary
from backend.features.economy.growth import INFLATION_THRESHOLD, MacroCourse
from backend.features.economy.layer import central_bank_reaction
from backend.features.government import measures as rules
from backend.features.government import spending_effects
from backend.features.government.budget import BudgetCourse, DebtChange
from backend.features.government.linked_economy import LinkedEconomy
from backend.features.government.spending_effects import SpendingEconomy
from backend.features.government.state import Measure

# Degrau mínimo para contar como mudança da SELIC (0.1 ponto); abaixo disso é ruído da série
MIN_COPOM_STEP = Decimal("0.001")
# A variação da dívida por causa soma os últimos 12 meses fechados
CAUSES_MONTHS = 12


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


def ibovespa_on(day: date, *, stored: bool = False) -> Decimal | None:
    return last_known_value(IndicatorSeries.IBOV, day, stored=stored)


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
        ibovespa=ibovespa_on(day),
        stored_selic=(
            annual_index_rate(IndicatorSeries.SELIC, day, stored=True)
            if budget is not None
            else None
        ),
        stored_ipca=(
            annual_index_rate(IndicatorSeries.IPCA, day, stored=True)
            if budget is not None
            else None
        ),
        stored_ibovespa=ibovespa_on(day, stored=True) if budget is not None else None,
    )


def copom_changes(start: date, end: date) -> list[CopomChangeDTO]:
    """Os dias entre `start` e `end` em que a SELIC mudou de nível."""
    history = repository.economic.get_history(IndicatorSeries.SELIC)
    before = last_known_rate(IndicatorSeries.SELIC, start - timedelta(days=1))
    level = None if before is None else annualize_daily(before)

    changes: list[CopomChangeDTO] = []
    for day in history.dates:
        if day < start or day > end:
            continue
        annual = annualize_daily(Percent(history.values[day]))
        if level is None:
            level = annual
        elif abs(annual - level) >= MIN_COPOM_STEP:
            changes.append(
                CopomChangeDTO(date=day, change=annual - level, selic=annual)
            )
            level = annual
    return changes


def debt_summary(linked: LinkedEconomy, today: date) -> DebtSummaryDTO:
    month = linked.budget.latest(today)
    recent = linked.budget.months_until(today)[-CAUSES_MONTHS:]
    causes = sum((m.change for m in recent), DebtChange())
    history = linked.base_budget().latest(today)
    country = linked.macro.latest(today)
    return DebtSummaryDTO(
        month_end=month.month_end,
        debt=month.debt,
        premium=month.premium,
        history_debt=history.debt,
        rate=month.rate,
        causes=DebtCausesDTO(
            months=len(recent),
            interest=causes.interest,
            growth=causes.growth,
            inflation=causes.inflation,
            primary=causes.primary,
        ),
        debt_amount=month.debt * month.gdp,
        gdp=month.gdp,
        month_result=month.monthly(month.result) if month.closed else None,
        primary=month.primary,
        stabilizing_primary=stabilizing_primary(
            month.debt,
            month.rate,
            nominal_growth(
                country.growth, annual_index_rate(IndicatorSeries.IPCA, today)
            ),
        ),
        history_stabilizing_primary=stabilizing_primary(
            history.debt,
            history.rate,
            nominal_growth(
                country.base_growth,
                annual_index_rate(IndicatorSeries.IPCA, today, stored=True),
            ),
        ),
    )


def growth_parts(macro: MacroCourse, today: date) -> GrowthPartsDTO:
    """O crescimento e o desemprego do último fechamento: a história e o que a partida somou por causa."""
    month = macro.latest(today)
    return GrowthPartsDTO(
        history_growth=month.base_growth,
        real_rate=month.gap.real_rate,
        stocks=month.gap.stocks,
        works=month.gap.spending,
        impulse=month.gap.impulse,
        inflation=month.gap.inflation,
        crowding_out=month.gap.crowding,
        growth=month.growth,
        history_unemployment=month.base_unemployment,
        unemployment=month.unemployment,
    )


def points(value: float) -> Decimal:
    return Decimal(str(round(value, 4)))


def link_effects(linked: LinkedEconomy, today: date) -> list[LinkEffectDTO]:
    """
    As ligações que valem hoje, pelo desvio do último mês fechado. Com a SELIC do
    governo, a reação do Banco Central some de cada ligação e a SELIC entra como
    ligação própria.
    """
    link = linked.links_on(today)
    stocks = linked.layer.stocks_parts(today)
    reacts = linked.layer.reacts(today)
    country = linked.macro.latest(today)

    def effect(
        kind: EconomyLink,
        gap: Decimal,
        inflation: float,
        exponent: float,
        growth: Decimal = Decimal(0),
        unemployment: Decimal = Decimal(0),
    ) -> LinkEffectDTO:
        return LinkEffectDTO(
            link=kind,
            gap=gap,
            inflation=points(inflation),
            selic=points(central_bank_reaction(inflation) if reacts else 0.0),
            stocks=points(math.exp(exponent) - 1),
            growth=growth,
            unemployment=unemployment,
        )

    def excess(inflation: Decimal) -> Decimal:
        return max(Decimal(0), inflation - INFLATION_THRESHOLD)

    government: list[LinkEffectDTO] = []
    if not reacts:
        selic = linked.layer.selic_points(today)
        government.append(
            LinkEffectDTO(
                link=EconomyLink.SELIC,
                gap=Decimal(str(round(selic / 100, 6))),
                inflation=Decimal(0),
                selic=points(selic),
                stocks=points(math.exp(stocks.selic) - 1),
                growth=Decimal(0),
            )
        )
    return [
        *government,
        effect(
            EconomyLink.REAL_RATE,
            link.real_rate_gap,
            link.rate_points,
            stocks.real_rate,
        ),
        effect(
            EconomyLink.PHILLIPS,
            link.unemployment_gap,
            link.phillips_points,
            stocks.phillips,
        ),
        effect(
            EconomyLink.FISCAL_RISK,
            link.premium_gap,
            link.premium_inflation_points,
            stocks.fiscal_risk,
        ),
        effect(EconomyLink.GDP, link.gdp_gap, 0.0, stocks.gdp),
        effect(
            EconomyLink.INFLATION_BRAKE,
            excess(country.aim.inflation) - excess(country.base_aim.inflation),
            0.0,
            0.0,
            country.gap.inflation,
        ),
        effect(
            EconomyLink.CROWDING_OUT,
            link.premium_gap,
            0.0,
            0.0,
            country.gap.crowding,
        ),
        effect(
            EconomyLink.CONSUMPTION_TAX,
            link.consumption_gap,
            link.consumption_points,
            stocks.consumption,
        ),
        effect(
            EconomyLink.CORPORATE_TAX,
            link.corporate_gap,
            0.0,
            stocks.corporate,
        ),
        effect(
            EconomyLink.PAYROLL_TAX,
            link.payroll_gap,
            0.0,
            0.0,
            unemployment=link.payroll_jobs,
        ),
    ]


def active_effects(
    economy: SpendingEconomy,
    measures: Iterable[Measure],
    today: date,
    *,
    reacts: bool = True,
) -> list[ActiveEffectDTO]:
    """
    Os efeitos das medidas de gasto aprovadas, do mais novo ao mais antigo. Com a SELIC
    do governo (`reacts` falso), a medida põe só inflação: a SELIC e a bolsa vêm da
    decisão das reuniões.
    """
    by_id = {m.id: m for m in measures}
    effects = []
    for now in reversed(economy.now(today)):
        effect = now.effect
        measure = by_id[effect.measure_id]
        elapsed = spending_effects.elapsed_months(effect.start, today)
        effects.append(
            ActiveEffectDTO(
                measure_id=effect.measure_id,
                kind=effect.kind,
                title=rules.title(measure),
                value=measure.value or Decimal(0),
                before=measure.before or Decimal(0),
                effective=effect.start,
                peak_on=spending_effects.peak_on(effect),
                faded_on=spending_effects.faded_on(effect),
                phase=now.phase,
                inflation=points(now.inflation),
                selic=points(now.selic if reacts else 0.0),
                stocks=points(now.stocks if reacts else 0.0),
                curve=[
                    points(value)
                    for value in spending_effects.curve(effect.kind, effect.steps)
                ],
                elapsed_months=max(int(elapsed), 0),
            )
        )
    return effects


def build_economy_panel(
    start: date,
    today: date,
    macro: MacroCourse,
    linked: LinkedEconomy | None = None,
    economy: SpendingEconomy | None = None,
    measures: Iterable[Measure] = (),
) -> EconomyPanelDTO:
    """`linked` e `economy` só existem nas partidas com a expansão Governo; sem eles a dívida, os efeitos e as ligações ficam de fora."""
    budget = None
    if linked is not None:
        linked.close_until(today)
        budget = linked.budget
    # Antes do primeiro pregão o painel já mostra o dia de partida
    end = max(start, today)
    changes = copom_changes(start, end)
    # Um ponto por mês e um em cada mudança da SELIC: o degrau cai sobre a linha
    days = sorted({*month_ends(start, end), *(change.date for change in changes)})
    return EconomyPanelDTO(
        points=[point_on(day, macro, budget) for day in days],
        copom_changes=changes,
        growth_parts=growth_parts(macro, today),
        debt=debt_summary(linked, today) if linked is not None else None,
        effects=(
            active_effects(
                economy,
                measures,
                today,
                reacts=linked is None or linked.layer.reacts(today),
            )
            if economy is not None
            else None
        ),
        links=link_effects(linked, today) if linked is not None else None,
    )
