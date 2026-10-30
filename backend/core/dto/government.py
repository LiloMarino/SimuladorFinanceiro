"""A eleição da expansão Governo & Política, como a página a mostra e como as ações chegam."""

import re
from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import Field, StringConstraints

from backend.core.dto.base import BaseDTO
from backend.core.dto.budget import BudgetEffectDTO, QueueBudgetDTO
from backend.core.dto.promises import (
    PromiseDTO,
    PromiseOptionDTO,
    PromiseRecordDTO,
    TermPromisesDTO,
)
from backend.core.enum import (
    ApprovalFactorKind,
    DealStatus,
    EffectPhase,
    ElectionPhase,
    GroupReading,
    GroupVerdict,
    MeasureKind,
    MeasureStatus,
    VicePhase,
    VoterGroup,
    VoterValue,
)

PARTY_NAME_MAX_LENGTH = 60
PARTY_ABBR_PATTERN = re.compile(r"^[A-ZÀ-Ý]{2,8}$")
PARTY_COLOR_PATTERN = r"^#[0-9A-Fa-f]{6}$"

PartyName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=2, max_length=PARTY_NAME_MAX_LENGTH
    ),
]
PartyAbbr = Annotated[
    str,
    StringConstraints(strip_whitespace=True, to_upper=True, min_length=2, max_length=5),
]
Contribution = Annotated[Decimal, Field(ge=0, max_digits=14, decimal_places=2)]


# Resposta


class ValueScoreDTO(BaseDTO):
    value: VoterValue
    score: Decimal


class GroupScoreDTO(BaseDTO):
    group: VoterGroup
    score: Decimal


class ValueMoveDTO(BaseDTO):
    value: VoterValue
    # Pontos de perfil que o valor ganha (positivo) ou perde
    points: Decimal


class ProfileMoveDTO(BaseDTO):
    """Uma medida aprovada que moveu o perfil do partido."""

    date: date
    description: str
    moves: list[ValueMoveDTO]


class VoterGroupDTO(BaseDTO):
    """Um grupo de eleitores: o tamanho, o que ele quer e o que ele lê do governo."""

    group: VoterGroup
    # Fatia do eleitorado, de 0 a 1
    weight: Decimal
    # Margem de erro da pesquisa no grupo, em pontos
    margin: int
    readings: list[GroupReading]
    # O que o grupo quer em cada valor, de 0 (rejeita) a 100 (quer); 50 é indiferente
    wants: list[ValueScoreDTO]
    # Quanto cada bandeira soma (ou tira) da afinidade inicial com o grupo
    flag_affinity: list[ValueScoreDTO]


class ElectorateRowDTO(BaseDTO):
    """O que um grupo acha do partido de quem vê, exato: só os filiados recebem."""

    group: VoterGroup
    affinity: Decimal
    support: Decimal
    rejection: Decimal
    # Diferença entre as duas últimas pesquisas; nula antes da segunda
    support_change: Decimal | None
    rejection_change: Decimal | None


class PartyMemberDTO(BaseDTO):
    nickname: str
    # Chave da paleta (chart-N): a cor do jogador na partida
    color: str
    contribution: Decimal
    # A parte da contribuição que vai para a campanha do Congresso
    congress: Decimal
    is_founder: bool
    is_candidate: bool
    vice: VicePhase


class PartyCandidateDTO(BaseDTO):
    """Quem vai à urna pelo partido; o do computador não é jogador."""

    # Apelido do jogador; nulo no partido do computador
    nickname: str | None
    name: str
    color: str | None


class PartyDTO(BaseDTO):
    id: int
    name: str
    abbr: str
    # Cor escolhida pelo fundador (#RRGGBB); nula no partido do computador
    color: str | None
    is_computer: bool
    # As 3 bandeiras; nulas no partido fundado antes delas, até o fundador escolher
    flags: list[VoterValue] | None
    # O perfil de hoje e o da fundação, de 0 a 100 em cada valor
    radar: list[ValueScoreDTO]
    founding_radar: list[ValueScoreDTO]
    # Afinidade de cada grupo com o perfil de hoje e com o da fundação, de 0 a 100
    affinity: list[GroupScoreDTO]
    founding_affinity: list[GroupScoreDTO]
    # O que moveu o perfil, do mais recente ao mais antigo
    moves: list[ProfileMoveDTO]
    founder: str | None
    founded: date
    members: list[PartyMemberDTO]
    # Verba por mês (soma das contribuições) e o que já saiu na campanha
    budget: Decimal
    spent: Decimal
    # Em cada 100 eleitores, quantos votariam no partido na última pesquisa publicada
    intention_points: Decimal
    # Fatia nos votos válidos dessa pesquisa, de 0 a 1
    valid_share: Decimal
    candidate: PartyCandidateDTO | None
    vice: PartyCandidateDTO | None
    vice_phase: VicePhase
    # A chapa foi escolhida pela fundadora; falso quando é a padrão
    ticket_chosen: bool
    # As promessas da campanha em curso e as das eleições que passaram
    promises: list[PromiseDTO]
    past_promises: list[PromiseRecordDTO]


class PollEntryDTO(BaseDTO):
    party_id: int
    points: Decimal


class GroupPollDTO(BaseDTO):
    group: VoterGroup
    entries: list[PollEntryDTO]
    undecided: Decimal
    # Pontos para mais ou para menos; zero quando a sala desligou a margem
    margin: int


class PollDTO(BaseDTO):
    """A pesquisa como foi publicada: com o erro sorteado dentro da margem, se ela vale."""

    date: date
    entries: list[PollEntryDTO]
    undecided: Decimal
    margin: int
    groups: list[GroupPollDTO]


class TransferGroupDTO(BaseDTO):
    """O voto de um partido eliminado dentro de um grupo e para onde ele foi, em cada 100 do grupo."""

    group: VoterGroup
    voted: Decimal
    # O que cada finalista recebeu no 1º turno
    sent: list[PollEntryDTO]
    # Os que ficaram indecisos na hora, e os que ainda estão
    undecided: Decimal
    undecided_now: Decimal
    # Confiança do grupo no partido eliminado (de 0 a 1), que decide quantos indecisos a declaração leva
    trust: Decimal
    # Quantos eleitores do grupo (em cada 100) mudariam do indeciso para o finalista apoiado se o partido declarasse hoje
    would_follow: Decimal


class TransferDTO(BaseDTO):
    """Para onde foram os votos de um partido eliminado, grupo a grupo e no eleitorado todo."""

    party_id: int
    groups: list[TransferGroupDTO]
    # Em cada 100 eleitores do país: os que votaram nele, os que foram a cada finalista e os que ficaram indecisos
    voted: Decimal
    sent: list[PollEntryDTO]
    undecided: Decimal
    # A declaração de apoio dele, quando houve; `declared` distingue neutralidade de silêncio
    declared: bool
    endorsed_party_id: int | None


class DeclarationDTO(BaseDTO):
    date: date
    party_id: int
    # Quem declarou; nulo no partido do computador
    nickname: str | None
    # Nulo é neutralidade
    endorsed_party_id: int | None


class RunoffContributionDTO(BaseDTO):
    date: date
    # Nulo no finalista do computador
    nickname: str | None
    party_id: int
    amount: Decimal


class RunoffRaceDTO(BaseDTO):
    """O 2º turno em andamento: pesquisa semanal, transferência dos eliminados e o que os partidos podem fazer."""

    finalists: list[int]
    # As pesquisas semanais publicadas, com a margem de cada grupo
    polls: list[PollDTO]
    next_poll: date | None
    transfers: list[TransferDTO]
    declarations: list[DeclarationDTO]
    contributions: list[RunoffContributionDTO]
    # O que o filiado de quem vê já contribuiu; nulo se ainda não contribuiu
    my_contribution: Decimal | None
    can_declare: bool
    can_contribute: bool
    can_add_promise: bool
    promise_limit: int


class RoundPartyDTO(BaseDTO):
    party_id: int
    abbr: str
    name: str
    color: str | None
    is_computer: bool
    candidate: PartyCandidateDTO | None
    vice: PartyCandidateDTO | None
    points: Decimal
    share: Decimal
    # As promessas que a chapa levou à urna
    promises: list[PromiseDTO]


class RoundDonationDTO(BaseDTO):
    party_id: int
    amount: Decimal


class RoundResultDTO(BaseDTO):
    date: date
    election_year: int
    round: int
    parties: list[RoundPartyDTO]
    finalists: list[int]
    # Nulo quando o 1º turno não decidiu
    winner: int | None
    # No 2º turno: o voto de cada grupo entre os finalistas, exato, e quem não votou (em pontos do eleitorado)
    groups: list[GroupPollDTO]
    not_voted: Decimal
    # O que se doou a cada finalista entre os turnos
    donations: list[RoundDonationDTO]


class DonationDTO(BaseDTO):
    date: date
    nickname: str
    party_id: int
    amount: Decimal


class TermDTO(BaseDTO):
    party_id: int | None
    president: PartyCandidateDTO | None
    vice: PartyCandidateDTO | None
    start: date
    consecutive: int
    # Assumiu depois de um impeachment: o vice ou, sem ele, o partido do computador
    succession: bool
    # As promessas da chapa, cobradas no fim do mandato
    promises: list[PromiseDTO]


class PlayerStandingDTO(BaseDTO):
    nickname: str
    color: str
    party_id: int | None
    total_networth: Decimal


class PartyStandingDTO(BaseDTO):
    """O patrimônio do partido é a soma do patrimônio dos filiados."""

    party_id: int
    abbr: str
    name: str
    color: str | None
    members: list[str]
    total_networth: Decimal


class ElectionDatesDTO(BaseDTO):
    campaign_start: date
    ticket_deadline: date
    first_round: date
    runoff: date
    donation_deadline: date
    inauguration: date


class GuidanceRuleDTO(BaseDTO):
    """A orientação padrão do partido para um valor: Sim ou Não nas medidas que mais puxam esse valor."""

    value: VoterValue
    yes: bool


class MyPartyDTO(BaseDTO):
    party_id: int
    is_founder: bool
    is_candidate: bool
    contribution: Decimal
    # A parte da contribuição que vai para a campanha do Congresso
    congress: Decimal
    # A orientação padrão da bancada, um valor por vez; só o líder muda
    guidance: list[GuidanceRuleDTO]


class MyViceDTO(BaseDTO):
    """A chapa em que quem vê foi indicado vice, de qualquer partido."""

    party_id: int
    phase: VicePhase


class ViceOptionDTO(BaseDTO):
    """Um jogador da sala que a fundadora pode convidar para vice."""

    nickname: str
    color: str
    # Sigla do partido dele; nula para quem não tem partido
    party_abbr: str | None
    # Por que não pode ser convidado ("já é vice do ABC"); nulo quando pode
    blocked: str | None


class ElectionPanelDTO(BaseDTO):
    today: date
    phase: ElectionPhase
    election_year: int
    dates: ElectionDatesDTO
    groups: list[VoterGroupDTO]
    # Afinidade de partida de toda bandeira com todo grupo, antes do que cada bandeira soma
    affinity_base: Decimal
    # No perfil de 0 a 100: onde fica o valor que o partido não defende e onde fica a bandeira
    radar_neutral: Decimal
    radar_flag: Decimal
    # A pesquisa mostra a margem de erro; desligada, mostra o número exato
    poll_margin: bool
    parties: list[PartyDTO]
    # Indecisos na última pesquisa publicada
    undecided: Decimal
    polls: list[PollDTO]
    # Apoio e rejeição do partido de quem vê em cada grupo; vazio para quem não é filiado
    electorate: list[ElectorateRowDTO]
    # Entre os turnos: a disputa do 2º turno
    runoff_race: RunoffRaceDTO | None
    # Entre os turnos: os finalistas e as doações já feitas
    finalists: list[int]
    donations: list[DonationDTO]
    my_party: MyPartyDTO | None
    # O convite de vice de quem vê, em qualquer partido
    my_vice: MyViceDTO | None
    # Só para quem funda: os jogadores da sala e quem pode ser convidado
    vice_options: list[ViceOptionDTO]
    can_found_or_join: bool
    can_edit_ticket: bool
    can_donate: bool
    # O último turno apurado e o histórico de todas as eleições
    last_result: RoundResultDTO | None
    results: list[RoundResultDTO]
    term: TermDTO | None
    pending_term: TermDTO | None
    # O ranking de partidos decide a partida quando a vitória é política
    decides_match: bool
    player_standings: list[PlayerStandingDTO]
    party_standings: list[PartyStandingDTO]
    # Quantas vezes a verba média dos partidos de jogadores cada partido do computador gasta
    computer_budget_factor: Decimal


# Congresso


class BlocDTO(BaseDTO):
    """A bancada de um partido na casa."""

    key: int
    party_id: int | None
    abbr: str
    name: str
    color: str | None
    is_computer: bool
    # Em cada 100 votos válidos da eleição da casa
    votes: Decimal
    seats: int
    # Cadeiras na casa anterior; nulo na primeira casa eleita
    previous_seats: int | None
    # A bancada é do partido do presidente
    governing: bool
    # Votações em que a bancada já votou, e dessas em quantas por cento ela votou Sim e quantos deputados desobedeceram
    votes_cast: int
    yes_share: Decimal | None
    defection_share: Decimal | None
    # Quem vê é o líder desta bancada
    is_mine: bool


class HouseDTO(BaseDTO):
    # O dia da eleição e o da posse; nulos na casa inicial do computador
    elected: date | None
    takes_office: date | None
    seats: int
    majority: int
    impeachment_votes: int
    # Piso de votos válidos para ter cadeira, em fração
    barrier: Decimal
    blocs: list[BlocDTO]
    # Siglas que ficaram abaixo da barreira
    below: list[str]
    # O quociente da última cadeira dada e o da primeira que ficou de fora (D'Hondt)
    last_quotient: Decimal
    next_quotient: Decimal


class BlocVoteDTO(BaseDTO):
    """Como a bancada vota numa medida ou num pedido de impeachment."""

    key: int
    abbr: str
    color: str | None
    seats: int
    # A orientação: Sim (verdadeiro) ou Não
    orientation: bool
    # O líder orientou; falso quando vale a orientação padrão
    guided: bool
    # Na fila: até quantos deputados podem votar contra a orientação
    may_defect: int
    # Votada: o Sim, o Não e quantos foram contra a orientação
    yes: int | None
    no: int | None
    defected: int | None
    # O grupo do eleitorado da bancada que mais queria o voto contrário e quanto ele pesa nos eleitores dela, de 0 a 1
    cause: VoterGroup | None
    cause_share: Decimal | None
    # A bancada tem acordo de apoio em vigor: orienta Sim pelo acordo
    by_deal: bool


class GuideScenarioDTO(BaseDTO):
    """O que muda no placar se o líder orientar a bancada dele assim."""

    orientation: bool
    low: int
    high: int
    may_defect: int
    cause: VoterGroup | None
    cause_share: Decimal | None


class GuideDTO(BaseDTO):
    """O que o líder vê para orientar a bancada dele numa votação."""

    bloc_key: int
    abbr: str
    seats: int
    # Até quando muda: a véspera da votação
    deadline: date
    # A orientação que vale sem ele, e o valor da medida que a decide
    default_orientation: bool
    pulled_value: VoterValue | None
    scenarios: list[GuideScenarioDTO]
    # Quanto orientar Sim move o perfil do partido dele; vazio no governo e nas medidas de gasto
    yes_moves: list[ValueMoveDTO]
    # A bancada dele tem acordo em vigor: orientar Não numa medida do governo rompe o acordo
    by_deal: bool


class VoteDTO(BaseDTO):
    """O placar de uma votação: previsto em faixa na fila, exato depois de votada."""

    blocs: list[BlocVoteDTO]
    # Votos Sim para passar
    needed: int
    yes: int | None
    no: int | None
    defected: int | None
    # Na fila: do Sim com todos os que podem desobedecer votando contra até o Sim sem nenhum
    low: int | None
    high: int | None
    # Presente quando quem vê é o líder de uma bancada e ainda dá tempo de orientar
    guide: GuideDTO | None


class ImpeachmentRequestDTO(BaseDTO):
    opened: date
    vote_day: date
    president: str | None
    vote: VoteDTO


class PastVoteDTO(BaseDTO):
    """Uma votação já feita pela casa, para o histórico."""

    day: date
    title: str
    approved: bool
    yes: int
    no: int
    defected: int
    is_impeachment: bool


class CongressDTO(BaseDTO):
    # A casa em exercício e, depois da eleição e antes da posse, a que vai assumir
    house: HouseDTO
    elected: HouseDTO | None
    impeachment_request: ImpeachmentRequestDTO | None
    history: list[PastVoteDTO]
    # Meses seguidos abaixo do piso e quantos faltam para abrir o pedido
    low_streak: int


# Base no Congresso


class DealDTO(BaseDTO):
    """Um acordo de apoio por emenda, da proposta ao fim."""

    id: int
    bloc_key: int
    party_id: int | None
    abbr: str
    name: str
    color: str | None
    seats: int
    status: DealStatus
    # O líder do partido aliado, pelo apelido; nulo no partido do computador
    leader: str | None
    is_computer: bool
    centrao: bool
    # A emenda em fração do PIB por ano e em reais por mês
    ratio: Decimal
    monthly: Decimal
    # Proposta: o prazo da resposta do partido de jogador
    answer_by: date | None
    # Em vigor: o último dia do acordo e quantos dias faltam
    start: date | None
    end: date | None
    days_left: int | None
    # Faltam no máximo 31 dias: o governo já pode propor de novo
    renewable: bool
    # Medidas do governo votadas durante o acordo e quantas a bancada orientou Sim
    votes: int
    yes: int
    # As cadeiras da base depois da mudança: sem o acordo em vigor, ou com a proposta aceita
    base_after: int
    # Os grupos mais fortes do aliado (que recebem a emenda e, na quebra do governo, culpam o presidente) e os do governo (que, na saída do aliado, culpam o aliado)
    ally_groups: list[VoterGroup]
    government_groups: list[VoterGroup]


class BaseBlocDTO(BaseDTO):
    """Uma bancada no hemiciclo da base: a situação dela e o que impede propor."""

    key: int
    party_id: int | None
    abbr: str
    name: str
    color: str | None
    seats: int
    is_computer: bool
    centrao: bool
    # O partido de jogador tem líder; o apelido dele
    leader: str | None
    # O partido do presidente
    governing: bool
    # Tem acordo em vigor
    in_base: bool
    # Espera a resposta de uma proposta
    pending: bool
    # A emenda em fração do PIB por ano e em reais por mês, pelo preço de hoje
    ratio: Decimal
    monthly: Decimal
    # Por que não dá para propor agora e, quando é espera, o dia em que abre
    blocker: str | None
    retry_from: date | None
    # O dia da última recusa; nulo sem recusa
    declined_on: date | None


class BaseVoteDTO(BaseDTO):
    """A última votação de medida do governo e quantos deputados da base votaram contra a orientação."""

    day: date
    defected: int


class AmendmentSummaryDTO(BaseDTO):
    """O que os acordos em vigor pagam: em fração do PIB por ano e em reais por mês."""

    ratio: Decimal
    monthly: Decimal


class CongressBaseDTO(BaseDTO):
    """A base do governo no Congresso: o partido do presidente mais os aliados pagos com emenda."""

    # O partido do presidente; nulo sem governo
    governing_abbr: str | None
    governing_seats: int
    seats: int
    majority: int
    # Os votos Sim que tiram o presidente
    impeachment_votes: int
    # O presidente, pelo apelido
    president: str | None
    # Quem vê é o presidente
    is_president: bool
    # Quem vê é o líder de um partido aliado, e o acordo dele
    my_deal: DealDTO | None
    # A proposta que espera a resposta de quem vê
    my_proposal: DealDTO | None
    deals: list[DealDTO]
    blocs: list[BaseBlocDTO]
    amendments: AmendmentSummaryDTO
    last_vote: BaseVoteDTO | None
    # Sem permissão de propor para ninguém: o motivo (impeachment em votação)
    blocker: str | None
    # As propostas ao partido de jogador contam 15 dias, e o do computador responde no pregão seguinte
    answer_days: int
    term_months: int


class DealPreviewDTO(BaseDTO):
    """O que a proposta faz antes de enviar: o preço, a base, a dívida e a chance de aceitar."""

    bloc_key: int
    abbr: str
    name: str
    color: str | None
    seats: int
    leader: str | None
    is_computer: bool
    centrao: bool
    ratio: Decimal
    monthly: Decimal
    start: date
    end: date
    base_before: int
    base_after: int
    # A dívida em fração do PIB no fim do mandato, sem e com o acordo, e o dia da conta
    debt_before: Decimal | None
    debt_after: Decimal | None
    debt_end: date | None
    # Os grupos do aliado: ganham apoio a ele com a emenda e, se o governo romper, somam rejeição ao partido do presidente
    ally_groups: list[VoterGroup]
    # O partido do computador deve aceitar; nulo no partido de jogador
    likely: bool | None
    shared_flags: int | None
    blocker: str | None


# Governo


class MeasureDTO(BaseDTO):
    id: int
    kind: MeasureKind
    title: str
    sector: str | None
    segment: str | None
    value: Decimal | None
    proposer: str
    proposed: date
    status: MeasureStatus
    # Na fila: o dia do próximo voto. Decidida: o dia em que foi votada
    vote_date: date | None
    # Na fila: o placar previsto e a orientação de cada bancada. Decidida: o placar da votação
    vote: VoteDTO | None
    # Aprovada: o dia em que passa a valer
    effective: date | None
    # Aprovada: dias de espera já cumpridos e os que faltam
    waiting_days: int | None
    days_left: int | None
    # Pontos no alvo da aprovação geral quando a medida vale cheia
    impact: int
    # Quanto a medida muda o resultado do governo (receita menos gasto), em fração do PIB por ano
    budget_effect: Decimal
    # Pontos de IPCA que a medida soma no pico, em 12 meses; negativo é corte. Zero nos impostos
    inflation_effect: Decimal
    # A medida cumpre uma promessa da chapa que governa
    fulfills_promise: bool
    can_withdraw: bool
    can_repropose: bool


class ApprovalFactorDTO(BaseDTO):
    kind: ApprovalFactorKind
    # Pontos que o fator soma ao alvo do grupo (ou o ponto neutro, no BASE)
    points: Decimal
    description: str
    measure_id: int | None


class ApprovalPointDTO(BaseDTO):
    date: date
    value: int


class GroupApprovalDTO(BaseDTO):
    """A satisfação de um grupo com o governo, o alvo dela e o que a puxa."""

    group: VoterGroup
    # Fatia do grupo no eleitorado
    weight: Decimal
    readings: list[GroupReading]
    satisfaction: int
    # Onde a satisfação para se nada mudar
    target: int
    verdict: GroupVerdict
    # A satisfação no fechamento anterior, para a seta
    previous: int | None
    history: list[ApprovalPointDTO]
    factors: list[ApprovalFactorDTO]


class UpcomingEffectDTO(BaseDTO):
    """Medida aprovada que ainda não vale e vai pesar no alvo dos grupos quando valer."""

    measure_id: int
    description: str
    effective: date
    impact: int


class ClosingDTO(BaseDTO):
    """O que o último fechamento fez com o apoio e a rejeição do partido do presidente."""

    month: date
    party_abbr: str
    approved: list[VoterGroup]
    reproved: list[VoterGroup]
    neutral: list[VoterGroup]


class ApprovalDTO(BaseDTO):
    # A aprovação geral: a média das satisfações pesada pelo tamanho dos grupos
    value: int
    # Aprovação do fechamento anterior, para a seta
    previous: int | None
    # Alvo da aprovação geral
    target: int
    # Do dia da posse ao último fechamento
    history: list[ApprovalPointDTO]
    groups: list[GroupApprovalDTO]
    upcoming: list[UpcomingEffectDTO]
    # Quando a satisfação anda um terço até o alvo
    closes_on: date
    # Satisfação abaixo da qual o grupo reprova o mês e acima da qual aprova
    reproves_below: int
    approves_above: int
    floor: int
    # Fechamentos seguidos abaixo do piso e quantos levam ao impeachment
    low_streak: int
    impeachment_months: int
    # O piso não conta até o fim da carência
    grace_until: date
    in_grace: bool
    # Só para os filiados do partido do presidente
    closing: ClosingDTO | None


class TaxRowDTO(BaseDTO):
    kind: MeasureKind
    # O valor em vigor hoje: alíquota, teto em reais ou, na renda fixa, a alíquota mínima
    value: Decimal
    # Na renda fixa, a alíquota do prazo mais curto
    top_value: Decimal | None
    # A medida da fila ou esperando a vigência que muda esta linha
    pending: MeasureDTO | None
    # A chapa que governa prometeu mexer nesta linha
    promised: bool


class SpendingRowDTO(BaseDTO):
    """Uma medida de gasto no cartão Gasto público: o valor em vigor, o que pesa e o que soma à inflação."""

    kind: MeasureKind
    # O valor em vigor: fração do PIB por ano (auxílio, obras) ou ganho real ao ano (reajustes)
    value: Decimal
    # O dia em que esse valor passou a valer; nulo no valor de largada
    since: date | None
    # Quanto a medida pesa no gasto do país, em fração do PIB por ano e em reais por ano
    cost: Decimal
    cost_amount: Decimal
    # O quanto o valor anda por passo de referência (também o máximo de uma medida) e o teto
    step: Decimal
    limit: Decimal
    # Pontos de IPCA que a última mudança soma hoje, a fase dela e o desenho mês a mês
    inflation: Decimal
    phase: EffectPhase | None
    curve: list[Decimal]
    elapsed_months: int | None
    # A medida da fila ou esperando a vigência que muda esta linha
    pending: MeasureDTO | None
    promised: bool


class SpendingCardDTO(BaseDTO):
    rows: list[SpendingRowDTO]
    # O resto do gasto, que as medidas não mexem, o gasto total e quanto ele passa do de largada
    rest: Decimal
    total: Decimal
    total_difference: Decimal
    # Pontos de IPCA que todas as medidas somam hoje
    inflation: Decimal


class SectorMeasureDTO(BaseDTO):
    measure: MeasureDTO
    assets: int


class FrozenSliceDTO(BaseDTO):
    label: str
    tickers: list[str]
    # Fatia do patrimônio, de 0 a 1
    share: Decimal


class InterestDTO(BaseDTO):
    """Um setor em que o presidente tem carteira e que tem medida na fila ou esperando a vigência."""

    sector: str
    share: Decimal
    measure_id: int
    vote_date: date | None
    effective: date | None


class FrozenPortfolioDTO(BaseDTO):
    nickname: str
    total_networth: Decimal
    frozen_until: date
    slices: list[FrozenSliceDTO]
    interests: list[InterestDTO]


class SegmentOptionDTO(BaseDTO):
    name: str
    assets: int


class SectorOptionDTO(BaseDTO):
    name: str
    assets: int
    tickers: list[str]
    segments: list[SegmentOptionDTO]


class ImpeachmentDTO(BaseDTO):
    date: date
    president: str | None
    successor: str | None
    # A regra que o abriu: fechamentos seguidos abaixo do piso de aprovação
    months: int
    floor: int
    # O placar da votação que derrubou o presidente
    yes: int
    no: int


class GovernmentPanelDTO(BaseDTO):
    today: date
    term: TermDTO | None
    # O governo do computador vale até a primeira posse
    computer_until_inauguration: bool
    is_president: bool
    # Fim do mandato: a carteira do presidente congelada vai até aqui
    term_end: date | None
    next_election: date
    congress: CongressDTO
    approval: ApprovalDTO | None
    taxes: list[TaxRowDTO]
    spending: SpendingCardDTO
    sector_measures: list[SectorMeasureDTO]
    queue: list[MeasureDTO]
    # A fila inteira do Congresso, se passar
    queue_budget: QueueBudgetDTO
    next_vote: date
    portfolio: FrozenPortfolioDTO | None
    sectors: list[SectorOptionDTO]
    last_impeachment: ImpeachmentDTO | None
    # Quantos dias a medida aprovada espera para valer
    vigence_days: int
    # As promessas da chapa que governa; nulo no governo do computador e sem promessas
    promises: TermPromisesDTO | None


class PromisesPanelDTO(BaseDTO):
    """O diálogo das promessas da chapa: o que a fundadora pode prometer e até quando."""

    party_id: int
    party_abbr: str
    is_founder: bool
    # Se a lista aceita mudança hoje; fechada, `closed_reason` explica
    open: bool
    closed_reason: str | None
    # A lista trava quando as chapas fecham
    ticket_deadline: date
    max_promises: int
    # Entre os turnos as promessas só se acrescentam: nenhuma sai nem muda
    add_only: bool
    promises: list[PromiseDTO]
    options: list[PromiseOptionDTO]
    sectors: list[SectorOptionDTO]


# Requisições do governo


class ProposeMeasureRequest(BaseDTO):
    kind: MeasureKind
    # Alíquota (0.20), teto em reais ou pontos somados, conforme o tipo
    value: Annotated[Decimal, Field(ge=0, max_digits=14, decimal_places=4)] | None = (
        None
    )
    sector: str | None = None
    segment: str | None = None


class MeasureHoldingDTO(BaseDTO):
    nickname: str
    # Fatia do patrimônio dele no setor (0 a 1) e o valor em reais
    share: Decimal
    value: Decimal


class InflationCurvePointDTO(BaseDTO):
    month: int
    points: Decimal


class InflationEffectDTO(BaseDTO):
    """O que uma medida de gasto faz com a inflação, a SELIC e a bolsa, estimado."""

    # Pontos de IPCA em 12 meses no pico (negativo é corte) e o mês em que o efeito vale cheio
    peak: Decimal
    peak_month: int
    curve: list[InflationCurvePointDTO]
    # IPCA em 12 meses e SELIC de hoje e no pico, em fração ao ano, se nada mais mudar
    ipca_before: Decimal
    ipca_after: Decimal
    selic_before: Decimal
    selic_after: Decimal
    # Variação da bolsa (fração) no trimestre da alta da SELIC; mais nas ações de beta alto
    stocks: Decimal
    # Pontos de crescimento do PIB que a medida soma no pico (as obras)
    growth: Decimal


class GroupReactionDTO(BaseDTO):
    group: VoterGroup
    # Pontos no alvo de apoio do grupo quando a medida vale cheia
    points: Decimal


class MeasurePreviewDTO(BaseDTO):
    title: str
    # Quanto a medida, aprovada, move o perfil do partido do presidente
    profile_moves: list[ValueMoveDTO]
    # Pontos no alvo da aprovação geral quando a medida vale cheia, pesados pelo tamanho dos grupos
    impact: int
    vote_date: date
    effective: date
    assets: int | None
    holdings: list[MeasureHoldingDTO]
    # O que a medida faz com a conta do governo, estimado
    budget: BudgetEffectDTO
    # A inflação, a SELIC e a bolsa esperadas; só nas medidas de gasto
    inflation: InflationEffectDTO | None
    # Como cada grupo de eleitores reage
    reactions: list[GroupReactionDTO]


# Requisições


class FoundPartyRequest(BaseDTO):
    name: PartyName
    abbr: PartyAbbr
    color: Annotated[str, StringConstraints(pattern=PARTY_COLOR_PATTERN)]
    flags: list[VoterValue]
    contribution: Contribution = Decimal(0)
    congress: Contribution = Decimal(0)


class PartyFlagsRequest(BaseDTO):
    flags: list[VoterValue]


class JoinPartyRequest(BaseDTO):
    contribution: Contribution = Decimal(0)
    congress: Contribution = Decimal(0)


class ContributionRequest(BaseDTO):
    contribution: Contribution
    # A parte que vai para o Congresso; o resto vai para a presidência
    congress: Contribution = Decimal(0)


class GuidanceRequest(BaseDTO):
    """A orientação do líder numa votação: a medida, ou o pedido de impeachment quando `measure_id` é nulo."""

    measure_id: int | None = None
    yes: bool
    # Orientar Não numa medida com acordo em vigor rompe o acordo: o líder confirma
    break_deal: bool = False


class ProposeDealRequest(BaseDTO):
    bloc_key: int


class AnswerDealRequest(BaseDTO):
    accept: bool


class GuidanceRuleRequest(BaseDTO):
    value: VoterValue
    yes: bool


class ExpelRequest(BaseDTO):
    nickname: str


class TicketRequest(BaseDTO):
    candidate: str
    vice: str | None = None


class ViceAnswerRequest(BaseDTO):
    accept: bool


class DonationRequest(BaseDTO):
    party_id: int
    amount: Annotated[Decimal, Field(gt=0, max_digits=14, decimal_places=2)]


class RunoffContributionRequest(BaseDTO):
    amount: Annotated[Decimal, Field(gt=0, max_digits=14, decimal_places=2)]


class EndorsementRequest(BaseDTO):
    # Nulo é neutralidade
    party_id: int | None = None
