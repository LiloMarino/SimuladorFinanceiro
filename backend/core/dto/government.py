"""A eleição da expansão Governo & Política, como a página a mostra e como as ações chegam."""

import re
from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import Field, StringConstraints

from backend.core.dto.base import BaseDTO
from backend.core.enum import (
    ApprovalFactorKind,
    ElectionPhase,
    MeasureKind,
    MeasureStatus,
    VicePhase,
)

PARTY_NAME_MAX_LENGTH = 60
PARTY_ABBR_PATTERN = re.compile(r"^[A-ZÀ-Ý]{2,8}$")
PARTY_COLOR_PATTERN = r"^#[0-9A-Fa-f]{6}$"
PROMISE_MIN = 1
PROMISE_MAX = 5

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
    # Posição na régua: 1 impostos baixos a 5 gasto alto
    promise: int
    founder: str | None
    founded: date
    members: list[PartyMemberDTO]
    # Verba por mês (soma das contribuições) e o que já saiu na campanha
    budget: Decimal
    spent: Decimal
    # Em cada 100 eleitores, quantos votariam no partido hoje
    intention_points: Decimal
    # Fatia nos votos válidos, de 0 a 1
    valid_share: Decimal
    candidate: PartyCandidateDTO | None
    vice: PartyCandidateDTO | None
    vice_phase: VicePhase
    # A chapa foi escolhida pela fundadora; falso quando é a padrão
    ticket_chosen: bool


class PollEntryDTO(BaseDTO):
    party_id: int
    points: Decimal


class PollDTO(BaseDTO):
    date: date
    entries: list[PollEntryDTO]


class RunoffEntryDTO(BaseDTO):
    party_id: int
    # Votos próprios, os que vieram de quem saiu e a fatia final
    own_points: Decimal
    received_points: Decimal
    share: Decimal
    # Para quem foram os eleitores deste partido; nulo para finalista
    transfer_to: int | None
    # Doado a este partido entre os turnos
    donated: Decimal


class RunoffSimulationDTO(BaseDTO):
    """A simulação do 2º turno (ou o resultado dele): os eleitores de quem sai vão ao finalista mais próximo."""

    finalists: list[int]
    entries: list[RunoffEntryDTO]
    winner: int


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


class RoundResultDTO(BaseDTO):
    date: date
    election_year: int
    round: int
    parties: list[RoundPartyDTO]
    finalists: list[int]
    # Nulo quando o 1º turno não decidiu
    winner: int | None
    runoff: RunoffSimulationDTO | None


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
    # A promessa do partido na régua; nula no governo do computador
    promise: int | None
    # O vice assumiu depois de um impeachment
    succession: bool


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
    parties: list[PartyDTO]
    undecided: Decimal
    polls: list[PollDTO]
    # A simulação do 2º turno entre os dois primeiros de hoje; nula com menos de 2 partidos
    runoff_simulation: RunoffSimulationDTO | None
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
    # Faixa da régua, de 1 a 5
    ruler_band: int
    # Pontos na aprovação ao valer: positivo é corte, negativo é imposto novo
    impact: int
    can_withdraw: bool
    can_repropose: bool


class ApprovalFactorDTO(BaseDTO):
    kind: ApprovalFactorKind
    points: int
    description: str
    measure_id: int | None


class ApprovalPointDTO(BaseDTO):
    date: date
    value: int


class UpcomingEffectDTO(BaseDTO):
    """Medida aprovada que ainda não vale e vai pesar na aprovação quando valer."""

    measure_id: int
    description: str
    effective: date
    impact: int


class ApprovalDTO(BaseDTO):
    value: int
    # Aprovação do mês anterior, para a seta
    previous: int | None
    history: list[ApprovalPointDTO]
    factors: list[ApprovalFactorDTO]
    upcoming: list[UpcomingEffectDTO]
    floor: int
    # Meses seguidos abaixo do piso e quantos levam ao impeachment
    low_streak: int
    impeachment_months: int
    # A marca do governo e a promessa da campanha, na régua de 1 a 5
    mark: Decimal | None
    promise: int | None


class TaxRowDTO(BaseDTO):
    kind: MeasureKind
    # O valor em vigor hoje: alíquota, teto em reais ou, na renda fixa, a alíquota mínima
    value: Decimal
    # Na renda fixa, a alíquota do prazo mais curto
    top_value: Decimal | None
    # A medida da fila ou esperando a vigência que muda esta linha
    pending: MeasureDTO | None


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
    # A regra que o disparou: meses seguidos abaixo do piso de aprovação
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
    ruler_band: int
    mark_before: Decimal | None
    mark_after: Decimal
    promise: int | None
    # Pontos na aprovação ao valer: positivo é corte, negativo é imposto novo
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
    promise: Annotated[int, Field(ge=PROMISE_MIN, le=PROMISE_MAX)]
    contribution: Contribution = Decimal(0)


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
