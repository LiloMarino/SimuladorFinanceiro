"""
As medidas do presidente: o que cada uma muda na política de impostos (as de gasto
público moram em `spending`). Tudo aqui é função pura sobre `Measure`.
"""

from bisect import bisect_right
from collections.abc import Iterable
from dataclasses import replace
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from backend.core.enum import MeasureKind, MeasureStatus
from backend.core.utils import required
from backend.features.government.state import Measure
from backend.features.tax_policy import (
    DEFAULT_TAX_POLICY,
    LossPool,
    SectorRule,
    TaxPolicy,
)

MONTHS = (
    "jan",
    "fev",
    "mar",
    "abr",
    "mai",
    "jun",
    "jul",
    "ago",
    "set",
    "out",
    "nov",
    "dez",
)

HUNDRED = Decimal(100)


def apply_measure(policy: TaxPolicy, measure: Measure) -> TaxPolicy:
    value = measure.value
    match measure.kind:
        case MeasureKind.STOCK_PROFIT_RATE:
            return replace(
                policy, rates={**policy.rates, LossPool.COMMON: required(value)}
            )
        case MeasureKind.DAY_TRADE_RATE:
            return replace(
                policy, rates={**policy.rates, LossPool.DAY_TRADE: required(value)}
            )
        case MeasureKind.STOCK_EXEMPTION:
            return replace(policy, stock_exemption_limit=required(value))
        case MeasureKind.FIXED_INCOME_TABLE:
            return replace(
                policy, fixed_income_brackets=(), fixed_income_floor=required(value)
            )
        case MeasureKind.LCI_LCA_RATE:
            return replace(policy, lci_lca_rate=required(value))
        case MeasureKind.SECTOR_EXEMPT | MeasureKind.SECTOR_TAX:
            rule = SectorRule(
                sector=required(measure.sector),
                segment=measure.segment,
                exempt=measure.kind is MeasureKind.SECTOR_EXEMPT,
                extra=value or Decimal(0),
            )
            return replace(policy, sector_rules=(*policy.sector_rules, rule))
        case (
            MeasureKind.WELFARE_SPENDING
            | MeasureKind.SERVANT_RAISE
            | MeasureKind.RETIREE_RAISE
            | MeasureKind.PUBLIC_WORKS
        ):
            # O gasto público não mexe nos impostos; vive na linha do tempo do gasto
            return policy


def general_value(policy: TaxPolicy, kind: MeasureKind) -> Decimal | None:
    """O valor que uma medida geral muda, como está na política."""
    match kind:
        case MeasureKind.STOCK_PROFIT_RATE:
            return policy.rates[LossPool.COMMON]
        case MeasureKind.DAY_TRADE_RATE:
            return policy.rates[LossPool.DAY_TRADE]
        case MeasureKind.STOCK_EXEMPTION:
            return policy.stock_exemption_limit
        case MeasureKind.FIXED_INCOME_TABLE:
            return policy.fixed_income_top_rate
        case MeasureKind.LCI_LCA_RATE:
            return policy.lci_lca_rate
        case _:
            return None


class PolicyTimeline:
    """As políticas de impostos ao longo da partida: a padrão mais cada medida aprovada, no dia em que vale."""

    def __init__(self, measures: Iterable[Measure]):
        approved = sorted(
            (
                m
                for m in measures
                if m.status is MeasureStatus.APPROVED
                and m.effective is not None
                and not m.kind.is_spending
            ),
            key=lambda m: (m.effective, m.id),
        )
        self._days: list[date] = []
        self._policies: list[TaxPolicy] = []
        policy = DEFAULT_TAX_POLICY
        for measure in approved:
            policy = apply_measure(policy, measure)
            self._days.append(required(measure.effective))
            self._policies.append(policy)

    def on(self, day: date) -> TaxPolicy:
        index = bisect_right(self._days, day)
        return self._policies[index - 1] if index else DEFAULT_TAX_POLICY

    @property
    def latest(self) -> TaxPolicy:
        """A política depois de todas as medidas aprovadas valerem."""
        return self._policies[-1] if self._policies else DEFAULT_TAX_POLICY


def title(measure: Measure) -> str:
    value = measure.value
    match measure.kind:
        case MeasureKind.STOCK_PROFIT_RATE:
            return f"Ações: IR das vendas com lucro em {percent(value)}"
        case MeasureKind.DAY_TRADE_RATE:
            return f"Ações: IR do day trade em {percent(value)}"
        case MeasureKind.STOCK_EXEMPTION:
            if not value:
                return "Isenção de vendas de ações acaba"
            return f"Isenção de vendas de ações passa a {money_per_month(value)}"
        case MeasureKind.FIXED_INCOME_TABLE:
            return f"Renda fixa: tabela única de {percent(value)}"
        case MeasureKind.LCI_LCA_RATE:
            if not value:
                return "LCI e LCA: isentas de IR"
            return f"LCI e LCA: IR de {percent(value)}"
        case MeasureKind.SECTOR_EXEMPT:
            return f"{target_name(measure)}: IR isento"
        case MeasureKind.SECTOR_TAX:
            return (
                f"{target_name(measure)}: +{number(required(value) * HUNDRED)} pontos no IR "
                "das vendas com lucro"
            )
        case MeasureKind.WELFARE_SPENDING:
            return f"Auxílio: {percent(value)} do PIB"
        case MeasureKind.SERVANT_RAISE:
            return f"Servidores: reajuste de {percent(value)} acima da inflação"
        case MeasureKind.RETIREE_RAISE:
            return f"Aposentadorias: reajuste de {percent(value)} acima da inflação"
        case MeasureKind.PUBLIC_WORKS:
            return f"Obras: {percent(value)} do PIB"


def target_name(measure: Measure) -> str:
    """O segmento (ou o setor) que a medida atinge."""
    return measure.segment or measure.sector or ""


def percent(value: Decimal | None) -> str:
    return f"{number((value or Decimal(0)) * HUNDRED)}%"


def number(value: Decimal) -> str:
    """Número em português, com vírgula e só as casas que fazem falta: 22,5 e 20."""
    text = f"{value.quantize(Decimal('0.1'), ROUND_HALF_UP):f}"
    return text.removesuffix(".0").replace(".", ",")


def money_per_month(value: Decimal) -> str:
    if value >= 1000 and value % 1000 == 0:
        return f"até R$ {int(value) // 1000} mil/mês"
    return f"até R$ {int(value):,}/mês".replace(",", ".")


def short_date(day: date) -> str:
    """O dia como o jogo escreve: 29 mai 2026."""
    return f"{day.day:02d} {MONTHS[day.month - 1]} {day.year}"
