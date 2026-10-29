"""
A apuração: intenção de voto pelos grupos de eleitores, 1º turno e a escolha dos
partidos do computador. Tudo aqui é função pura sobre
`GovernmentState`.
"""

from decimal import Decimal

from backend.core.enum import VoterGroup
from backend.features.government import voters
from backend.features.government.computer_parties import (
    COMPUTER_PARTIES,
    ComputerParty,
)
from backend.features.government.state import (
    NEUTRAL_SATISFACTION,
    GovernmentState,
    Party,
)

PARTIES_PER_ELECTION = 3
MAJORITY = Decimal("0.5")


def is_eligible(state: GovernmentState, user_id: int) -> bool:
    """Quem cumpriu dois mandatos seguidos não concorre de novo."""
    term = state.term
    return not (
        term is not None and term.president_id == user_id and term.consecutive >= 2
    )


def vice_of_other(state: GovernmentState, party: Party, user_id: int) -> Party | None:
    """A outra chapa de jogadores em que `user_id` é vice (convidado ou já aceito)."""
    return next(
        (
            p
            for p in state.player_parties()
            if p.id != party.id and p.vice_id == user_id
        ),
        None,
    )


def effective_ticket(
    state: GovernmentState, party: Party
) -> tuple[int | None, int | None]:
    """
    A chapa que vai à urna: o candidato escolhido, ou a fundadora (ou o primeiro filiado
    que pode concorrer) quando ninguém foi indicado; o vice só vale depois de aceitar.
    Quem é vice de outra chapa não concorre por esta.
    """
    if party.is_computer:
        return None, None

    def can_run(user_id: int) -> bool:
        return (
            is_eligible(state, user_id) and vice_of_other(state, party, user_id) is None
        )

    candidate = party.candidate_id
    if candidate is None or not can_run(candidate):
        candidate = next((u for u in _founder_first(party) if can_run(u)), None)
    vice = party.vice_id if party.vice_accepted and party.vice_id != candidate else None
    return candidate, vice


def vice_blocker(state: GovernmentState, party: Party, user_id: int) -> str | None:
    """
    Por que `user_id` não pode ser vice da chapa de `party`; nulo quando pode. O vice é
    qualquer jogador da sala, de outro partido ou sem partido, desde que não seja vice
    nem candidato de outra chapa.
    """
    other = vice_of_other(state, party, user_id)
    if other is not None:
        status = "já é vice" if other.vice_accepted else "já foi convidado para vice"
        return f"{status} do {other.abbr}"
    for rival in state.player_parties():
        if rival.id != party.id and effective_ticket(state, rival)[0] == user_id:
            return f"candidato pelo {rival.abbr}"
    return None


def runs(state: GovernmentState, party: Party) -> bool:
    """O partido do computador sempre concorre; o de jogadores precisa de quem possa ser candidato."""
    return party.is_computer or effective_ticket(state, party)[0] is not None


def intention(state: GovernmentState) -> voters.Vote:
    """O voto de hoje, exato, entre os partidos que concorrem."""
    return voters.vote(
        {p.id: p.standings() for p in state.parties.values() if runs(state, p)}
    )


def start_satisfaction(
    result: voters.Vote, winner_id: int
) -> dict[VoterGroup, Decimal]:
    """
    A satisfação de posse de cada grupo: a fatia dele nos votos válidos do turno que
    decidiu a eleição. Quem ganhou com 54% num grupo começa com 54 nele.
    """
    satisfaction = {}
    for group, gv in result.groups.items():
        valid = sum(gv.shares.values(), Decimal(0))
        satisfaction[group] = (
            gv.shares.get(winner_id, Decimal(0)) * voters.HUNDRED / valid
            if valid > 0
            else NEUTRAL_SATISFACTION
        )
    return satisfaction


def valid_shares(points: dict[int, Decimal]) -> dict[int, Decimal]:
    """Fatia de cada um nos votos válidos; sem nenhum voto, todos empatam."""
    total = sum(points.values(), Decimal(0))
    if not points:
        return {}
    if total <= 0:
        return {pid: Decimal(1) / len(points) for pid in points}
    return {pid: value / total for pid, value in points.items()}


def top_two(points: dict[int, Decimal]) -> list[int]:
    """Os dois mais votados; empate fica com o partido mais antigo."""
    ranked = sorted(points, key=lambda pid: (-points[pid], pid))
    return ranked[:2]


def first_round_winner(shares: dict[int, Decimal]) -> int | None:
    """Mais de 50% dos válidos leva no 1º turno."""
    return next((pid for pid, share in shares.items() if share > MAJORITY), None)


def next_computer_party(state: GovernmentState) -> ComputerParty | None:
    """O próximo partido da lista que ainda não está na disputa."""
    used = {p.abbr for p in state.parties.values()}
    return next((c for c in COMPUTER_PARTIES if c.abbr not in used), None)


def computer_spend(state: GovernmentState, factor: Decimal) -> Decimal:
    """A verba mensal de cada partido do computador: `factor` vezes a média dos de jogadores."""
    players = state.player_parties()
    if not players:
        return Decimal(0)
    average = sum((p.budget for p in players), Decimal(0)) / len(players)
    return average * factor


def _founder_first(party: Party) -> list[int]:
    ordered = list(party.members)
    if party.founder_id in party.members:
        ordered.remove(party.founder_id)
        ordered.insert(0, party.founder_id)
    return ordered
