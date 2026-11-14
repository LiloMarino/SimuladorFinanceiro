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

# Dias do ano médio, para contar os anos de uma carreira e de uma herança
DAYS_PER_YEAR = Decimal("365.25")

# A taxa ao ano que traz a herança do Herdeiro a valor presente: o patrimônio que rende
# os salários da partida inteira. Com correção pela inflação o salário sobe com o IPCA e
# o patrimônio rende juro real; sem ela o salário é fixo e o patrimônio rende o CDI nominal.
REAL_INHERITANCE_RATE = Decimal("0.05")
NOMINAL_INHERITANCE_RATE = Decimal("0.10")


def inheritance_rate(inflation_adjusted: bool) -> Decimal:
    return REAL_INHERITANCE_RATE if inflation_adjusted else NOMINAL_INHERITANCE_RATE


class RealRaise(Enum):
    """De onde vem o reajuste acima do IPCA no aniversário."""

    NONE = "NONE"
    # Parte do crescimento do PIB de 12 meses (o salário de carteira)
    GDP_SHARE = "GDP_SHARE"
    SERVANTS = "SERVANTS"
    RETIREES = "RETIREES"


class IncomeDriver(Enum):
    """A variável da partida que move a renda da profissão."""

    # O PIB de 12 meses
    GDP = "GDP"
    # A variação do dólar em 12 meses
    DOLLAR = "DOLLAR"
    # O nível da SELIC ao ano
    SELIC = "SELIC"
    # O retorno do Ibovespa em 12 meses
    STOCKS = "STOCKS"


class StartingCapital(Enum):
    """O capital com que a profissão entra na partida."""

    ROOM = "ROOM"
    # O capital da sala mais a herança
    ROOM_PLUS_INHERITANCE = "ROOM_PLUS_INHERITANCE"
    ZERO = "ZERO"


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
class DriverCurve:
    """
    Quanto a variável move a renda: o fator é `1 + sensibilidade x (valor - neutro)`, entre
    o piso e o teto. No valor neutro a renda vale o múltiplo da profissão.
    """

    sensitivity: Decimal
    neutral: Decimal
    floor: Decimal
    ceiling: Decimal | None = None


DRIVER_CURVES: dict[IncomeDriver, DriverCurve] = {
    # O PIB de 12 meses acima de 2% soma 3x ao fator; o empreendedor não tem teto
    IncomeDriver.GDP: DriverCurve(Decimal(3), Decimal("0.02"), Decimal("0.5")),
    IncomeDriver.DOLLAR: DriverCurve(
        Decimal("1.0"), Decimal(0), Decimal("0.5"), Decimal("2.0")
    ),
    IncomeDriver.SELIC: DriverCurve(
        Decimal("4.0"), Decimal("0.12"), Decimal("0.5"), Decimal("2.0")
    ),
    IncomeDriver.STOCKS: DriverCurve(
        Decimal("1.5"), Decimal("0.12"), Decimal("0.4"), Decimal("2.0")
    ),
}


@dataclass(frozen=True)
class CareerCurve:
    """
    A carreira de quem começa por baixo: o múltiplo da profissão sobe em linha reta até
    `final_multiple` em `years` anos de partida, e o peso da demissão cai de `layoff_weight`
    até 1 no mesmo prazo. O peso multiplica a chance de demissão da sala.
    """

    final_multiple: Decimal
    years: int
    layoff_weight: Decimal

    def progress(self, elapsed_days: int) -> Decimal:
        """A fração da carreira percorrida, de 0 a 1."""
        done = Decimal(max(elapsed_days, 0)) / (DAYS_PER_YEAR * self.years)
        return min(done, Decimal(1))


@dataclass(frozen=True)
class ProfessionRule:
    # A renda do mês exposta ao sorteio da demissão, em múltiplos do salário do host
    income_multiple: Decimal
    tax: TaxBase
    # O que a demissão sorteada faz com ela; nulo quando a profissão ignora o sorteio
    loss: IncomeLoss | None = None
    real_raise: RealRaise = RealRaise.NONE
    # A variável que oscila a renda, pela curva dela em `DRIVER_CURVES`
    driver: IncomeDriver | None = None
    # A renda sobe pelo IPCA no aniversário; falso é a renda que a inflação corrói
    inflation_indexed: bool = True
    # A renda que sobe com a carreira e a demissão que pesa mais no começo
    career: CareerCurve | None = None
    starting_capital: StartingCapital = StartingCapital.ROOM
    # A profissão só existe na sala que corrige a renda e a despesa pela inflação
    requires_inflation_adjusted: bool = False
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
        driver=IncomeDriver.GDP,
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
        income_multiple=Decimal("1.1"),
        tax=TaxBase.PERSONAL,
        loss=IncomeLoss.VACANCY,
    ),
    Profession.EXPORTER: ProfessionRule(
        income_multiple=Decimal("1.05"),
        tax=TaxBase.CORPORATE,
        driver=IncomeDriver.DOLLAR,
    ),
    Profession.BANKER: ProfessionRule(
        income_multiple=Decimal("1.1"),
        tax=TaxBase.PERSONAL,
        loss=IncomeLoss.LAYOFF,
        driver=IncomeDriver.SELIC,
    ),
    Profession.FREELANCER: ProfessionRule(
        income_multiple=Decimal("1.4"),
        tax=TaxBase.PERSONAL,
        loss=IncomeLoss.NO_CLIENTS,
        inflation_indexed=False,
        requires_inflation_adjusted=True,
    ),
    Profession.BROKER: ProfessionRule(
        income_multiple=Decimal("1.05"),
        tax=TaxBase.PERSONAL,
        driver=IncomeDriver.STOCKS,
    ),
    Profession.HEIR: ProfessionRule(
        income_multiple=Decimal(0),
        tax=TaxBase.PERSONAL,
        starting_capital=StartingCapital.ROOM_PLUS_INHERITANCE,
    ),
    Profession.NEW_GRADUATE: ProfessionRule(
        income_multiple=Decimal("0.6"),
        tax=TaxBase.PERSONAL,
        loss=IncomeLoss.LAYOFF,
        real_raise=RealRaise.GDP_SHARE,
        career=CareerCurve(Decimal("1.5"), years=10, layoff_weight=Decimal(2)),
        starting_capital=StartingCapital.ZERO,
    ),
}

# O imprevisto cujo valor a saúde de cada profissão multiplica
HEALTH_EVENT_KEY = "HEALTH"


def driver_factor(curve: DriverCurve, value: Decimal) -> Decimal:
    """O quanto a variável move a renda: 1 no valor neutro, limitado pelo piso e pelo teto da curva."""
    factor = max(1 + curve.sensitivity * (value - curve.neutral), curve.floor)
    return factor if curve.ceiling is None else min(factor, curve.ceiling)


def available_professions(inflation_adjusted: bool) -> list[Profession]:
    """As profissões que a sala pode escolher: as que exigem a correção pela inflação somem sem ela."""
    return [
        profession
        for profession, rule in PROFESSIONS.items()
        if inflation_adjusted or not rule.requires_inflation_adjusted
    ]
