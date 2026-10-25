"""
A política de impostos em vigor: as alíquotas e isenções que o jogo cobra. Os valores
padrão são os da lei brasileira; a expansão Governo & Política os muda por medida
aprovada no Congresso. A renda variável e a renda fixa leem a mesma política, por isso
ela mora no ancestral comum das duas.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

from backend.core.enum import AssetClass


class LossPool(Enum):
    """Conjunto de operações cujos prejuízos se compensam entre si."""

    COMMON = "COMMON"
    DAY_TRADE = "DAY_TRADE"
    FII = "FII"
    CRYPTO = "CRYPTO"


@dataclass(frozen=True, slots=True)
class SectorRule:
    """
    O que o governo decidiu para um setor, ou para um segmento dele. Isento tira a venda
    do cálculo do mês; `extra` soma pontos (0.05 = 5 pontos) à alíquota do ganho.
    """

    sector: str
    segment: str | None
    exempt: bool
    extra: Decimal = Decimal(0)

    def covers(self, sector: str, segment: str) -> bool:
        return self.sector == sector and self.segment in (None, segment)


@dataclass(frozen=True, slots=True)
class TaxPolicy:
    rates: Mapping[LossPool, Decimal]
    # Teto mensal de vendas de ações abaixo do qual o ganho comum é isento
    stock_exemption_limit: Decimal
    crypto_exemption_limit: Decimal
    # Tabela regressiva da renda fixa: (até N dias corridos de aplicação, alíquota)
    fixed_income_brackets: tuple[tuple[int, Decimal], ...]
    fixed_income_floor: Decimal
    lci_lca_rate: Decimal
    # Da regra mais antiga para a mais nova
    sector_rules: tuple[SectorRule, ...] = ()

    @property
    def exemption_limits(self) -> Mapping[AssetClass, Decimal]:
        """Teto mensal de vendas abaixo do qual o ganho comum da classe é isento."""
        return {
            AssetClass.STOCK: self.stock_exemption_limit,
            AssetClass.CRYPTO: self.crypto_exemption_limit,
        }

    @property
    def fixed_income_top_rate(self) -> Decimal:
        """A alíquota da primeira faixa da renda fixa: a mais alta da tabela."""
        return (
            self.fixed_income_brackets[0][1]
            if self.fixed_income_brackets
            else self.fixed_income_floor
        )

    def sector_rule(self, sector: str | None, segment: str | None) -> SectorRule | None:
        """
        A regra que vale para o ativo: a do segmento vence a do setor, e entre duas do
        mesmo alcance vale a mais nova.
        """
        if sector is None:
            return None
        covering = [r for r in self.sector_rules if r.covers(sector, segment or "")]
        by_segment = [r for r in covering if r.segment is not None]
        pool = by_segment or covering
        return pool[-1] if pool else None


DEFAULT_TAX_POLICY = TaxPolicy(
    rates={
        LossPool.COMMON: Decimal("0.15"),
        LossPool.DAY_TRADE: Decimal("0.20"),
        LossPool.FII: Decimal("0.20"),
        LossPool.CRYPTO: Decimal("0.15"),
    },
    stock_exemption_limit=Decimal(20000),
    crypto_exemption_limit=Decimal(35000),
    fixed_income_brackets=(
        (180, Decimal("0.225")),
        (360, Decimal("0.20")),
        (720, Decimal("0.175")),
    ),
    fixed_income_floor=Decimal("0.15"),
    lci_lca_rate=Decimal(0),
)

# A política em vigor num dia; sem governo, é sempre a padrão
PolicyOn = Callable[[date], TaxPolicy]


def default_policy_on(_day: date) -> TaxPolicy:
    return DEFAULT_TAX_POLICY
