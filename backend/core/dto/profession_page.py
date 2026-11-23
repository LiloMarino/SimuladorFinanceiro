"""O que a página Profissão lê: o cabeçalho, os indicadores que mexem na renda e o bloco da mecânica."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field

from backend.core.dto.base import BaseDTO
from backend.core.dto.credit import PayrollLoanDTO
from backend.core.enum import (
    IncomeLoss,
    IncomeSeriesEffect,
    IncomeSeriesKey,
    MechanicStatus,
    Profession,
)
from backend.core.professions import RealRaise


class IncomeHeaderDTO(BaseDTO):
    """Os quatro números do topo da página."""

    # A renda do mês depois do imposto e a parte dela que vem da mecânica (a hora extra do CLT)
    income: Decimal
    mechanic_income: Decimal
    # O reajuste acima do IPCA do próximo aniversário e de onde ele vem; nulo na profissão sem reajuste real
    real_raise: Decimal | None
    real_raise_source: RealRaise
    # Falso quando a renda não sobe pelo IPCA (a sala sem correção ou a profissão fixa)
    inflation_indexed: bool
    # O que o sorteio tira da renda e quantas vezes a chance dele pesa para a profissão; nulos quando ela ignora o sorteio
    income_loss: IncomeLoss | None
    layoff_factor: Decimal | None
    unemployment: Decimal
    neutral_unemployment: Decimal
    # Quantas vezes o imprevisto de saúde pesa e quanto dele vem da mecânica
    health_multiple: Decimal
    health_multiple_base: Decimal


class IncomeSeriesPointDTO(BaseDTO):
    month: date
    value: Decimal


class SeriesGuideDTO(BaseDTO):
    """Uma linha de referência do gráfico, além do ponto neutro."""

    value: Decimal
    # O que a linha marca: a hora extra só existe a partir dela
    overtime: bool


class LeverChangeDTO(BaseDTO):
    """Uma mudança recente da alavanca do governo."""

    change_date: date
    before: Decimal
    after: Decimal
    # Quem propôs a medida que mudou o valor e o partido dele; nulos quando o autor não é recuperável
    proposer_name: str | None
    proposer_party: str | None


class IncomeSeriesDTO(BaseDTO):
    key: IncomeSeriesKey
    # O valor de hoje, o ponto neutro da curva e os 12 meses até hoje (vazio na alavanca)
    current: Decimal
    neutral: Decimal | None
    points: list[IncomeSeriesPointDTO]
    guides: list[SeriesGuideDTO]
    # O efeito do valor de hoje na renda e o que ele é (reajuste, múltiplo da renda, peso da demissão)
    effect: Decimal | None
    effect_kind: IncomeSeriesEffect
    # As mudanças da alavanca do governo, da mais recente à mais antiga; vazio no gráfico
    changes: list[LeverChangeDTO]
    # Verdadeiro na alavanca decidida pelo governo da sala
    lever: bool


class CltMechanicDTO(BaseDTO):
    """FGTS e hora extra do CLT."""

    kind: Literal["clt"] = "clt"
    status: MechanicStatus
    fgts_balance: Decimal
    # O depósito do mês (8% do bruto), a TR de hoje ao ano e o que o saldo rende ao ano
    fgts_deposit: Decimal
    tr: Decimal
    fgts_yield: Decimal
    # Saldo mais a multa de 40%, o que cai no caixa na demissão
    layoff_payout: Decimal
    overtime: bool
    # A fração da renda que a hora extra soma ao salário
    overtime_rate: Decimal
    # O que a hora extra soma à renda por mês, ligada ou não
    overtime_income: Decimal
    # O PIB de 12 meses e se ele deixa a hora extra existir
    growth: Decimal
    overtime_offered: bool
    # A recessão desligou a hora extra e ela ainda não voltou a ser possível
    overtime_waiting: bool


class ExchangeLockOptionDTO(BaseDTO):
    """Uma opção de prazo da trava, com o dólar que ela garante hoje."""

    months: int
    locked_dollar: Decimal


class ExchangeLockDTO(BaseDTO):
    """A trava de câmbio em vigor e o que ela rendeu até agora."""

    locked_dollar: Decimal
    # A fração da receita exportada que ela cobre e o prazo contratado
    share: Decimal
    months: int
    paid_months: int
    expires_on: date
    # O dólar travado menos o dólar de hoje: positivo quando a trava paga mais por dólar
    dollar_gap: Decimal
    # Soma, mês a mês desde a contratação, da renda da parte travada menos a que o dólar do mês daria
    gain: Decimal


class ExporterMechanicDTO(BaseDTO):
    """Trava de câmbio e mix de exportação do Exportador."""

    kind: Literal["exporter"] = "exporter"
    status: MechanicStatus
    # O dólar de hoje em reais, a variação dele em 12 meses e o PIB de 12 meses
    dollar: Decimal
    dollar_change: Decimal
    growth: Decimal
    # A fração da renda que é exportada e os fatores da renda: da parte exportada (com a trava), da vendida no Brasil e das duas juntas
    export_share: Decimal
    exported_factor: Decimal
    domestic_factor: Decimal
    mix_factor: Decimal
    # Quanto da renda bruta do mês vem da exportação, a base da fração que a trava cobre
    exported_revenue: Decimal
    # O mix muda uma vez por trimestre: se pode agora e quando libera de novo (nulo antes da primeira mudança)
    can_change_mix: bool
    next_mix_change: date | None
    lock_options: list[ExchangeLockOptionDTO]
    lock: ExchangeLockDTO | None


class PriceRowDTO(BaseDTO):
    """Uma linha da tabela de preços: o que um preço renderia no mês."""

    price: Decimal
    # O preço sobre a referência do dia, menos 1 (0 é a própria referência)
    deviation: Decimal
    clients: Decimal
    income: Decimal
    # A chance do mês sem clientes que o sorteio usa neste preço, com o desemprego do dia
    empty_month_chance: Decimal


class FreelancerMechanicDTO(BaseDTO):
    """Tabela de preços do Autônomo."""

    kind: Literal["freelancer"] = "freelancer"
    status: MechanicStatus
    # O preço por atendimento, desde quando vale e o preço sobre a referência do dia, menos 1
    price: Decimal
    price_since: date
    deviation: Decimal
    # A referência do mercado de hoje e quanto ela subiu desde o último ajuste do preço
    reference: Decimal
    reference_rise: Decimal
    # Os clientes do mês e a renda do mês, preço vezes clientes
    clients: Decimal
    month_income: Decimal
    # A frase que compara o desemprego de hoje com o neutro
    unemployment_note: str
    # A faixa que o novo preço aceita
    min_price: Decimal
    max_price: Decimal
    # O preço muda uma vez por mês: se pode agora e quando libera de novo (nulo antes do primeiro ajuste)
    can_change_price: bool
    next_price_change: date | None
    # Meses desde o último ajuste (ou o início) e se o preço ficou atrás da referência a ponto de avisar
    stalled_months: int
    stale: bool
    rows: list[PriceRowDTO]


class PublicServantMechanicDTO(BaseDTO):
    """Consignado do Servidor."""

    kind: Literal["public_servant"] = "public_servant"
    status: MechanicStatus
    net_salary: Decimal
    margin: Decimal
    margin_used: Decimal
    margin_free: Decimal
    # O juro de hoje ao ano e a SELIC de que ele parte
    annual_rate: Decimal
    selic: Decimal
    loans: list[PayrollLoanDTO]
    # Quando a margem volta a abrir: a data da última parcela do consignado que termina primeiro
    next_release: date | None
    # A parcela mensal que essa data libera da margem
    next_release_amount: Decimal | None


class HouseCdbDTO(BaseDTO):
    years: int
    annual_rate: Decimal
    # O prefixado do Tesouro do mesmo prazo, que o CDB da casa supera em um ponto
    treasury_rate: Decimal
    cap: Decimal
    applied: Decimal
    # Quanto o capital aplicado vale hoje, com o juro já corrido
    current_value: Decimal
    maturity_date: date


class BankerMechanicDTO(BaseDTO):
    """CDB da casa do Bancário."""

    kind: Literal["banker"] = "banker"
    status: MechanicStatus
    cdbs: list[HouseCdbDTO]


class HeirMechanicDTO(BaseDTO):
    """A herança do Herdeiro."""

    kind: Literal["heir"] = "heir"
    inheritance: Decimal
    received_on: date
    annual_expense: Decimal
    # Quantos anos de despesa a herança cobre
    covered_years: Decimal


class AppointeeMechanicDTO(BaseDTO):
    """O partido do Comissionado."""

    kind: Literal["appointee"] = "appointee"
    party: str | None
    in_government: bool
    # Quantas vezes o salário a renda rende hoje, com o partido no governo e fora dele
    multiple_now: Decimal
    multiple_in_government: Decimal
    multiple_outside: Decimal
    # Meses até a votação da próxima eleição; nulo sem governo na sala
    election_in_months: int | None


class OffersBankerMechanicDTO(BaseDTO):
    """As comissões do Banqueiro de ofertas."""

    kind: Literal["offers_banker"] = "offers_banker"
    month_commission: Decimal
    month_offers: int
    total_commission: Decimal
    total_offers: int


class NoMechanicDTO(BaseDTO):
    """A profissão sem mecânica a ligar, ou com mecânica ainda sem motor."""

    kind: Literal["none"] = "none"


MechanicBlockDTO = Annotated[
    CltMechanicDTO
    | ExporterMechanicDTO
    | FreelancerMechanicDTO
    | PublicServantMechanicDTO
    | BankerMechanicDTO
    | HeirMechanicDTO
    | AppointeeMechanicDTO
    | OffersBankerMechanicDTO
    | NoMechanicDTO,
    Field(discriminator="kind"),
]


class ProfessionPageDTO(BaseDTO):
    profession: Profession
    header: IncomeHeaderDTO
    series: list[IncomeSeriesDTO]
    mechanic: MechanicBlockDTO
