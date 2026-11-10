"""O que a presidência paga ao jogador: o salário do cargo e o legado que a aprovação acumula."""

from collections.abc import Sequence
from decimal import Decimal

from backend.features.government import approval
from backend.features.government.state import ApprovalPoint

# O presidente recebe, por mês, este múltiplo do salário da partida no lugar da renda da profissão
SALARY_MULTIPLE = Decimal(3)
# Cada ponto de aprovação acima do piso soma esta fração de um salário ao legado do mês
LEGACY_PER_POINT = Decimal("0.05")
LEGACY_FLOOR = 40


def month_salaries(point: ApprovalPoint) -> Decimal:
    """O que o fechamento de um mês soma ao legado, em salários: aprovação 60 soma 1."""
    rating = approval.rounded(approval.overall(point.satisfaction))
    return max(0, rating - LEGACY_FLOOR) * LEGACY_PER_POINT


def legacy_salaries(approvals: Sequence[ApprovalPoint]) -> Decimal:
    """O legado do mandato, em salários: a soma dos meses fechados."""
    return sum((month_salaries(point) for point in approvals), Decimal(0))


def average_approval(approvals: Sequence[ApprovalPoint]) -> int:
    """A aprovação média dos meses fechados do mandato; 0 sem nenhum."""
    if not approvals:
        return 0
    ratings = [approval.overall(point.satisfaction) for point in approvals]
    return approval.rounded(sum(ratings, Decimal(0)) / len(ratings))
