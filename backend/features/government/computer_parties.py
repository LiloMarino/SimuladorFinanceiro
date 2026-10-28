"""Os partidos que o computador lança: nome, sigla, candidato e as bandeiras fixas de cada um."""

from dataclasses import dataclass

from backend.core.enum import VoterValue as V


@dataclass(frozen=True)
class ComputerParty:
    name: str
    abbr: str
    candidate: str
    # Três bandeiras, um conjunto diferente em cada partido
    flags: tuple[V, V, V]


COMPUTER_PARTIES: tuple[ComputerParty, ...] = (
    ComputerParty(
        "União do Progresso",
        "UPR",
        "Helena Prado",
        (V.STABILITY, V.DEVELOPMENT, V.PUBLIC_SERVICE),
    ),
    ComputerParty(
        "Movimento Novo Vigor",
        "MNV",
        "Caio Menezes",
        (V.FREE_MARKET, V.DEVELOPMENT, V.SAVER_PROTECTION),
    ),
    ComputerParty(
        "Aliança Cidadã",
        "ACI",
        "Marta Lopes",
        (V.SOCIAL_JUSTICE, V.STABILITY, V.PUBLIC_SERVICE),
    ),
)

COMPUTER_FLAGS = {party.abbr: party.flags for party in COMPUTER_PARTIES}
