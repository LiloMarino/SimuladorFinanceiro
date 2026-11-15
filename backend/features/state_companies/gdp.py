"""Contas do efeito das estatais fundadas no PIB: o gasto da fundação e o empurrão permanente."""

from collections.abc import Iterable, Mapping
from decimal import Decimal

from backend.core.enum import DividendPolicy, StateLever

# A fundação é gasto primário espalhado em 12 meses a partir do mês da vigência
FOUNDING_MONTHS = 12

# Empurrão permanente no crescimento, em fração ao ano por raiz de bilhão de reais: uma
# estatal grande (R$ 300 bi) sozinha soma cerca de 0,13 ponto ao ano
GDP_PER_ROOT_BILLION = Decimal("0.000075")

# O porte efetivo da estatal anda 1% do original por mês: reinvestir o lucro o cresce e
# apertar o dividendo o encolhe, dentro de metade e uma vez e meia o porte original
SIZE_STEP = Decimal("0.01")
MIN_SIZE_MULTIPLIER = Decimal("0.5")
MAX_SIZE_MULTIPLIER = Decimal("1.5")


def founding_installment(invested: Decimal) -> Decimal:
    """A parcela mensal do gasto da fundação, em reais."""
    return invested / FOUNDING_MONTHS


def size_path(policies: Iterable[DividendPolicy]) -> list[Decimal]:
    """O porte efetivo sobre o original ao fim de cada mês, uma política por mês, do primeiro ao último."""
    multiplier = Decimal(1)
    path: list[Decimal] = []
    for policy in policies:
        if policy is DividendPolicy.REINVEST:
            multiplier += SIZE_STEP
        elif policy is DividendPolicy.SQUEEZE:
            multiplier -= SIZE_STEP
        multiplier = max(MIN_SIZE_MULTIPLIER, min(MAX_SIZE_MULTIPLIER, multiplier))
        path.append(multiplier)
    return path


def size_multiplier(policies: Iterable[DividendPolicy]) -> Decimal:
    """O porte efetivo sobre o original depois de uma política por mês, do primeiro ao último."""
    path = size_path(policies)
    return path[-1] if path else Decimal(1)


def permanent_push(
    effective_billions_by_sector: Mapping[StateLever | None, Decimal],
) -> Decimal:
    """
    O empurrão no crescimento, em fração ao ano: a raiz da soma do porte efetivo (em
    bilhões) de cada setor, vezes a constante. A raiz faz a segunda estatal do mesmo
    setor valer menos que a primeira.
    """
    return GDP_PER_ROOT_BILLION * sum(
        (total.sqrt() for total in effective_billions_by_sector.values() if total > 0),
        Decimal(0),
    )
