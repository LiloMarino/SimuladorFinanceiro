"""
Regras do crédito num lugar só: a escada de notas, os prazos e as penalidades.

A nota vem de pontos (0 a 100) e cada nota fixa o spread sobre a SELIC e quanto
da dívida o patrimônio líquido aguenta. Os números aqui valem para o cálculo, a
oferta, as sugestões e os textos da tela.
"""

from dataclasses import dataclass
from decimal import Decimal

from backend.core.enum import CreditGrade

MIN_TERM_MONTHS = 6
MAX_TERM_MONTHS = 60

# Multa única sobre a parcela atrasada e mora de 1% ao mês, simples, por dia corrido
LATE_FEE = Decimal("0.02")
LATE_INTEREST_PER_MONTH = Decimal("0.01")
MONTH_DAYS = Decimal(30)

# Dias de antecedência do aviso de parcela sem caixa
WARNING_DAYS = 7

# O juro nunca fica abaixo da renda fixa mais cara do dia mais esta margem
FIXED_INCOME_MARGIN = Decimal("0.005")

# Pontos da nota
LEVERAGE_MAX_POINTS = Decimal(40)
# 0,4 ponto por ponto percentual de alavancagem: 40 pontos por 100%
LEVERAGE_POINTS_PER_UNIT = Decimal(40)
VOLATILITY_MAX_POINTS = Decimal(30)
VOLATILITY_CEILING = Decimal("0.45")
# Pregões mínimos de histórico para a volatilidade contar; abaixo disso vale zero
VOLATILITY_MIN_SAMPLE = 21
PAYMENT_MAX_POINTS = Decimal(30)
PAYMENT_PENALTY = Decimal(10)
LATE_WINDOW_MONTHS = 12


@dataclass(frozen=True)
class GradeTier:
    grade: CreditGrade
    min_points: int
    # Pontos ao ano somados à SELIC (0.05 = SELIC + 5); None na nota que não recebe crédito
    spread: Decimal | None
    # Fração do patrimônio líquido que a dívida pode chegar a ser
    debt_limit: Decimal


LADDER: tuple[GradeTier, ...] = (
    GradeTier(CreditGrade.AAA, 90, Decimal("0.03"), Decimal("1.00")),
    GradeTier(CreditGrade.AA, 80, Decimal("0.04"), Decimal("0.80")),
    GradeTier(CreditGrade.A, 70, Decimal("0.05"), Decimal("0.60")),
    GradeTier(CreditGrade.BBB, 60, Decimal("0.065"), Decimal("0.45")),
    GradeTier(CreditGrade.BB, 50, Decimal("0.08"), Decimal("0.30")),
    GradeTier(CreditGrade.B, 40, Decimal("0.10"), Decimal("0.20")),
    GradeTier(CreditGrade.CCC, 30, Decimal("0.13"), Decimal("0.10")),
    GradeTier(CreditGrade.D, 0, None, Decimal(0)),
)


def tier_of(grade: CreditGrade) -> GradeTier:
    return next(tier for tier in LADDER if tier.grade is grade)


def grade_for_points(points: Decimal | int) -> CreditGrade:
    """A melhor nota cujo mínimo os pontos alcançam."""
    return next(tier.grade for tier in LADDER if points >= tier.min_points)


def next_tier(grade: CreditGrade) -> GradeTier | None:
    """A nota logo acima de `grade`; None na AAA."""
    index = LADDER.index(tier_of(grade))
    return LADDER[index - 1] if index > 0 else None
