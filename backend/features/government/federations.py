"""
As federações partidárias: dois partidos numa lista e numa chapa só, presos pelo mandato.
Aqui moram a federação e a proposta, o líder da chapa, a orientação da bancada, a
rejeição que um parceiro herda do outro e a regra do computador; tudo é função pura
sobre números, e o estado da partida guarda as federações.
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from backend.core.enum import (
    FederationProposalStatus,
    FederationStatus,
    VoterGroup,
    VoterValue,
)
from backend.features.government import voters

# A proposta vale 7 dias, ou até o outro partido se federar
PROPOSAL_DAYS = 7
# Cada partido soma esta fração da rejeição do parceiro em cada grupo
INHERITED_REJECTION = Decimal("0.5")


@dataclass
class Federation:
    """Uma federação formada, da aceitação ao fim."""

    id: int
    # Quem propôs e quem aceitou, nesta ordem
    parties: tuple[int, int]
    # O partido do candidato: o líder da chapa
    candidate_party_id: int
    # Nulo quando o líder é um partido do computador
    candidate_id: int | None
    name: str
    # A eleição em que concorre junta
    cycle: int
    formed_on: date
    # Vale no Congresso de `in_force_from` a `ends_on`: da formação, ou da posse em que a
    # federação anterior do partido acaba
    in_force_from: date
    ends_on: date
    status: FederationStatus = FederationStatus.ACTIVE
    left_by: int | None = None
    left_on: date | None = None

    @property
    def proposer_id(self) -> int:
        return self.parties[0]

    def other(self, party_id: int) -> int:
        """O parceiro de `party_id`."""
        return self.parties[1] if party_id == self.parties[0] else self.parties[0]

    def includes(self, party_id: int) -> bool:
        return party_id in self.parties

    def stands(self, day: date) -> bool:
        """A federação está de pé no dia: a rejeição se herda e a chapa é uma só."""
        return (
            self.status is FederationStatus.ACTIVE
            and self.formed_on <= day <= self.ends_on
        )

    def in_congress(self, day: date) -> bool:
        """A lista vale no Congresso no dia: orienta junto e divide o voto."""
        return self.stands(day) and self.in_force_from <= day


@dataclass
class FederationProposal:
    """A proposta de federação de um partido ao outro."""

    id: int
    from_party_id: int
    to_party_id: int
    name: str
    candidate_party_id: int
    candidate_id: int | None
    # A eleição para a qual a federação se forma
    cycle: int
    sent_on: date
    expires_on: date
    status: FederationProposalStatus = FederationProposalStatus.OPEN
    answered_on: date | None = None

    def is_open(self, day: date) -> bool:
        return self.status is FederationProposalStatus.OPEN and day <= self.expires_on

    def involves(self, party_id: int) -> bool:
        return party_id in (self.from_party_id, self.to_party_id)


@dataclass(frozen=True)
class RejectionRow:
    """A rejeição de um grupo: a do proponente hoje, a do parceiro e a que o proponente sente federado."""

    group: VoterGroup
    own: Decimal
    partner: Decimal
    federated: Decimal


@dataclass(frozen=True)
class Preview:
    """O que a federação muda para o proponente antes de enviar a proposta."""

    cycle: int
    # A fatia de cada um nos votos válidos da casa, sem federação, e a barreira
    own_share: Decimal
    partner_share: Decimal
    barrier: Decimal
    # O partido que orienta a bancada, pelas cadeiras de hoje
    orienting_party_id: int
    # Promessas do partido que não lidera e que saem sem custo
    leaving_promises: int
    own_budget: Decimal
    partner_budget: Decimal
    in_force_from: date
    ends_on: date
    # O último dia para o outro partido responder
    answer_until: date
    rejection: tuple[RejectionRow, ...]


def default_name(first_abbr: str, second_abbr: str) -> str:
    """O nome que a federação leva sem escolha: a sigla dos dois ligada por travessão."""
    return f"Federação {first_abbr}\N{EN DASH}{second_abbr}"


def expires_on(sent: date) -> date:
    """O último dia para responder a uma proposta enviada em `sent`."""
    return sent + timedelta(days=PROPOSAL_DAYS)


def orientation_party(parties: tuple[int, int], seats: Mapping[int, int]) -> int:
    """
    O partido que orienta a lista: o de mais cadeiras na Câmara atual; sem cadeira ou com
    empate, o que propôs (o primeiro de `parties`). O outro segue a orientação.
    """
    first, second = parties
    return second if seats.get(second, 0) > seats.get(first, 0) else first


def inherited_rejection(partner: Decimal) -> Decimal:
    """O que o partido soma à própria rejeição num grupo: metade da do parceiro."""
    return partner * INHERITED_REJECTION


def effective_rejection(
    own: Decimal, partners: Iterable[Decimal], limit: Decimal = voters.HUNDRED
) -> Decimal:
    """A rejeição que conta no voto: a própria mais a herdada de cada parceiro, até o teto."""
    return min(limit, own + sum((inherited_rejection(p) for p in partners), Decimal(0)))


# O computador


def shared_flags(a: Iterable[VoterValue] | None, b: Iterable[VoterValue] | None) -> int:
    """Quantas bandeiras os dois partidos têm em comum."""
    return len(set(a or ()) & set(b or ()))


def opposed(a: Iterable[VoterValue] | None, b: Iterable[VoterValue] | None) -> bool:
    """Um partido defende o que o outro rejeita: Mercado livre de um e Justiça social do outro."""
    first, second = set(a or ()), set(b or ())
    low, high = sorted(voters.EXCLUSIVE, key=lambda v: v.value)
    return (low in first and high in second) or (high in first and low in second)


def compatible(a: Iterable[VoterValue] | None, b: Iterable[VoterValue] | None) -> bool:
    """Ao menos uma bandeira em comum e nenhuma oposta."""
    return shared_flags(a, b) >= 1 and not opposed(a, b)


def computer_accepts(
    below_barrier: bool,
    own: Iterable[VoterValue] | None,
    proposer: Iterable[VoterValue] | None,
) -> bool:
    """O computador aceita quando, sozinho, ficaria abaixo da barreira e as bandeiras combinam."""
    return below_barrier and compatible(own, proposer)


def computer_partner(
    flags: Iterable[VoterValue] | None,
    options: Iterable[tuple[int, Iterable[VoterValue] | None, Decimal]],
) -> int | None:
    """
    O parceiro que o computador procura: o de mais bandeiras em comum e nenhuma oposta;
    no empate, o de mais voto, e depois o mais antigo. `options` traz (id, bandeiras, voto).
    """
    fitting = [
        (pid, shared_flags(flags, other), votes)
        for pid, other, votes in options
        if compatible(flags, other)
    ]
    if not fitting:
        return None
    return min(fitting, key=lambda item: (-item[1], -item[2], item[0]))[0]
