"""A preparação de cada jogador no lobby e o Meu partido salvo no perfil."""

from typing import Annotated

from pydantic import StringConstraints

from backend.core.dto.base import BaseDTO
from backend.core.dto.government import PARTY_COLOR_PATTERN, PartyAbbr, PartyName
from backend.core.enum import PreparationKind, VoterValue


class PartyIdentityDTO(BaseDTO):
    """A identidade do partido que o jogador funda, guardada no perfil; o histórico recomeça a cada partida."""

    name: PartyName
    abbr: PartyAbbr
    color: Annotated[str, StringConstraints(pattern=PARTY_COLOR_PATTERN)]
    flags: list[VoterValue]


class PreparationRequest(BaseDTO):
    kind: PreparationKind
    # Quem fundou o partido em que entra; só para JOIN
    founder: str | None = None
    # Quem encabeça a chapa (o próprio fundador ou um filiado) e o vice convidado; só para FOUND
    candidate: str | None = None
    vice: str | None = None


class ViceAnswerRequest(BaseDTO):
    accept: bool


class PlayerPreparationDTO(BaseDTO):
    nickname: str
    kind: PreparationKind
    # A identidade do partido, quando o jogador funda
    party: PartyIdentityDTO | None = None
    # O fundador do partido em que o jogador entra
    founder: str | None = None
    candidate: str | None = None
    vice: str | None = None
    vice_accepted: bool = False


class ReservedPartyDTO(BaseDTO):
    """Um partido do computador, cujo nome e sigla ninguém repete."""

    name: str
    abbr: str


class PreparationsDTO(BaseDTO):
    """A preparação da sala: a de cada jogador, os avisos de conflito e se o painel está travado."""

    players: list[PlayerPreparationDTO]
    reserved: list[ReservedPartyDTO]
    # Sigla, nome ou cor repetidos entre os preparados e com os partidos do computador
    conflicts: list[str]
    # Por que a preparação está travada (expansão desligada, partida salva ou em andamento); nulo quando aberta
    locked_reason: str | None = None
