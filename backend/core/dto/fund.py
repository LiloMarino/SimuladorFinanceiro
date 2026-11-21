from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field, StringConstraints

from backend.core.dto.base import BaseDTO
from backend.core.enum import (
    FundAssemblyAgenda,
    FundAssemblyStatus,
    FundComanagerStatus,
    FundDirectedIssuanceStatus,
)

# Quatro letras e o 11 das cotas
FUND_TICKER_PATTERN = r"^[A-Z]{4}11$"
FundTicker = Annotated[str, StringConstraints(pattern=FUND_TICKER_PATTERN)]
FundName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=3, max_length=40)
]
# Taxa ao ano em fração: 0,02 é 2%
FeeRate = Annotated[Decimal, Field(ge=0, le=1, decimal_places=4)]
# Parte do lucro realizado que vira rendimento, em fração: 0,95 é 95%
DistributionRate = Annotated[Decimal, Field(ge=0, le=1, decimal_places=4)]
# A parte das taxas de um co-gestor: 0,30 é 30%; o principal fica com o que sobra
ComanagerShare = Annotated[Decimal, Field(gt=0, lt=1, decimal_places=4)]
DEFAULT_DISTRIBUTION_RATE = Decimal("0.95")


class FundTermsDTO(BaseDTO):
    """O que a gestora mostra a quem a vê: cotas, oferta, taxas e marca d'água."""

    id: int
    ticker: str
    founder_user_id: int
    manager_user_id: int
    name: str
    quotas: Decimal
    maker_quotas: Decimal
    offer_remaining: Decimal | None
    listed_on: date | None
    # As cotas postas à venda e o preço da oferta, fixados na abertura
    offer_quotas: Decimal | None
    offer_price: Decimal | None
    # O dia em que a oferta fechou; nulo com a oferta aberta ou sem oferta
    offer_closed_on: date | None
    management_fee: Decimal
    performance_fee: Decimal
    pending_management_fee: Decimal | None
    pending_performance_fee: Decimal | None
    pending_from: date | None
    high_water_mark: Decimal | None
    high_water_mark_on: date | None
    last_performance_on: date | None
    # A parte do lucro realizado que vira rendimento aos cotistas e a troca pedida (vale em `pending_from`)
    distribution_rate: Decimal = DEFAULT_DISTRIBUTION_RATE
    pending_distribution_rate: Decimal | None = None
    # O dia em que o gestor de hoje assumiu a gestora; nulo nas gestoras antigas que nunca listaram
    manager_since: date | None = None
    # O gestor que passou a gestão ao herdeiro na posse da presidência e retoma no fim do
    # mandato; nulo sem gestor em licença
    leave_manager_user_id: int | None = None


class FundDTO(FundTermsDTO):
    """Uma gestora da partida, como a linha de `funds` a guarda."""

    stock_id: int
    portfolio_id: int
    client_id: uuid.UUID
    maker_cash: Decimal
    # A parte nas taxas que o herdeiro tinha como co-gestor antes de virar principal; volta com
    # o gestor em licença. Nula sem gestor em licença
    leave_heir_share: Decimal | None = None
    # O dia em que a oferta automática do modo aquisição hostil abriu; nulo sem ela
    takeover_offer_on: date | None = None
    # A gestora que incorporou esta e o dia da fusão; nulos enquanto ela existe por si
    merged_into_fund_id: int | None = None
    merged_on: date | None = None
    # O lucro realizado desde a última data-com, por origem
    month_dividends: Decimal = Decimal(0)
    month_interest: Decimal = Decimal(0)
    month_sales_gain: Decimal = Decimal(0)
    month_fees: Decimal = Decimal(0)
    # A taxa que o caixa não cobriu, por tipo
    management_fee_payable: Decimal = Decimal(0)
    performance_fee_payable: Decimal = Decimal(0)

    @property
    def fee_payable(self) -> Decimal:
        return self.management_fee_payable + self.performance_fee_payable


class FundDistributionDTO(BaseDTO):
    """O rendimento de um mês: o lucro realizado que a data-com apurou e o que foi pago por cota."""

    data_com: date
    realized_profit: Decimal
    rate: Decimal
    # As cotas fora do formador que dividem o rendimento
    quotas: Decimal
    per_quota: Decimal
    # O que foi pago de fato; nulos até o pagamento. Abaixo do apurado quando o caixa não cobriu
    paid_per_quota: Decimal | None
    paid: Decimal | None
    paid_on: date | None


class FundOfferSaleDTO(BaseDTO):
    """Uma venda da oferta pública ou da emissão; sem comprador quando quem levou as cotas não é jogador."""

    day: date
    buyer_user_id: int | None
    quotas: Decimal
    price: Decimal
    # A emissão a que a venda pertence; nulo na oferta pública de abertura
    issuance_id: int | None = None


class FundIssuanceDTO(BaseDTO):
    """Uma emissão de cotas novas, com o preço fixado no anúncio."""

    id: int
    announced_on: date
    quotas: Decimal
    price: Decimal
    # Último dia da preferência dos cotistas e último dia da sobra aberta
    preference_ends_on: date
    ends_on: date
    # Cotas que já nasceram, na preferência e na sobra
    sold: Decimal
    # Nulo com a emissão aberta
    closed_on: date | None
    # O fechamento da cota na sessão anterior ao anúncio; nulo = emissão sem ágio
    book_price: Decimal | None


class FundIssuanceEstimateDTO(BaseDTO):
    """A captação que bots cotistas e o Mercado devem trazer na sobra, entre a opinião mais pessimista e a mais otimista dos bots."""

    # As cotas da sobra que os dois compram nos dois extremos, o dinheiro que entra no caixa da gestora (já sem a comissão) e a comissão dos Banqueiros, que incide só na compra dos bots
    quotas_min: Decimal
    quotas_max: Decimal
    raised_min: Decimal
    raised_max: Decimal
    commission_min: Decimal
    commission_max: Decimal
    # O que move a compra: o desempenho da cota sobre o CDI na janela (0,03 é 3 pontos acima) e o ágio da foto sobre o PL por cota (0,10 é 10%)
    performance: float
    premium: float


class FundIssuanceRightDTO(BaseDTO):
    """O direito de preferência de um jogador, pela proporção que ele tinha no anúncio."""

    user_id: int
    rights: Decimal
    bought: Decimal


type FundBuybackState = Literal["open", "done", "canceled"]


class FundBuybackDTO(BaseDTO):
    """Uma recompra: a ordem de compra da gestora, com o que já foi comprado e pago."""

    id: int
    announced_on: date
    quantity: Decimal
    max_price: Decimal
    bought: Decimal
    paid: Decimal
    state: FundBuybackState


class FundAssemblyDTO(BaseDTO):
    """Uma assembleia de cotistas, como a linha de `fund_assemblies` a guarda."""

    id: int
    agenda: FundAssemblyAgenda
    convener_user_id: int
    # O indicado a gestor; nulo nas pautas que não trocam o gestor
    candidate_user_id: int | None
    # O gestor de quando a assembleia foi convocada
    previous_manager_user_id: int
    status: FundAssemblyStatus
    called_on: date
    # O dia em que a votação abriu; nulo enquanto o convite espera o aliado
    started_on: date | None
    # O último pregão da fase de agora: o do convite ou o da votação
    ends_on: date
    closed_on: date | None
    # O placar do fechamento, em cotas; nulo até a votação fechar
    in_favor_quotas: Decimal | None
    against_quotas: Decimal | None
    abstention_quotas: Decimal | None
    # As taxas da pauta de aumento: as de quando foi proposto e as propostas; nulas nas outras pautas
    previous_management_fee: Decimal | None = None
    previous_performance_fee: Decimal | None = None
    proposed_management_fee: Decimal | None = None
    proposed_performance_fee: Decimal | None = None
    # Na pauta de fusão: a outra gestora e se esta é a incorporada; nulos nas outras pautas
    partner_fund_id: int | None = None
    absorbed: bool = False
    # O que faltou nos caixas quando isso rejeitou a fusão no fechamento; nulo nas demais votações
    merge_shortfall: Decimal | None = None


class FundAssemblyVoteDTO(BaseDTO):
    """O voto de um cotista, que ele muda até o fim da votação."""

    user_id: int
    in_favor: bool
    voted_on: date


class FundDayDTO(BaseDTO):
    """O fechamento de uma gestora num pregão."""

    day: date
    nav: Decimal
    quotas: Decimal
    traded_quantity: Decimal
    traded_value: Decimal
    ranking_price: Decimal
    fee_payable: Decimal = Decimal(0)
    # O saldo devedor dos empréstimos da gestora no fim do pregão
    loan_debt: Decimal = Decimal(0)


class FundSummaryDTO(FundTermsDTO):
    """A gestora na lista da partida, com o PL por cota de agora e o preço de ranking."""

    nav: Decimal | None
    ranking_price: Decimal | None
    # O preço do último negócio da cota; nulo enquanto ela nunca negociou. O ágio é preço / nav - 1
    price: Decimal | None
    manager_nickname: str | None
    # O pregão da oferta pública (1 a 5) e o dia em que ela fecha sozinha; nulos sem oferta aberta
    offer_session: int | None
    offer_ends_on: date | None
    # O último dia do mandato do gestor presidente, em que a gestora fica congelada; nulo se opera
    frozen_until: date | None
    # Uma estratégia opera a carteira da gestora: as boletas dela travam, e na presidência a carteira segue operando
    automatic: bool = False
    # O último dia do mandato do gestor em licença, em que a gestão volta a ele; nulo sem licença
    leave_until: date | None = None


class FundRoomItemDTO(FundSummaryDTO):
    """A gestora na lista da sala, com as cotas e o papel de quem consulta."""

    # Zero quando quem consulta não tem cotas
    my_quotas: Decimal
    # Os apelidos dos co-gestores ativos, na ordem em que entraram
    comanager_nicknames: list[str]
    # Quem consulta é co-gestor ativo desta gestora
    i_comanage: bool


# Quem tem cotas: jogador, bot ou o formador de mercado
type FundHolderKind = Literal["player", "bot", "maker"]
# As classes em que a gestora mantém patrimônio: o Tesouro à parte da renda fixa de crédito
type FundHoldingClass = Literal["cash", "stocks", "fixed_income", "treasury"]
type FundMovementType = Literal[
    "contribution",
    "offer_opened",
    "offer_closed",
    "management_fee",
    "performance_fee",
    "report_published",
    "manager_buy",
    "manager_sell",
    "issuance_opened",
    "issuance_closed",
    "buyback_opened",
    "distribution",
    "comanager_joined",
    "comanager_left",
    "directed_issuance",
    "asset_buy",
    "asset_sell",
    "merger",
]


class FundHolderDTO(BaseDTO):
    kind: FundHolderKind
    # Nulo no formador de mercado
    user_id: int | None
    nickname: str
    color: str | None
    quotas: Decimal
    # Fração das cotas em circulação: 0,25 é 25%
    share: Decimal


class FundCompositionDTO(BaseDTO):
    """O patrimônio da gestora numa classe, hoje."""

    asset_class: FundHoldingClass
    value: Decimal
    # Fração do patrimônio: 0,40 é 40%
    fraction: Decimal


class FundPositionDTO(BaseDTO):
    """Uma posição da gestora: o caixa, uma ação (com quantidade) ou um título de renda fixa."""

    ticker: str | None
    name: str
    asset_class: FundHoldingClass
    quantity: Decimal | None
    value: Decimal
    fraction: Decimal


class FundReportDTO(BaseDTO):
    """O relatório mensal: as posições no último pregão do mês fechado."""

    day: date
    positions: list[FundPositionDTO]
    # A taxa a pagar em aberto no fechamento daquele pregão
    fee_payable: Decimal


class FundSeriesPointDTO(BaseDTO):
    day: date
    # O fechamento do pregão; nulo antes da primeira vela
    close: Decimal | None
    nav: Decimal
    # O preço de ranking do pregão; nulo no dia da oferta, antes do primeiro fechamento
    ranking_price: Decimal | None = None


class FundFeesDTO(BaseDTO):
    management_fee: Decimal
    # O que a administração cobra no próximo mês: taxa anual / 12 x PL por cota x cotas fora do formador
    management_monthly_estimate: Decimal
    performance_fee: Decimal
    # O que a performance cobraria se o semestre fechasse hoje, pela marca d'água; nulo antes da oferta
    performance_estimate: Decimal | None
    next_performance_on: date | None
    high_water_mark: Decimal | None
    high_water_mark_on: date | None
    # O que o gestor recebeu de taxas (administração e performance) nos últimos 12 meses
    received_12m: Decimal
    # A taxa que o caixa não cobriu e a gestora ainda deve ao gestor
    payable: Decimal
    # O saldo devedor dos empréstimos da gestora, à parte da taxa a pagar
    loan_debt: Decimal


class FundDistributionPlanDTO(BaseDTO):
    """O rendimento do mês corrente: a parte distribuída, o lucro realizado até hoje e as datas."""

    rate: Decimal
    pending_rate: Decimal | None
    pending_from: date | None
    # O lucro realizado do mês até hoje, por origem; as taxas entram com sinal de menos
    dividends: Decimal
    interest: Decimal
    sales_gain: Decimal
    fees: Decimal
    realized_profit: Decimal
    # O que o mês distribuiria se fechasse hoje e o valor por cota fora do formador
    projected: Decimal
    projected_per_quota: Decimal
    # O caixa da gestora e se ele cobre o rendimento projetado
    cash: Decimal
    cash_enough: bool
    data_com_on: date
    pay_on: date


class FundMovementDTO(BaseDTO):
    day: date
    type: FundMovementType
    quotas: Decimal | None
    price: Decimal | None
    # Valor em reais do movimento
    amount: Decimal | None
    ticker: str | None
    # Quem entrou ou saiu da gestão (a parte das taxas, de quem entrou) ou quem comprou numa
    # emissão dirigida; nulos nos demais movimentos
    nickname: str | None = None
    share: Decimal | None = None


class FundMonthlyReportDTO(BaseDTO):
    """O relatório de um mês fechado: as posições do último pregão e o mês em números."""

    # O primeiro dia do mês relatado e os meses com relatório publicado, do mais antigo ao mais novo
    month: date
    months: list[date]
    report: FundReportDTO
    # O saldo devedor dos empréstimos da gestora no fechamento do mês
    loan_debt: Decimal
    # O PL por cota no começo e no fim do mês e o CDI do mesmo período
    nav_start: Decimal
    nav_end: Decimal
    cdi_return: Decimal
    # O rendimento apurado na data-com do mês; nulo quando o mês não teve rendimento
    distribution: FundDistributionDTO | None
    # O que a gestora pagou de taxa de administração e de performance no mês
    management_fee_paid: Decimal
    performance_fee_paid: Decimal
    # As operações do mês, da mais antiga à mais nova
    operations: list[FundMovementDTO]


class FundOfferBuyerDTO(BaseDTO):
    """Quem comprou na oferta em andamento; os bots entram somados numa linha só."""

    kind: FundHolderKind
    user_id: int | None
    nickname: str
    color: str | None
    quotas: Decimal


type FundIssuancePhase = Literal["preference", "leftover"]


class FundIssuanceStatusDTO(FundIssuanceDTO):
    """A emissão aberta como quem consulta a vê: a fase de hoje, o que entrou no caixa e o direito dele."""

    phase: FundIssuancePhase
    # Dinheiro que as cotas já nascidas levaram ao caixa da gestora
    raised: Decimal
    # O direito de preferência de quem consulta e o quanto ele já usou; nulos sem direito
    my_rights: Decimal | None
    my_bought: Decimal | None
    # A captação estimada da sobra por bots e Mercado; nula sem sobra a vender ou sem PL por cota
    estimate: FundIssuanceEstimateDTO | None


# O que a gestora vende ao público: a oferta de abertura ou a sobra de uma emissão
type FundOpenOfferKind = Literal["initial", "leftover"]
# O que já encerrou: a oferta de abertura ou uma emissão
type FundClosedOfferKind = Literal["initial", "issuance"]


class FundPreferenceOfferDTO(BaseDTO):
    """A preferência de quem consulta numa emissão aberta: o que ele ainda pode comprar antes do público."""

    fund_id: int
    ticker: str
    name: str
    issuance_quotas: Decimal
    price: Decimal
    # O direito no anúncio, o que falta usar e o que os cotistas já compraram da emissão
    my_rights: Decimal
    my_left: Decimal
    holders_bought: Decimal
    preference_ends_on: date
    # Pregões que restam da preferência, contando hoje, e os da sobra que vêm depois
    sessions_left: int
    leftover_sessions: int


class FundOpenOfferDTO(BaseDTO):
    """Uma venda de cotas novas aberta a qualquer investidor, a preço fixo."""

    fund_id: int
    ticker: str
    name: str
    manager_nickname: str | None
    kind: FundOpenOfferKind
    price: Decimal
    # As cotas postas à venda (da oferta ou da emissão) e o que ainda não foi vendido
    quotas: Decimal
    remaining: Decimal
    # O pregão de hoje na oferta de abertura e quantos pregões ainda restam depois de hoje
    session: int | None
    ends_on: date
    sessions_left: int
    management_fee: Decimal
    performance_fee: Decimal
    # Só na sobra de emissão: até quando valeu a preferência dos cotistas e quanto eles compraram
    preference_ends_on: date | None
    preference_bought: Decimal | None


class FundClosedOfferDTO(BaseDTO):
    """Uma oferta ou emissão que já encerrou, com o preço dela e o da cota no mercado hoje."""

    fund_id: int
    ticker: str
    name: str
    kind: FundClosedOfferKind
    price: Decimal
    quotas: Decimal
    sold: Decimal
    closed_on: date
    # O preço do último negócio da cota; nulo se nunca negociou
    market_price: Decimal | None


class FundOffersDTO(BaseDTO):
    """A página Ofertas públicas como quem consulta a vê."""

    preference: list[FundPreferenceOfferDTO]
    open: list[FundOpenOfferDTO]
    closed: list[FundClosedOfferDTO]


type FundAssemblyStance = Literal["favor", "against", "abstain"]
# "manager_only" é a pauta que só o gestor principal propõe; "no_partner" é a fusão sem outra
# gestora que o mesmo gestor gere, e "busy" a que tem emissão, recompra ou oferta em aberto;
# "frozen" é a gestora congelada pela presidência do gestor, "swap_open" a fusão que espera uma
# troca de gestor em andamento, "merge_open" a troca que espera uma fusão em votação e "team"
# a troca pedida por quem é da equipe de quem gere a gestora, na aquisição hostil em equipes
type FundAssemblyBlock = Literal[
    "share",
    "interval",
    "pending",
    "manager",
    "unlisted",
    "grace",
    "manager_only",
    "no_partner",
    "busy",
    "frozen",
    "swap_open",
    "merge_open",
    "team",
]


class FundAssemblyVoterDTO(BaseDTO):
    """Um cotista jogador no placar: as cotas dele no momento e para onde elas vão."""

    user_id: int
    nickname: str
    color: str | None
    quotas: Decimal
    # Fração das cotas em circulação: 0,25 é 25%
    share: Decimal
    stance: FundAssemblyStance
    is_manager: bool


class FundAssemblyAutoVoteDTO(BaseDTO):
    """O grupo que vota pelo desempenho no aumento de taxa (bots cotistas ou formador de mercado): as cotas e o lado."""

    quotas: Decimal
    # Fração das cotas em circulação: 0,25 é 25%
    share: Decimal
    stance: FundAssemblyStance


class FundAssemblyTallyDTO(BaseDTO):
    """O placar em cotas: a favor, contra e abstenção (quem não votou e, fora do aumento de taxa, bots e formador de mercado)."""

    in_favor: Decimal
    against: Decimal
    abstention: Decimal
    total: Decimal
    # Cotas a favor que faltam para a pauta vencer; zero quando ela já vence (o empate rejeita)
    missing_to_win: Decimal


class FundAssemblyFeeDTO(BaseDTO):
    """As taxas da pauta de aumento: as de quando foi proposto e as propostas, em fração (0,02 é 2%)."""

    management_from: Decimal
    management_to: Decimal
    performance_from: Decimal
    performance_to: Decimal


class FundMergeSideDTO(BaseDTO):
    """Uma das duas gestoras de uma fusão: quem incorpora ou quem é incorporada."""

    fund_id: int
    ticker: str
    name: str
    # O PL por cota de agora; nulo sem cota em circulação
    nav: Decimal | None
    cash: Decimal


class FundAssemblyMergeDTO(BaseDTO):
    """A fusão da votação, vista da gestora que consulta: as duas pontas, a troca de cotas e a saída de quem vota contra."""

    mother: FundMergeSideDTO
    daughter: FundMergeSideDTO
    # Se a gestora que consulta é a que incorpora
    is_mother: bool
    # Cotas da incorporadora por cota da incorporada, pelo PL por cota de agora; nulo sem PL
    ratio: Decimal | None
    # O placar da assembleia da outra gestora
    partner_tally: FundAssemblyTallyDTO
    # Fração das cotas da outra gestora que já votaram (0,52 é 52%) e a favor entre os votos
    partner_voted_share: Decimal
    partner_in_favor_share: Decimal | None
    # A saída de quem vota contra na incorporada: cotas e o que elas valem pelo PL por cota; `shortfall`
    # é o que o caixa e a renda fixa de liquidez diária das duas gestoras somados não cobrem
    exit_quotas: Decimal
    exit_amount: Decimal
    shortfall: Decimal


class FundAssemblyStatusDTO(BaseDTO):
    """A assembleia em andamento como quem consulta a vê."""

    id: int
    agenda: FundAssemblyAgenda
    status: FundAssemblyStatus
    convener_user_id: int
    convener_nickname: str
    candidate_user_id: int | None
    candidate_nickname: str | None
    # As taxas propostas; nulas fora da pauta de aumento
    fee: FundAssemblyFeeDTO | None
    # A fusão; nula fora da pauta de fusão
    merge: FundAssemblyMergeDTO | None = None
    called_on: date
    started_on: date | None
    ends_on: date
    # O pregão da votação ou do convite (1 a 5) e o total de pregões
    session: int
    sessions: int
    # Placar e cotistas de agora; nulos com o convite esperando o aliado
    tally: FundAssemblyTallyDTO | None
    voters: list[FundAssemblyVoterDTO]
    # A parte da abstenção que nunca vota: bots e formador de mercado (fora do aumento de taxa) e quem opera a gestora
    non_voting: Decimal
    # Os bots cotistas e o formador de mercado no aumento de taxa; nulos nas outras pautas
    bots: FundAssemblyAutoVoteDTO | None = None
    market: FundAssemblyAutoVoteDTO | None = None
    # O voto de quem consulta: a favor, contra, ou nulo se ainda não votou
    my_vote: bool | None
    # Se quem consulta pode votar agora (tem cota, não é o gestor)
    can_vote: bool


class FundAssemblyResultDTO(BaseDTO):
    """O resultado de uma votação concluída."""

    id: int
    agenda: FundAssemblyAgenda
    status: FundAssemblyStatus
    convener_nickname: str
    candidate_nickname: str | None
    previous_manager_nickname: str
    started_on: date
    closed_on: date
    tally: FundAssemblyTallyDTO
    # As taxas da pauta de aumento e o dia em que a aprovada passa a valer
    fee: FundAssemblyFeeDTO | None
    effective_on: date | None
    # Na pauta de fusão, a outra gestora e se esta foi a incorporada
    partner_ticker: str | None = None
    partner_name: str | None = None
    absorbed: bool = False
    # O que faltou nos caixas quando isso rejeitou a fusão; nulo quando a votação decidiu
    merge_shortfall: Decimal | None = None


class FundAssemblyOptionDTO(BaseDTO):
    """Uma pauta que a assembleia aceita e se quem consulta pode pô-la em votação agora."""

    agenda: FundAssemblyAgenda
    can_convene: bool
    # Por que quem consulta não pode convocar; nulo quando pode
    block: FundAssemblyBlock | None
    # Quando a pauta aceita nova votação, se o intervalo é o que bloqueia
    next_allowed_on: date | None


class FundAssemblyPanelDTO(BaseDTO):
    """A seção Assembleia da página da gestora: as votações em andamento (uma por pauta), o histórico e as pautas que quem consulta pode convocar."""

    current: list[FundAssemblyStatusDTO]
    # As votações concluídas pelo voto, da mais nova à mais antiga
    history: list[FundAssemblyResultDTO]
    options: list[FundAssemblyOptionDTO]
    # As gestoras com que quem consulta pode propor a fusão desta; vazia sem nenhuma
    merge_partners: list[FundMergeSideDTO]
    # Cotas mínimas para convocar (10% das em circulação) e as de quem consulta
    convene_quotas: Decimal
    my_quotas: Decimal
    # Até quando quem consulta, afastado de uma gestora, não pode fundar outra
    blocked_founding_until: date | None


class FundComanagerDTO(BaseDTO):
    """Um co-gestor como a linha de `fund_comanagers` o guarda."""

    user_id: int
    status: FundComanagerStatus
    # A parte das taxas em vigor, como fração (0,30 é 30%); zero enquanto o convite espera
    share: Decimal
    # A parte agendada e o dia em que passa a valer
    pending_share: Decimal | None
    pending_from: date | None
    invited_on: date
    # O dia em que aceitou; nulo enquanto o convite espera
    since: date | None

    @property
    def future_share(self) -> Decimal:
        """A parte que vale daqui em diante: a agendada, se houver, senão a de hoje."""
        return self.share if self.pending_share is None else self.pending_share


class FundComanagerEventDTO(BaseDTO):
    """A entrada (`joined`) ou a saída (`left`) de um co-gestor, no dia em que aconteceu."""

    user_id: int
    kind: Literal["joined", "left"]
    day: date
    share: Decimal | None


class FundDirectedIssuanceDTO(BaseDTO):
    """Uma emissão dirigida como a linha de `fund_directed_issuances` a guarda."""

    id: int
    buyer_user_id: int
    # As cotas da oferta; o preço só nasce na liquidação
    quotas: Decimal
    offered_on: date
    status: FundDirectedIssuanceStatus
    price: Decimal | None
    settled_on: date | None


class FundDirectedIssuanceViewDTO(FundDirectedIssuanceDTO):
    """A oferta de cotas novas na página da gestora, com quem compra e até quando ela vale."""

    buyer_nickname: str
    expires_on: date


class FundComanagerViewDTO(FundComanagerDTO):
    """O co-gestor na página da gestora, com quem ele é e até quando o convite vale."""

    nickname: str
    color: str | None
    # O último dia do convite pendente; nulo no co-gestor ativo
    expires_on: date | None


# O papel de quem consulta a gestora: gestor principal, co-gestor ou só cotista/visitante
type FundRole = Literal["manager", "comanager", "viewer"]


class FundIssuanceRulesDTO(BaseDTO):
    """As regras da emissão de cotas que o front explica: a janela de cada fase e como o bot valora a cota."""

    # Pregões da preferência dos cotistas, contando o do anúncio
    preference_sessions: int
    # Pregões da sobra aberta a todos, depois da preferência
    leftover_sessions: int
    # Quanto o prêmio do desempenho sobre o CDI soma ou tira, no máximo, do PL por cota na valoração do bot (fração: 0,20 é 20%)
    bot_premium_limit: float
    # Quanto a opinião do dia de cada bot varia o valor da cota, para cima ou para baixo (fração: 0,05 é 5%)
    bot_opinion_range: float


class FundDetailsDTO(FundSummaryDTO):
    """A página da gestora: quem tem as cotas, a carteira, o desempenho, as taxas e a oferta."""

    holders: list[FundHolderDTO]
    # Cotas que dão o controle: mais da metade das cotas em circulação
    control_quotas: Decimal
    # Quanto o gestor vende sem perder o controle; só o gestor vê
    sellable_keeping_control: Decimal | None
    composition: list[FundCompositionDTO]
    # Rentabilidade do PL por cota nos últimos 12 meses e o CDI do mesmo período (0,10 é 10%);
    # numa gestora mais nova que isso valem desde `return_since`
    return_12m: Decimal | None
    return_since: date | None
    cdi_12m: Decimal | None
    series: list[FundSeriesPointDTO]
    last_report: FundReportDTO | None
    fees: FundFeesDTO
    # O rendimento do mês corrente e o histórico dos meses, do mais novo ao mais antigo
    distribution: FundDistributionPlanDTO
    distributions: list[FundDistributionDTO]
    # Retorno total do PL por cota nos últimos 12 meses: a variação da cota mais o que foi pago
    # de rendimento (0,10 é 10%); vale desde `return_since` numa gestora mais nova
    total_return_12m: Decimal | None
    # Os movimentos mais novos primeiro
    movements: list[FundMovementDTO]
    # A oferta em andamento: cotas vendidas, o que entrou no caixa e quem comprou; nulos sem oferta aberta
    offer_sold: Decimal | None
    offer_raised: Decimal | None
    offer_buyers: list[FundOfferBuyerDTO] | None
    # Quantos compradores a oferta pública teve (bots e formador contam um a um); nulo sem oferta
    offer_buyers_count: int | None = None
    # A emissão e a recompra em aberto; nulas quando a gestora não tem
    issuance: FundIssuanceStatusDTO | None
    # As regras da emissão valem com ou sem emissão aberta: o diálogo de anunciar também as explica
    issuance_rules: FundIssuanceRulesDTO
    buyback: FundBuybackDTO | None
    # A troca de gestor pela assembleia dos cotistas
    assembly: FundAssemblyPanelDTO
    # A carteira posição a posição, ao vivo; só o gestor vê
    positions: list[FundPositionDTO] | None
    # As cotas de quem consulta, ao preço de ranking (o do patrimônio no ranking), e o retorno
    # sobre o custo médio dele; nulo sem cotas
    my_quotas: Decimal
    my_value: Decimal
    my_return: Decimal | None
    # Os co-gestores (ativos e convites pendentes), a parte das taxas do principal (o que sobra
    # das partes dos co-gestores) e o papel de quem consulta, com a parte dele quando co-gestor
    comanagers: list[FundComanagerViewDTO]
    manager_share: Decimal
    my_role: FundRole
    my_share: Decimal | None
    # A oferta de cotas novas que espera resposta; só o principal e o comprador a veem
    directed_issuance: FundDirectedIssuanceViewDTO | None


class FundAccountDTO(BaseDTO):
    """Uma conta com que o jogador opera: a pessoal (sem gestora), uma gestora que ele gere ou, ao presidente, o Fundo Soberano."""

    # O id da gestora; o Fundo Soberano tem o id 0, que nenhuma gestora usa
    fund_id: int | None
    name: str
    ticker: str | None
    cash: Decimal
    # O último dia em que a carteira desta conta fica sem operar; nulo se opera
    frozen_until: date | None
    # Uma estratégia opera a carteira da gestora: as boletas dela travam
    automatic: bool = False
    # O dia em que o jogador perdeu a assembleia da própria gestora e passou a só assistir;
    # nulo nas gestoras e para quem segue na partida
    eliminated_on: date | None = None
    # O papel do jogador na conta; nulo na conta pessoal
    role: Literal["manager", "comanager", "president"] | None


class FundTickerCheckDTO(BaseDTO):
    """O que a conferência da sigla achou: livre, fora do formato, de um ativo ou de uma gestora."""

    ticker: str
    status: Literal["free", "format", "asset", "fund"]
    owner_name: str | None


class FundFoundRequest(BaseDTO):
    name: FundName
    ticker: FundTicker
    management_fee: FeeRate
    performance_fee: FeeRate


class FundContributionStockRequest(BaseDTO):
    ticker: str
    quantity: Decimal = Field(gt=0, decimal_places=8)


class FundContributionRequest(BaseDTO):
    cash: Decimal = Field(default=Decimal(0), ge=0, decimal_places=2)
    stocks: list[FundContributionStockRequest] = Field(default_factory=list)


class FundContributionResponse(BaseDTO):
    quotas: Decimal


class FundOfferRequest(BaseDTO):
    quotas: int = Field(gt=0)


class FundIssuanceRequest(BaseDTO):
    quotas: int = Field(gt=0)


class FundDirectedIssuanceRequest(BaseDTO):
    quotas: int = Field(gt=0)
    # O apelido do co-gestor que recebe a oferta; nulo é o gestor principal comprando para si
    buyer_nickname: str | None = None


class FundIssuanceSubscriptionRequest(BaseDTO):
    quotas: int = Field(gt=0)


class FundBuybackRequest(BaseDTO):
    quantity: int = Field(gt=0)
    max_price: Decimal = Field(gt=0, decimal_places=2)


class FundComanagerInviteRequest(BaseDTO):
    # O apelido do jogador convidado
    nickname: str
    share: ComanagerShare


class FundComanagerShareRequest(BaseDTO):
    share: ComanagerShare


class FundAssemblyConveneRequest(BaseDTO):
    # O apelido do jogador indicado a gestor; nulo é quem convoca
    candidate_nickname: str | None = None


class FundAssemblyFeeProposalRequest(BaseDTO):
    """As taxas que o gestor leva à votação dos cotistas."""

    management_fee: FeeRate
    performance_fee: FeeRate


class FundMergeProposalRequest(BaseDTO):
    """A gestora que a gestora do caminho incorpora."""

    daughter_fund_id: int


class FundMergePreviewDTO(BaseDTO):
    """O que a fusão faz hoje, antes de o gestor levá-la às duas assembleias."""

    mother: FundMergeSideDTO
    daughter: FundMergeSideDTO
    # Cotas da incorporadora por cota da incorporada, pelo PL por cota de hoje; nulo sem PL
    ratio: Decimal | None
    mother_quotas: Decimal
    daughter_quotas: Decimal
    # A incorporadora depois: cotas em circulação e o patrimônio delas ao PL por cota de hoje
    quotas_after: Decimal | None
    equity_after: Decimal | None


class FundAssemblyVoteRequest(BaseDTO):
    agenda: FundAssemblyAgenda
    in_favor: bool


class FundIssuancePreviewDTO(BaseDTO):
    """O que uma emissão de `quotas` cotas faz, antes de o gestor anunciar."""

    quotas: Decimal
    # PL por cota de hoje: o preço fixo da emissão
    price: Decimal
    # Dinheiro que entra no caixa se todas as cotas forem vendidas
    raised: Decimal
    # A parte de `raised` que vai aos Banqueiros de ofertas da partida; zero sem Banqueiro
    commission: Decimal
    total_after: Decimal
    # Maior emissão permitida, em cotas
    limit: Decimal
    # A parte do gestor hoje e depois da emissão se ele não comprar e se usar o direito dele
    share_now: Decimal
    share_if_skip: Decimal
    keeps_control_if_skip: bool
    share_if_buy: Decimal
    keeps_control_if_buy: bool
    # O direito de preferência do gestor e o que custa usá-lo inteiro
    manager_rights: Decimal
    manager_cost: Decimal
    # A captação estimada da sobra por bots e Mercado; nula sem PL por cota
    estimate: FundIssuanceEstimateDTO | None


class FundIssuanceSubscriptionPreviewDTO(BaseDTO):
    """O que comprar `quotas` da preferência custa e deixa para quem consulta."""

    quotas: Decimal
    price: Decimal
    cost: Decimal
    # O caixa pessoal cobre o custo
    cash_enough: bool
    # O máximo de cotas que ele compra agora: o menor entre o direito que resta e as cotas inteiras que o caixa paga
    max_quotas: Decimal
    # Cotas de quem consulta e a parte dele depois da compra
    my_quotas_after: Decimal
    my_share_after: Decimal
    # O direito que ainda resta depois da compra
    rights_left_after: Decimal


class FundDirectedIssuancePreviewDTO(BaseDTO):
    """O que uma emissão dirigida de `quotas` cotas faz, vista por quem consulta como comprador."""

    quotas: Decimal
    # PL por cota, preço de ranking e o preço da emissão: o maior dos dois
    nav: Decimal
    ranking_price: Decimal
    price: Decimal
    cost: Decimal
    # O caixa pessoal de quem consulta e se ele cobre o custo
    buyer_cash: Decimal
    cash_enough: bool
    # Do custo, a parte que quita a taxa a pagar da gestora e a que fica no caixa dela
    to_payable: Decimal
    to_cash: Decimal
    # O máximo de cotas novas agora (nulo sem limite) e o teto de participação do modo aquisição hostil (nulo fora dele)
    room: Decimal | None
    manager_cap: Decimal | None
    total_after: Decimal
    # PL por cota de quem já tem cotas depois da emissão
    nav_after: Decimal
    # As cotas e a participação de quem consulta, antes e depois
    my_quotas_after: Decimal
    my_share_now: Decimal
    my_share_after: Decimal
    # A participação somada do principal e dos co-gestores, antes e depois
    operators_share_now: Decimal
    operators_share_after: Decimal


class FundBuybackPreviewDTO(BaseDTO):
    """O que uma recompra de `quantity` cotas a até `max_price` faz, antes de o gestor confirmar."""

    quantity: Decimal
    max_price: Decimal
    # PL por cota de hoje
    nav: Decimal
    # Ágio (positivo) ou deságio (negativo) do preço máximo sobre o PL por cota: 0,10 é 10%
    premium: Decimal
    # Caixa da gestora que a ordem reserva ao preço máximo
    cost: Decimal
    # Quanto desse custo é ágio sobre o PL por cota: sai do patrimônio de quem fica
    premium_cost: Decimal
    # O que sobra no caixa e se ele cobre o custo
    cash_after: Decimal
    cash_enough: bool
    # PL por cota de quem fica se tudo for comprado ao preço máximo
    nav_after: Decimal
    total_after: Decimal
    # A parte do gestor hoje e depois da recompra
    share_now: Decimal
    share_after: Decimal
    keeps_control_after: bool


class FundFeesRequest(BaseDTO):
    management_fee: FeeRate
    performance_fee: FeeRate


class FundDistributionRequest(BaseDTO):
    distribution_rate: DistributionRate
