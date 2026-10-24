"""A eleição da expansão Governo & Política, como a página a mostra e como as ações chegam."""

import re
from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import Field, StringConstraints

from backend.core.dto.base import BaseDTO
from backend.core.enum import ElectionPhase, VicePhase

PARTY_NAME_MAX_LENGTH = 60
PARTY_ABBR_PATTERN = re.compile(r"^[A-ZÀ-Ý]{2,5}$")
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
    vice: VicePhase
    contribution: Decimal


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
