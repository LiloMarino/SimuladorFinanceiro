"""
As profissões do viver de renda: quanto cada uma rende por mês (em múltiplos do salário
do host), o que a sorteia na demissão e qual medida do governo chega até ela. A tabela é
dado puro: quem calcula é o `LifeBudget`.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

from backend.core.enum import IncomeLoss, Profession

# As alavancas do governo no padrão, sem medida aprovada. As alíquotas são as da lei
# (as mesmas de `DEFAULT_TAX_POLICY`) e o auxílio é o gasto de partida
REFERENCE_PERSONAL_RATE = Decimal("0.15")
REFERENCE_CORPORATE_RATE = Decimal("0.34")
REFERENCE_CONSUMPTION_RATE = Decimal("0.18")
REFERENCE_WELFARE_SPENDING = Decimal("0.015")

# O empreendedor ganha 3x o que o PIB de 12 meses passa de 2% (ou perde, abaixo disso)
ENTREPRENEUR_GDP_SENSITIVITY = Decimal(3)
ENTREPRENEUR_NEUTRAL_GROWTH = Decimal("0.02")
ENTREPRENEUR_INCOME_FLOOR = Decimal("0.5")


class RealRaise(Enum):
    """De onde vem o reajuste acima do IPCA no aniversário."""

    NONE = "NONE"
    # Parte do crescimento do PIB de 12 meses (o salário de carteira)
    GDP_SHARE = "GDP_SHARE"
    SERVANTS = "SERVANTS"
    RETIREES = "RETIREES"


class TaxBase(Enum):
    """O imposto cujo desvio contra a lei aumenta ou corta a renda líquida."""

    PERSONAL = "PERSONAL"
    CORPORATE = "CORPORATE"
    CONSUMPTION = "CONSUMPTION"


@dataclass(frozen=True)
class LifeLevers:
    """
    As medidas do governo que chegam à renda dos jogadores no dia. O padrão é o país sem
    medida aprovada: sem governo na partida, todas ficam nele.
    """

    # Reajuste real ao ano, acima do IPCA, dos servidores e dos aposentados
    servant_raise: Decimal = Decimal(0)
    retiree_raise: Decimal = Decimal(0)
    # Gasto com auxílio, em fração do PIB por ano
    welfare_spending: Decimal = REFERENCE_WELFARE_SPENDING
    personal_rate: Decimal = REFERENCE_PERSONAL_RATE
    corporate_rate: Decimal = REFERENCE_CORPORATE_RATE
    consumption_rate: Decimal = REFERENCE_CONSUMPTION_RATE

    def rate_of(self, tax: TaxBase) -> Decimal:
        match tax:
            case TaxBase.PERSONAL:
                return self.personal_rate
            case TaxBase.CORPORATE:
                return self.corporate_rate
            case TaxBase.CONSUMPTION:
                return self.consumption_rate

    def real_raise_of(self, source: RealRaise) -> Decimal:
        match source:
            case RealRaise.SERVANTS:
                return self.servant_raise
            case RealRaise.RETIREES:
                return self.retiree_raise
            case RealRaise.NONE | RealRaise.GDP_SHARE:
                return Decimal(0)


def no_levers(day: date) -> LifeLevers:
    return LifeLevers()


REFERENCE_RATES: dict[TaxBase, Decimal] = {
    TaxBase.PERSONAL: REFERENCE_PERSONAL_RATE,
    TaxBase.CORPORATE: REFERENCE_CORPORATE_RATE,
    TaxBase.CONSUMPTION: REFERENCE_CONSUMPTION_RATE,
}


@dataclass(frozen=True)
class ProfessionRule:
    # A renda do mês exposta ao sorteio da demissão, em múltiplos do salário do host
    income_multiple: Decimal
    tax: TaxBase
    # O que a demissão sorteada faz com ela; nulo quando a profissão ignora o sorteio
    loss: IncomeLoss | None = None
    real_raise: RealRaise = RealRaise.NONE
    # A renda oscila com o PIB de 12 meses do dia
    follows_gdp: bool = False
    # A parte da renda que o auxílio paga, em múltiplos do salário no gasto de referência;
    # a demissão não a tira
    benefit_multiple: Decimal = Decimal(0)
    # Quantas vezes o imprevisto de saúde pesa para esta profissão
    health_multiple: Decimal = Decimal(1)


PROFESSIONS: dict[Profession, ProfessionRule] = {
    Profession.CLT: ProfessionRule(
        income_multiple=Decimal(1),
        tax=TaxBase.PERSONAL,
        loss=IncomeLoss.LAYOFF,
        real_raise=RealRaise.GDP_SHARE,
    ),
    Profession.PUBLIC_SERVANT: ProfessionRule(
        income_multiple=Decimal("0.9"),
        tax=TaxBase.PERSONAL,
        real_raise=RealRaise.SERVANTS,
    ),
    Profession.ENTREPRENEUR: ProfessionRule(
        income_multiple=Decimal("1.2"),
        tax=TaxBase.CORPORATE,
        follows_gdp=True,
    ),
    Profession.RETIREE: ProfessionRule(
        income_multiple=Decimal("0.85"),
        tax=TaxBase.PERSONAL,
        real_raise=RealRaise.RETIREES,
        health_multiple=Decimal(2),
    ),
    Profession.WELFARE: ProfessionRule(
        income_multiple=Decimal("0.5"),
        tax=TaxBase.CONSUMPTION,
        loss=IncomeLoss.GIG_LOSS,
        benefit_multiple=Decimal("0.4"),
    ),
    Profession.LANDLORD: ProfessionRule(
        income_multiple=Decimal(1),
        tax=TaxBase.PERSONAL,
        loss=IncomeLoss.VACANCY,
    ),
}

# O imprevisto cujo valor a saúde de cada profissão multiplica
HEALTH_EVENT_KEY = "HEALTH"


def entrepreneur_gdp_factor(growth: Decimal) -> Decimal:
    """O quanto o PIB de 12 meses move a renda do empreendedor: 1 no PIB de 2%, com piso de 0,5."""
    factor = 1 + ENTREPRENEUR_GDP_SENSITIVITY * (growth - ENTREPRENEUR_NEUTRAL_GROWTH)
    return max(factor, ENTREPRENEUR_INCOME_FLOOR)
