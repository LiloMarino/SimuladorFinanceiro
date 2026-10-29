"""O efeito das medidas de gasto como as telas o mostram: a inflação esperada de uma proposta e o cartão Gasto público."""

from datetime import date
from decimal import Decimal

from backend.core.dto.government import (
    GroupReactionDTO,
    InflationCurvePointDTO,
    InflationEffectDTO,
    MeasureDTO,
    SpendingCardDTO,
    SpendingRowDTO,
)
from backend.core.enum import IndicatorSeries, MeasureKind, VoterGroup
from backend.core.indicators import annual_index_rate
from backend.features.government import approval as approval_rules
from backend.features.government import spending, spending_effects
from backend.features.government.state import Measure

HUNDRED = Decimal(100)


def points(value: float) -> Decimal:
    """Pontos de IPCA em 4 casas, como o painel os guarda."""
    return Decimal(str(round(value, 4)))


def inflation_effect(measure: Measure, today: date) -> InflationEffectDTO | None:
    """A inflação, a SELIC e a bolsa esperadas da medida de gasto, se ela passar; nulo nos impostos."""
    if not measure.kind.is_spending:
        return None
    steps = float(spending.steps_of(measure.kind, measure.value, measure.before))
    peak = spending_effects.peak_inflation(measure.kind, steps)
    ipca = annual_index_rate(IndicatorSeries.IPCA, today)
    selic = annual_index_rate(IndicatorSeries.SELIC, today)
    return InflationEffectDTO(
        peak=points(peak),
        peak_month=int(spending_effects.DELAY_MONTHS),
        curve=[
            InflationCurvePointDTO(month=month, points=points(value))
            for month, value in enumerate(spending_effects.curve(measure.kind, steps))
        ],
        ipca_before=ipca,
        ipca_after=ipca + points(peak) / HUNDRED,
        selic_before=selic,
        selic_after=selic + points(spending_effects.SELIC_REACTION * peak) / HUNDRED,
        stocks=points(spending_effects.peak_stocks(measure.kind, steps)),
        growth=points(spending_effects.GROWTH_PER_STEP.get(measure.kind, 0.0) * steps),
    )


def reactions(measure: Measure) -> list[GroupReactionDTO]:
    """Quanto cada grupo de eleitores muda de opinião quando a medida vale cheia."""
    return [
        GroupReactionDTO(
            group=group, points=approval_rules.measure_reaction(group, measure)
        )
        for group in VoterGroup
    ]


def peak_inflation(measure: Measure) -> Decimal:
    """Os pontos de IPCA que a medida soma quando o efeito vale cheio; zero nos impostos."""
    if not measure.kind.is_spending:
        return Decimal(0)
    steps = float(spending.steps_of(measure.kind, measure.value, measure.before))
    return points(spending_effects.peak_inflation(measure.kind, steps))


def spending_card(
    timeline: spending.SpendingTimeline,
    economy: spending_effects.SpendingEconomy,
    gdp: Decimal,
    today: date,
    pending: dict[MeasureKind, MeasureDTO],
    promised: set[MeasureKind],
) -> SpendingCardDTO:
    """O cartão Gasto público: cada medida com o valor em vigor, o que pesa no gasto e o que soma ao IPCA hoje."""
    rows = []
    for kind in spending.KINDS:
        latest = economy.latest_of(kind)
        elapsed = (
            spending_effects.elapsed_months(latest.start, today) if latest else None
        )
        cost = timeline.cost_on(kind, today)
        rows.append(
            SpendingRowDTO(
                kind=kind,
                value=timeline.value_on(kind, today),
                since=timeline.since(kind, today),
                cost=cost,
                cost_amount=cost * gdp,
                step=spending.STEPS[kind],
                limit=spending.LIMITS[kind],
                inflation=points(economy.inflation_of(kind, today)),
                phase=spending_effects.phase_of(latest, today) if latest else None,
                curve=(
                    [
                        points(value)
                        for value in spending_effects.curve(kind, latest.steps)
                    ]
                    if latest
                    else []
                ),
                elapsed_months=(max(int(elapsed), 0) if elapsed is not None else None),
                pending=pending.get(kind),
                promised=kind in promised,
            )
        )
    total = timeline.spending_on(today)
    return SpendingCardDTO(
        rows=rows,
        rest=spending.REST_SPENDING,
        total=total,
        total_difference=total - spending.BASE_SPENDING,
        inflation=points(economy.inflation_points(today)),
    )
