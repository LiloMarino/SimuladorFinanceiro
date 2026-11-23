"""O que a página Profissão lê: o cabeçalho, os indicadores que mexem na renda e o bloco da mecânica."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field

from backend.core.dto.base import BaseDTO
from backend.core.dto.credit import PayrollLoanDTO
from backend.core.dto.house_report import HouseRecommendationDTO
from backend.core.enum import (
    AcademicStep,
    IncomeLoss,
    IncomeSeriesEffect,
    IncomeSeriesKey,
    MechanicStatus,
    Profession,
    PropertySize,
    PropertyStatus,
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


class CapitalSaleOptionDTO(BaseDTO):
    """Uma fração do capital que a venda aceita e o que ela rende hoje."""

    share: Decimal
    # A parte do capital que sai da empresa e o que entra no caixa dela, com o desconto da venda
    part: Decimal
    proceeds: Decimal


class EntrepreneurMechanicDTO(BaseDTO):
    """Reinvestimento do Empreendedor."""

    kind: Literal["entrepreneur"] = "entrepreneur"
    status: MechanicStatus
    # O capital da empresa e o de 3 meses atrás (nulo antes do terceiro pagamento)
    capital: Decimal
    capital_months_ago: Decimal | None
    # O rendimento do capital no mês, com sinal, a taxa ao mês e o PIB de 12 meses de que ela sai
    income: Decimal
    rate: Decimal
    growth: Decimal
    # O lucro do mês, a fração salva e quanto dele volta para a empresa com ela
    profit: Decimal
    reinvest_share: Decimal
    reinvested: Decimal
    # PIB de 12 meses negativo e há quantos trimestres seguidos o PIB fecha negativo
    recession: bool
    negative_quarters: int
    sale_options: list[CapitalSaleOptionDTO]


class RedeemBracketDTO(BaseDTO):
    """Uma faixa da tabela do IR regressivo do resgate."""

    label: str
    rate: Decimal
    # Verdadeiro na faixa que o tempo no plano alcança hoje
    current: bool


class RetireeMechanicDTO(BaseDTO):
    """Previdência do Aposentado."""

    kind: Literal["retiree"] = "retiree"
    status: MechanicStatus
    balance: Decimal
    # A taxa anual do plano (CDI menos 1%) e o CDI de que ela sai
    annual_rate: Decimal
    cdi: Decimal
    # A renda vitalícia já convertida no mês, o valor que virou renda e o juro real médio dele (nulo sem conversão)
    converted_income: Decimal
    converted_amount: Decimal
    converted_real_rate: Decimal | None
    # O juro real de hoje, a SELIC e o IPCA esperado de que ele sai, e se o IPCA esperado é o do Focus (senão, o realizado em 12 meses)
    real_rate: Decimal
    selic: Decimal
    expected_ipca: Decimal
    expected_ipca_from_focus: bool
    # A fração do valor convertido que vira renda por mês com o juro real de hoje
    income_rate: Decimal
    # A sala corrige a renda convertida pelo IPCA
    inflation_indexed: bool
    # O IR do resgate de hoje e o tempo no plano, em meses completos
    redeem_rate: Decimal
    months_in_plan: int
    # A faixa seguinte: a alíquota, em quantos meses chega e o mês em que passa a valer; nulos na última faixa
    next_rate: Decimal | None
    next_rate_months: int | None
    next_rate_on: date | None
    brackets: list[RedeemBracketDTO]


class WelfareMechanicDTO(BaseDTO):
    """Pé-de-Meia, tarifa social e curso técnico do Auxílio."""

    kind: Literal["welfare"] = "welfare"
    status: MechanicStatus
    # O saldo do Pé-de-Meia, a próxima data de liberação e se o caixa ficou negativo no período (a liberação então pula)
    balance: Decimal
    next_release_on: date
    cash_was_negative: bool
    # O depósito que o mês rende hoje, a sobra de que ele sai, a fração da sobra que o governo deposita e o teto, ambos já com o fator do gasto do governo com auxílio
    deposit: Decimal
    surplus: Decimal
    deposit_rate: Decimal
    deposit_cap: Decimal
    deposit_factor: Decimal
    # A despesa cheia, a paga com a tarifa social e o desconto mensal
    full_expense: Decimal
    paid_expense: Decimal
    discount: Decimal
    # A renda do bico sem o curso e com ele, e o salário líquido que o CLT paga
    gig_income: Decimal
    gig_income_in_course: Decimal
    clt_salary: Decimal
    # O curso em andamento: quantos meses passaram, quantos ele dura e o mês em que conclui; nulos sem matrícula
    in_course: bool
    course_months: int
    course_months_done: int | None
    course_ends_on: date | None


class GraduateStepDTO(BaseDTO):
    """Uma linha da escada acadêmica do Recém-formado."""

    step: AcademicStep
    # Concluído, em curso, o próximo a se matricular ou um mais adiante
    status: Literal["done", "current", "next", "later"]
    # A duração em meses (zero na graduação) e quantos já passaram; nulo fora do degrau em curso
    months: int
    months_done: int | None
    # O mês em que concluiu (degrau concluído) ou em que conclui (degrau em curso)
    concluded_on: date | None
    ends_on: date | None
    # O múltiplo do fim da carreira que o degrau leva
    final_multiple: Decimal
    # A mensalidade (especialização) ou a bolsa no lugar do salário (mestrado e doutorado) por mês; nulos no degrau concluído
    tuition: Decimal | None
    stipend: Decimal | None
    # Se a mensalidade ou a bolsa já traz o desconto do desemprego: a da matrícula no degrau em curso, a de hoje nos demais
    unemployment_discount: bool


class GraduateMechanicDTO(BaseDTO):
    """Escada acadêmica e casa dos pais do Recém-formado."""

    kind: Literal["graduate"] = "graduate"
    status: MechanicStatus
    # O salário líquido da curva de carreira hoje, a bolsa do mês no mestrado e no doutorado (nula fora deles) e o ano da carreira
    salary: Decimal
    stipend_income: Decimal | None
    career_year: int
    # O múltiplo do fim da carreira em vigor e o que o próximo degrau leva; nulo no topo da escada
    final_multiple: Decimal
    next_final_multiple: Decimal | None
    next_step: AcademicStep | None
    steps: list[GraduateStepDTO]
    # Quando o degrau seguinte abre (a conclusão do em curso) e quantos meses faltam; nulos sem degrau em curso
    next_opens_on: date | None
    months_left: int | None
    # O desemprego de hoje, o neutro, se hoje ele está acima (a matrícula de hoje teria desconto) e os percentuais do desconto
    unemployment: Decimal
    neutral_unemployment: Decimal
    unemployment_discount: bool
    tuition_discount_rate: Decimal
    stipend_bonus_rate: Decimal
    # A casa dos pais: com eles, já saiu ou o prazo acabou
    home: Literal["with_parents", "left", "expired"]
    home_discount_rate: Decimal
    # O desconto mensal em reais enquanto mora com os pais (zero depois), até quando vale e a despesa cheia que volta
    home_discount: Decimal
    home_until: date
    full_expense: Decimal


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


class HouseReportDTO(BaseDTO):
    """O relatório de um mês: o dia em que saiu e as recomendações, na ordem em que a casa as deu."""

    month: date
    issued_on: date
    items: list[HouseRecommendationDTO]


class BrokerMechanicDTO(BaseDTO):
    """O relatório da casa, o placar e a comissão do Corretor."""

    kind: Literal["broker"] = "broker"
    status: MechanicStatus
    # O relatório vigente e o anterior; o vigente é nulo antes do primeiro, e o anterior até haver dois
    current: HouseReportDTO | None
    previous: HouseReportDTO | None
    # O dia em que o próximo relatório sai
    next_report_on: date
    # Quantas recomendações da partida inteira acertaram, quantas já têm desfecho e a fração que acertou (nula sem desfecho)
    hits: int
    resolved: int
    hit_rate: Decimal | None
    # A renda líquida do mês, a parte fixa e a comissão dela
    income: Decimal
    fixed_income: Decimal
    commission: Decimal
    # A fração do volume que vira comissão, o volume da sala no mês que fechou, quantos Corretores o dividem e se o teto cortou a comissão
    commission_rate: Decimal
    volume: Decimal
    brokers: int
    capped: bool


class LandlordPropertyDTO(BaseDTO):
    """Um imóvel do Locador na tabela da página."""

    id: int
    name: str
    size: PropertySize
    # O valor de hoje, pelo IVG-R
    value: Decimal
    status: PropertyStatus
    # O aluguel em vigor e o dia do próximo reajuste pelo IGP-M; nulos no imóvel vago
    rent: Decimal | None
    next_readjustment: date | None
    # Há quantos meses está vago e o aluguel com que volta (0,5% do valor de hoje); nulos fora da vacância
    vacant_months: int | None
    rerent: Decimal | None
    # O dia em que a venda pedida conclui; nulo fora da venda
    sale_due: date | None


class PropertyOfferDTO(BaseDTO):
    """A oferta do mês para um tamanho de imóvel."""

    size: PropertySize
    price: Decimal
    # O aluguel inicial e o custo de compra (ITBI e corretagem)
    rent: Decimal
    cost: Decimal
    # Verdadeiro quando o jogador já comprou esta oferta
    bought: bool


class LandlordMechanicDTO(BaseDTO):
    """Os imóveis, o rendimento e as ofertas do mês do Locador."""

    kind: Literal["landlord"] = "landlord"
    status: MechanicStatus
    # A soma dos aluguéis do mês e quantos imóveis estão alugados, entre quantos o jogador tem
    income: Decimal
    rented: int
    total: int
    # O rendimento do aluguel em 12 meses sobre o valor dos imóveis, com os vagos fora e com todos alugados; nulos sem imóvel
    annual_yield: Decimal | None
    full_yield: Decimal | None
    # O CDI ao ano, que o rendimento do imóvel concorre
    cdi: Decimal
    # A chance de vacância por imóvel no mês
    vacancy_chance: Decimal
    properties: list[LandlordPropertyDTO]
    total_value: Decimal
    # O mês das ofertas, o dia em que as próximas saem e as 3 ofertas, uma de cada tamanho
    offers_month: date
    next_offers_on: date
    offers: list[PropertyOfferDTO]
    # O aluguel inicial como fração do preço ao mês e o custo de compra e de venda como fração do preço
    rent_rate: Decimal
    cost_rate: Decimal
    # Em quantos meses a venda pedida conclui
    sale_months: int


class NoMechanicDTO(BaseDTO):
    """A profissão sem mecânica a ligar, ou com mecânica ainda sem motor."""

    kind: Literal["none"] = "none"


MechanicBlockDTO = Annotated[
    CltMechanicDTO
    | EntrepreneurMechanicDTO
    | RetireeMechanicDTO
    | WelfareMechanicDTO
    | GraduateMechanicDTO
    | ExporterMechanicDTO
    | FreelancerMechanicDTO
    | PublicServantMechanicDTO
    | BankerMechanicDTO
    | HeirMechanicDTO
    | AppointeeMechanicDTO
    | OffersBankerMechanicDTO
    | BrokerMechanicDTO
    | LandlordMechanicDTO
    | NoMechanicDTO,
    Field(discriminator="kind"),
]


class ProfessionPageDTO(BaseDTO):
    profession: Profession
    header: IncomeHeaderDTO
    series: list[IncomeSeriesDTO]
    mechanic: MechanicBlockDTO
