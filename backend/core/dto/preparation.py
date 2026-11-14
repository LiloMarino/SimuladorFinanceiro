"""A preparação de cada jogador no lobby, o Meu partido e a Minha gestora salvos no perfil."""

from decimal import Decimal
from typing import Annotated

from pydantic import Field, StringConstraints

from backend.core.dto.base import BaseDTO
from backend.core.dto.fund import FundName, FundTicker
from backend.core.dto.government import (
    PARTY_COLOR_PATTERN,
    Contribution,
    PartyAbbr,
    PartyName,
)
from backend.core.enum import FundPreparationKind, PreparationKind, VoterValue


class PartyIdentityDTO(BaseDTO):
    """A identidade do partido que o jogador funda, guardada no perfil; o histórico recomeça a cada partida."""

    name: PartyName
    abbr: PartyAbbr
    color: Annotated[str, StringConstraints(pattern=PARTY_COLOR_PATTERN)]
    flags: list[VoterValue]


class FundIdentityDTO(BaseDTO):
    """A identidade da gestora que o jogador funda, guardada no perfil: nome e sigla ficam fixos na partida."""

    name: FundName
    ticker: FundTicker


class FundPreparationRequest(BaseDTO):
    kind: FundPreparationKind


class PartyContributionDTO(BaseDTO):
    """A contribuição mensal que o jogador leva a cada partido em que funda ou entra."""

    amount: Contribution


class PreparationRequest(BaseDTO):
    kind: PreparationKind
    # Quem fundou o partido em que entra; só para JOIN
    founder: str | None = None
    # Quem encabeça a chapa (o próprio fundador ou um filiado); só para FOUND
    candidate: str | None = None
    # O jogador convidado para vice; só para INVITE_VICE
    vice: str | None = None


class PreparationViceAnswerRequest(BaseDTO):
    # O fundador que convidou
    owner: str
    accept: bool


class FederationOfferRequest(BaseDTO):
    """A federação que o fundador propõe a outro fundador da sala; sem `partner`, retira a proposta."""

    partner: str | None = None
    name: PartyName | None = None
    # Quem encabeça a chapa dos dois: o próprio fundador, o do parceiro ou um filiado de qualquer um dos dois; vazio é o próprio fundador
    candidate: str | None = None


class FederationAnswerRequest(BaseDTO):
    # O fundador que propôs
    owner: str
    accept: bool


class PreparationFederationDTO(BaseDTO):
    """A federação combinada no lobby, vista pelos dois fundadores e pela sala."""

    # O fundador do outro partido
    partner: str
    name: str
    candidate: str


class PlayerPreparationDTO(BaseDTO):
    nickname: str
    kind: PreparationKind
    # A identidade do partido, quando o jogador funda
    party: PartyIdentityDTO | None = None
    # O fundador do partido em que o jogador entra
    founder: str | None = None
    candidate: str | None = None
    # O vice que aceitou o convite; o convite sem resposta só os dois enxergam
    vice: str | None = None
    vice_accepted: bool = False
    # A federação que o partido combinou; a proposta sem resposta só os dois enxergam
    federation: PreparationFederationDTO | None = None


class FundPreparationDTO(BaseDTO):
    """A gestora que um jogador da sala vai fundar no 1º dia da partida."""

    nickname: str
    name: str
    ticker: str


class ReservedPartyDTO(BaseDTO):
    """Um partido do computador, cujo nome e sigla ninguém repete, com as bandeiras fixas dele."""

    name: str
    abbr: str
    flags: list[VoterValue]


class PreparationsDTO(BaseDTO):
    """A preparação da sala: a de cada jogador, os avisos de conflito e se o painel está travado."""

    players: list[PlayerPreparationDTO]
    reserved: list[ReservedPartyDTO]
    # Sigla, nome ou cor repetidos entre os partidos preparados e com os do computador
    conflicts: list[str]
    # Quem funda gestora; vazio com a expansão Gestoras desligada
    funds: list[FundPreparationDTO] = Field(default_factory=list)
    # Nome ou sigla de gestora repetidos entre os jogadores, ou sigla com as letras de um ativo; cada frase começa pelos apelidos envolvidos
    fund_conflicts: list[str] = Field(default_factory=list)
    # Por que a escolha da gestora está travada (partida em andamento ou salva selecionada); nulo quando aberta
    fund_locked_reason: str | None = None
    # Convites de vice ainda sem resposta na sala, sem dizer de quem
    pending_invites: int = 0
    # No perfil de 0 a 100: onde fica o valor que o partido não defende e onde fica a bandeira
    radar_neutral: Decimal
    radar_flag: Decimal
    # Por que a preparação está travada (expansão desligada, partida salva ou em andamento); nulo quando aberta
    locked_reason: str | None = None


class ViceInviteDTO(BaseDTO):
    """Um convite de vice sem resposta: quem convidou, para a chapa de qual partido e de qual candidato."""

    owner: str
    abbr: str
    candidate: str


class FederationInviteDTO(BaseDTO):
    """Uma proposta de federação sem resposta: de quem veio, o nome e o candidato dos dois partidos."""

    owner: str
    abbr: str
    name: str
    candidate: str


class MyPreparationDTO(BaseDTO):
    """O que da preparação só o próprio jogador vê."""

    # Os convites de vice que o jogador recebeu e ainda não respondeu, um por chapa
    invites: list[ViceInviteDTO]
    # Quem o jogador convidou para vice e ainda não respondeu
    invited: str | None = None
    # Quem recusou o convite do jogador, ou aceitou o de outra chapa
    vice_declined: str | None = None
    # A sigla do partido em que o jogador entrou e que saiu da preparação; some na próxima escolha
    left_party: str | None = None
    # As propostas de federação que o jogador recebeu e ainda não respondeu
    federation_invites: list[FederationInviteDTO]
    # O fundador a quem o jogador propôs federação e ainda não respondeu
    federation_invited: str | None = None
