"""
A preparação que cada jogador deixa no lobby: fundar um partido, filiar-se ao de outro jogador,
a chapa, o vice e a federação com o partido de outro fundador. Ela vira um evento da partida: os partidos nascem no 1º dia, e a chapa entra
quando a campanha abre.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from backend.core import repository
from backend.core.dto.events.government import GovernmentEventDTO
from backend.core.enum import GovernmentEventType, VoterValue


@dataclass(frozen=True)
class PartyIdentity:
    name: str
    abbr: str
    color: str
    flags: tuple[VoterValue, ...]


@dataclass(frozen=True)
class Prepared:
    """O que um jogador preparou; `found` e `join_id` não vêm juntos."""

    user_id: int
    # A identidade do partido que o jogador funda
    found: PartyIdentity | None = None
    # O fundador em cujo partido o jogador entra
    join_id: int | None = None
    # O candidato da chapa de quem funda: ele mesmo ou um filiado
    candidate_id: int | None = None
    vice_id: int | None = None
    vice_accepted: bool = False
    # O jogador que recusou o convite, ou que aceitou outra chapa; fica até convidar de novo ou retirar
    vice_declined_id: int | None = None
    # A contribuição mensal salva no perfil, com que o jogador nasce no partido
    contribution: Decimal = Decimal(0)
    # A federação que o fundador propôs a outro fundador: o parceiro, o nome e o candidato (de qualquer um dos dois partidos); vale quando o parceiro aceita
    federation_partner_id: int | None = None
    federation_name: str | None = None
    federation_candidate_id: int | None = None
    federation_accepted: bool = False

    def to_payload(self) -> dict[str, object]:
        return {
            "user_id": self.user_id,
            "found": None
            if self.found is None
            else {
                "name": self.found.name,
                "abbr": self.found.abbr,
                "color": self.found.color,
                "flags": [v.value for v in self.found.flags],
            },
            "join_id": self.join_id,
            "candidate_id": self.candidate_id,
            "vice_id": self.vice_id,
            "vice_accepted": self.vice_accepted,
            "vice_declined_id": self.vice_declined_id,
            "contribution": str(self.contribution),
            "federation_partner_id": self.federation_partner_id,
            "federation_name": self.federation_name,
            "federation_candidate_id": self.federation_candidate_id,
            "federation_accepted": self.federation_accepted,
        }

    @classmethod
    def from_payload(cls, data: dict[str, object]) -> "Prepared":
        found = data.get("found")
        return cls(
            user_id=int(data["user_id"]),  # type: ignore[call-overload]
            found=None
            if found is None
            else PartyIdentity(
                name=str(found["name"]),  # type: ignore[index]
                abbr=str(found["abbr"]),  # type: ignore[index]
                color=str(found["color"]),  # type: ignore[index]
                flags=tuple(VoterValue(str(v)) for v in found["flags"]),  # type: ignore[index]
            ),
            join_id=_opt(data, "join_id"),
            candidate_id=_opt(data, "candidate_id"),
            vice_id=_opt(data, "vice_id"),
            vice_accepted=bool(data.get("vice_accepted", False)),
            vice_declined_id=_opt(data, "vice_declined_id"),
            contribution=Decimal(str(data.get("contribution", "0"))),
            federation_partner_id=_opt(data, "federation_partner_id"),
            federation_name=None
            if data.get("federation_name") is None
            else str(data["federation_name"]),
            federation_candidate_id=_opt(data, "federation_candidate_id"),
            federation_accepted=bool(data.get("federation_accepted", False)),
        )


def _opt(data: dict[str, object], key: str) -> int | None:
    value = data.get(key)
    return None if value is None else int(value)  # type: ignore[call-overload]


def record(simulation_id: int, day: date, players: list[Prepared]) -> None:
    """Grava a preparação da sala na partida que nasce; sem ninguém preparado, não grava nada."""
    if not players:
        return
    repository.government.insert(
        GovernmentEventDTO(
            simulation_id=simulation_id,
            event_type=GovernmentEventType.PARTIES_PREPARED,
            payload={"players": [p.to_payload() for p in players]},
            event_date=day,
        )
    )
