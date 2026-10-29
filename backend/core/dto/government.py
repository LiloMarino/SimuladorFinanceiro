"""A eleição da expansão Governo & Política, como a página a mostra e como as ações chegam."""

import re
from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import Field, StringConstraints

from backend.core.dto.base import BaseDTO
from backend.core.dto.promises import (
    PromiseDTO,
    PromiseOptionDTO,
    PromiseRecordDTO,
    TermPromisesDTO,
)
from backend.core.enum import (
    ApprovalFactorKind,
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
    # O vice assumiu depois de um impeachment
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


class MyPartyDTO(BaseDTO):
    party_id: int
    is_founder: bool
    is_candidate: bool
    contribution: Decimal


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
    # Em cada 100 eleitores, quantos aprovavam no voto (ou aprovam hoje, na fila)
    chance: int | None
    # Aprovada: o dia em que passa a valer
    effective: date | None
    # Aprovada: dias de espera já cumpridos e os que faltam
    waiting_days: int | None
    days_left: int | None
    # Pontos no alvo da aprovação geral quando a medida vale cheia
    impact: int
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
    # A regra que o disparou: fechamentos seguidos abaixo do piso de aprovação
    months: int
    floor: int


class GovernmentPanelDTO(BaseDTO):
    today: date
    term: TermDTO | None
    # O governo do computador vale até a primeira posse
    computer_until_inauguration: bool
    is_president: bool
    # Fim do mandato: a carteira do presidente congelada vai até aqui
    term_end: date | None
    next_election: date
    approval: ApprovalDTO | None
    taxes: list[TaxRowDTO]
    sector_measures: list[SectorMeasureDTO]
    queue: list[MeasureDTO]
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


class MeasurePreviewDTO(BaseDTO):
    title: str
    # Quanto a medida, aprovada, move o perfil do partido do presidente
    profile_moves: list[ValueMoveDTO]
    # Pontos no alvo da aprovação geral quando a medida vale cheia, pesados pelo tamanho dos grupos
    impact: int
    chance: int
    vote_date: date
    effective: date
    assets: int | None
    holdings: list[MeasureHoldingDTO]


# Requisições


class FoundPartyRequest(BaseDTO):
    name: PartyName
    abbr: PartyAbbr
    color: Annotated[str, StringConstraints(pattern=PARTY_COLOR_PATTERN)]
    flags: list[VoterValue]
    contribution: Contribution = Decimal(0)


class PartyFlagsRequest(BaseDTO):
    flags: list[VoterValue]


class JoinPartyRequest(BaseDTO):
    contribution: Contribution = Decimal(0)


class ContributionRequest(BaseDTO):
    contribution: Contribution


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
