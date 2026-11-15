"""O preço da ação de estatal sob as ordens do presidente: o controle de preço e a política de dividendos."""

from collections.abc import Iterable
from decimal import Decimal
from itertools import repeat

from backend.core.enum import DividendPolicy
from backend.core.periods import MONTHS_PER_YEAR
from backend.features.state_companies import gdp, payout
from backend.features.state_companies.orders import StateOrder

# Crescimento anual de referência do preço da importada, perto do retorno médio do valor
# justo da fundada: o porte efetivo acima ou abaixo de 1 o multiplica
POLICY_REFERENCE_GROWTH = 0.04

# O prazo da prévia da ordem: o efeito de cada política no preço depois de 4 anos
PREVIEW_MONTHS = 48


def price_factor(order: StateOrder) -> float:
    """O preço da ação sob a ordem, contra o preço sem ordem: o controle o derruba na mesma
    proporção do corte de lucro."""
    return 1 - float(payout.profit_cut(order.control))


def policy_price_factor(size_path: Iterable[Decimal]) -> float:
    """
    O efeito acumulado da política de dividendos no preço, contra o preço sem ordem: cada
    mês cresce (1 + crescimento de referência vezes (porte efetivo - 1)) ao 1/12. O porte
    efetivo de cada mês vem de `gdp.size_path`; com o porte original o fator é 1 exato.
    """
    factor = 1.0
    for size in size_path:
        factor *= (1 + POLICY_REFERENCE_GROWTH * float(size - 1)) ** (
            1 / MONTHS_PER_YEAR
        )
    return factor


def sustained_policy_factor(
    policy: DividendPolicy, months: int = PREVIEW_MONTHS
) -> float:
    """O efeito da política no preço depois de `months` meses seguidos nela, contra o Normal."""
    return policy_price_factor(gdp.size_path(repeat(policy, months)))


def dividend_factor(order: StateOrder) -> float:
    """O provento histórico da estatal importada sob a ordem, contra o provento sem ordem."""
    return float(payout.dividend_factor(order.dividend_policy, order.control))
