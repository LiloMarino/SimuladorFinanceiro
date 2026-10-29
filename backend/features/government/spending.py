"""
As medidas de gasto público: o auxílio e as obras (em fração do PIB por ano) e o
reajuste real dos servidores e das aposentadorias (em fração ao ano, acima da
inflação). A linha do tempo diz o valor de cada medida em cada dia e o gasto total do
governo que sai delas; tudo é função pura sobre `Measure`.
"""

from bisect import bisect_right
from collections.abc import Iterable
from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from backend.core.enum import MeasureKind, MeasureStatus
from backend.core.utils import required
from backend.features.government import voters

if TYPE_CHECKING:
    from backend.features.government.state import Measure

ZERO = Decimal(0)
ONE = Decimal(1)

# Gasto base do governo, em fração do PIB por ano: as quatro categorias abaixo estão dentro dele
BASE_SPENDING = Decimal("0.19")

# O valor em vigor antes de qualquer medida: o auxílio e as obras são o gasto da
# categoria; o reajuste real parte de zero, que só mantém o poder de compra
DEFAULTS: dict[MeasureKind, Decimal] = {
    MeasureKind.WELFARE_SPENDING: Decimal("0.015"),
    MeasureKind.PUBLIC_WORKS: Decimal("0.007"),
    MeasureKind.SERVANT_RAISE: ZERO,
    MeasureKind.RETIREE_RAISE: ZERO,
}

# Quanto a medida anda por passo de referência, que é também o máximo de uma medida
STEPS: dict[MeasureKind, Decimal] = {
    kind: voters.EFFECT_STEPS[kind] for kind in DEFAULTS
}

# Teto do valor em vigor: o auxílio e as obras, em fração do PIB; os reajustes, ao ano
LIMITS: dict[MeasureKind, Decimal] = {
    MeasureKind.WELFARE_SPENDING: Decimal("0.05"),
    MeasureKind.PUBLIC_WORKS: Decimal("0.03"),
    MeasureKind.SERVANT_RAISE: Decimal("0.15"),
    MeasureKind.RETIREE_RAISE: Decimal("0.15"),
}

# Gasto de hoje com a folha que o reajuste multiplica, em fração do PIB por ano
RAISE_BASES: dict[MeasureKind, Decimal] = {
    MeasureKind.SERVANT_RAISE: Decimal("0.033"),
    MeasureKind.RETIREE_RAISE: Decimal("0.080"),
}

KINDS = tuple(DEFAULTS)

# O peso de cada medida no gasto antes de qualquer mudança, em fração do PIB por ano
DEFAULT_COSTS: dict[MeasureKind, Decimal] = {
    kind: RAISE_BASES.get(kind, DEFAULTS[kind]) for kind in KINDS
}

# O resto do gasto do país, que as medidas não mexem
REST_SPENDING = BASE_SPENDING - sum(DEFAULT_COSTS.values(), ZERO)


def is_raise(kind: MeasureKind) -> bool:
    return kind in RAISE_BASES


def steps_of(
    kind: MeasureKind, value: Decimal | None, before: Decimal | None
) -> Decimal:
    """Quantos passos de referência a medida anda; positivo gasta mais, negativo corta."""
    return ((value or ZERO) - (before or ZERO)) / STEPS[kind]


def cost_change(
    kind: MeasureKind, value: Decimal | None, before: Decimal | None
) -> Decimal:
    """
    Quanto a medida muda o gasto no primeiro ano, em fração do PIB por ano: o auxílio e as
    obras andam o próprio valor; o reajuste anda a folha que ele multiplica.
    """
    moved = (value or ZERO) - (before or ZERO)
    return moved * RAISE_BASES.get(kind, ONE)


class SpendingTimeline:
    """O valor de cada medida de gasto ao longo da partida: o padrão mais cada medida aprovada, no dia em que vale."""

    def __init__(self, measures: Iterable["Measure"]):
        measures = list(measures)
        self._measures = measures
        approved = sorted(
            (
                m
                for m in measures
                if m.kind.is_spending
                and m.status is MeasureStatus.APPROVED
                and m.effective is not None
            ),
            key=lambda m: (m.effective, m.id),
        )
        self._days: dict[MeasureKind, list[date]] = {k: [] for k in KINDS}
        self._values: dict[MeasureKind, list[Decimal]] = {k: [] for k in KINDS}
        for measure in approved:
            self._days[measure.kind].append(required(measure.effective))
            self._values[measure.kind].append(required(measure.value))

    def with_measure(self, measure: "Measure", effective: date) -> "SpendingTimeline":
        """A linha do tempo como ficaria se a medida passasse e valesse em `effective`."""
        return SpendingTimeline(
            [
                *self._measures,
                replace(measure, status=MeasureStatus.APPROVED, effective=effective),
            ]
        )

    def value_on(self, kind: MeasureKind, day: date) -> Decimal:
        index = bisect_right(self._days[kind], day)
        return self._values[kind][index - 1] if index else DEFAULTS[kind]

    def latest(self, kind: MeasureKind) -> Decimal:
        """O valor depois de todas as medidas aprovadas valerem."""
        values = self._values[kind]
        return values[-1] if values else DEFAULTS[kind]

    def multiplier(self, kind: MeasureKind, day: date) -> Decimal:
        """
        O quanto a folha cresceu acima da inflação até `day`: todo 1º de janeiro, a partir
        da vigência da primeira medida, ela sobe o reajuste que vale naquele dia.
        """
        days = self._days[kind]
        if not days:
            return ONE
        product = ONE
        for year in range(days[0].year, day.year + 1):
            january = date(year, 1, 1)
            if days[0] <= january <= day:
                product *= ONE + self.value_on(kind, january)
        return product

    def cost_on(self, kind: MeasureKind, day: date) -> Decimal:
        """Quanto a medida pesa no gasto do governo no dia, em fração do PIB por ano."""
        if is_raise(kind):
            return RAISE_BASES[kind] * self.multiplier(kind, day)
        return self.value_on(kind, day)

    def since(self, kind: MeasureKind, day: date) -> date | None:
        """O dia em que passou a valer o valor que a medida tem em `day`; nulo quando é o padrão."""
        index = bisect_right(self._days[kind], day)
        return self._days[kind][index - 1] if index else None

    def spending_on(self, day: date) -> Decimal:
        """O gasto total do governo no dia, em fração do PIB por ano."""
        return BASE_SPENDING + sum(
            (self.cost_on(kind, day) - DEFAULT_COSTS[kind] for kind in KINDS), ZERO
        )
