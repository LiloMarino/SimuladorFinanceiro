"""
As medidas do presidente: o que cada uma muda na política de impostos, onde cai na régua
da campanha e quanto pesa na aprovação. Tudo aqui é função pura sobre `Measure`.
"""

from bisect import bisect_right
from collections.abc import Iterable
from dataclasses import replace
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from backend.core.enum import MeasureKind, MeasureStatus
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

# Régua da campanha: corte geral de imposto é 1, isenção setorial 2, taxar um setor 4 e
# imposto geral novo 5
RULER_CUT = 1
RULER_SECTOR_EXEMPT = 2
RULER_SECTOR_TAX = 4
RULER_TAX_UP = 5

# Peso na aprovação: imposto novo tira de 1 a 5 pontos e corte soma de 1 a 3
MAX_TAX_PENALTY = 5
MAX_CUT_BONUS = 3
# Pontos de alíquota que valem 1 ponto de bônus no corte
CUT_POINTS_PER_BONUS = Decimal("7.5")
# Pontos somados a um setor que valem 1 ponto de penalidade
SECTOR_POINTS_PER_PENALTY = Decimal(2)
SECTOR_EXEMPT_BONUS = 2
EXEMPTION_RAISED_BONUS = 2
EXEMPTION_LOWERED_PENALTY = 3

# Em quanto tempo o efeito de um imposto novo na aprovação some
FADE_DAYS = 180

HUNDRED = Decimal(100)


def _round(value: Decimal) -> int:
    return int(value.quantize(Decimal(1), ROUND_HALF_UP))


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def _step(measure: Measure) -> Decimal:
    """O quanto a medida muda o imposto geral: positivo é imposto maior."""
    assert measure.value is not None and measure.before is not None
    return measure.value - measure.before


def is_cut(measure: Measure) -> bool:
    """Se a medida alivia o imposto de quem paga; a que tira imposto vale como corte."""
    match measure.kind:
        case MeasureKind.SECTOR_EXEMPT:
            return True
        case MeasureKind.SECTOR_TAX:
            return False
        case MeasureKind.STOCK_EXEMPTION:
            # O teto maior isenta mais vendas
            return _step(measure) > 0
        case _:
            return _step(measure) < 0


def ruler_band(measure: Measure) -> int:
    match measure.kind:
        case MeasureKind.SECTOR_EXEMPT:
            return RULER_SECTOR_EXEMPT
        case MeasureKind.SECTOR_TAX:
            return RULER_SECTOR_TAX
        case _:
            return RULER_CUT if is_cut(measure) else RULER_TAX_UP


def approval_impact(measure: Measure) -> int:
    """Pontos de aprovação ao valer: corte soma, imposto novo tira."""
    match measure.kind:
        case MeasureKind.SECTOR_EXEMPT:
            return SECTOR_EXEMPT_BONUS
        case MeasureKind.SECTOR_TAX:
            assert measure.value is not None
            points = _round(measure.value * HUNDRED / SECTOR_POINTS_PER_PENALTY)
            return -_clamp(points, 1, MAX_TAX_PENALTY)
        case MeasureKind.STOCK_EXEMPTION:
            return (
                EXEMPTION_RAISED_BONUS
                if is_cut(measure)
                else -EXEMPTION_LOWERED_PENALTY
            )
        case _:
            points = abs(_step(measure)) * HUNDRED
            if is_cut(measure):
                return _clamp(_round(points / CUT_POINTS_PER_BONUS), 1, MAX_CUT_BONUS)
            return -_clamp(_round(points), 1, MAX_TAX_PENALTY)


def fade(measure: Measure, today: date) -> Decimal:
    """Quanto do efeito de imposto novo ainda pesa: cheio ao valer, zero em 6 meses."""
    assert measure.effective is not None
    elapsed = (today - measure.effective).days
    return max(Decimal(0), 1 - Decimal(elapsed) / FADE_DAYS)


def current_effect(measure: Measure, today: date) -> int:
    """Pontos que a medida em vigor soma à aprovação hoje; o corte não some, o imposto novo sim."""
    impact = approval_impact(measure)
    return impact if impact > 0 else _round(impact * fade(measure, today))


def apply_measure(policy: TaxPolicy, measure: Measure) -> TaxPolicy:
    value = measure.value
    match measure.kind:
        case MeasureKind.STOCK_PROFIT_RATE:
            assert value is not None
            return replace(policy, rates={**policy.rates, LossPool.COMMON: value})
        case MeasureKind.DAY_TRADE_RATE:
            assert value is not None
            return replace(policy, rates={**policy.rates, LossPool.DAY_TRADE: value})
        case MeasureKind.STOCK_EXEMPTION:
            assert value is not None
            return replace(policy, stock_exemption_limit=value)
        case MeasureKind.FIXED_INCOME_TABLE:
            assert value is not None
            return replace(policy, fixed_income_brackets=(), fixed_income_floor=value)
        case MeasureKind.LCI_LCA_RATE:
            assert value is not None
            return replace(policy, lci_lca_rate=value)
        case MeasureKind.SECTOR_EXEMPT | MeasureKind.SECTOR_TAX:
            assert measure.sector is not None
            rule = SectorRule(
                sector=measure.sector,
                segment=measure.segment,
                exempt=measure.kind is MeasureKind.SECTOR_EXEMPT,
                extra=value or Decimal(0),
            )
            return replace(policy, sector_rules=(*policy.sector_rules, rule))


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
                if m.status is MeasureStatus.APPROVED and m.effective is not None
            ),
            key=lambda m: (m.effective, m.id),
        )
        self._days: list[date] = []
        self._policies: list[TaxPolicy] = []
        policy = DEFAULT_TAX_POLICY
        for measure in approved:
            assert measure.effective is not None
            policy = apply_measure(policy, measure)
            self._days.append(measure.effective)
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
            assert value is not None
            return (
                f"{target_name(measure)}: +{number(value * HUNDRED)} pontos no IR "
                "das vendas com lucro"
            )


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
