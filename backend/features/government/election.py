"""
A apuração: intenção de voto a partir do apoio, 1º turno, transferência de votos no 2º
e a escolha dos partidos do computador. Tudo aqui é função pura sobre `GovernmentState`.
"""

from dataclasses import dataclass
from decimal import Decimal

from backend.features.government.state import (
    ELECTORATE,
    GovernmentState,
    Party,
)

PARTIES_PER_ELECTION = 3
PROMISE_BANDS = (1, 2, 3, 4, 5)
MAJORITY = Decimal("0.5")

# Quem o computador lança: nome do partido, sigla e candidato
COMPUTER_PARTIES: tuple[tuple[str, str, str], ...] = (
    ("União do Progresso", "UPR", "Helena Prado"),
    ("Movimento Novo Vigor", "MNV", "Caio Menezes"),
    ("Aliança Cidadã", "ACI", "Marta Lopes"),
)


@dataclass(frozen=True)
class Intention:
    """Em cada 100 eleitores, quantos votariam em cada partido hoje."""

    # Pontos por partido; passam de 100 só se a soma passar, e aí é reescalada
    points: dict[int, Decimal]
    undecided: Decimal
    # Fatia de cada partido nos votos válidos (os dados a algum partido)
    valid_shares: dict[int, Decimal]


@dataclass(frozen=True)
class Runoff:
    """A disputa entre dois partidos, com os votos de quem saiu já transferidos."""

    votes: dict[int, Decimal]
    shares: dict[int, Decimal]
    transfers: dict[int, int]
    winner_id: int


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


def intention(state: GovernmentState) -> Intention:
    parties = [p for p in state.parties.values() if runs(state, p)]
    total = sum((p.points for p in parties), Decimal(0))
    scale = ELECTORATE / total if total > ELECTORATE else Decimal(1)
    points = {p.id: p.points * scale for p in parties}
    shown = sum(points.values(), Decimal(0))
    return Intention(
        points=points,
        undecided=max(ELECTORATE - shown, Decimal(0)),
        valid_shares=valid_shares({p.id: p.points for p in parties}),
    )


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


def runoff(
    state: GovernmentState, points: dict[int, Decimal], finalists: list[int]
) -> Runoff:
    """
    Os eleitores de quem saiu vão para o finalista com a promessa mais parecida; em
    distância igual, para o que tem mais votos próprios.
    """
    votes = {pid: points[pid] for pid in finalists}
    transfers: dict[int, int] = {}
    for pid, value in points.items():
        if pid in finalists:
            continue
        target = min(
            finalists,
            key=lambda f: (
                abs(state.parties[f].promise - state.parties[pid].promise),
                -points[f],
                f,
            ),
        )
        transfers[pid] = target
        votes[target] += value
    shares = valid_shares(votes)
    winner = min(finalists, key=lambda f: (-votes[f], -points[f], f))
    return Runoff(votes, shares, transfers, winner)


def pick_promise(parties: list[Party]) -> int:
    """
    A faixa da régua mais longe de todos os partidos que já existem; entre faixas
    igualmente longe, a que tem menos partidos, e depois a de número menor.
    """
    taken = [p.promise for p in parties]
    if not taken:
        return PROMISE_BANDS[len(PROMISE_BANDS) // 2]
    return min(
        PROMISE_BANDS,
        key=lambda band: (
            -min(abs(band - t) for t in taken),
            sum(1 for t in taken if t == band),
            band,
        ),
    )


def next_computer_party(state: GovernmentState) -> tuple[str, str, str] | None:
    """O próximo partido da lista que ainda não está na disputa."""
    used = {p.abbr for p in state.parties.values()}
    return next((c for c in COMPUTER_PARTIES if c[1] not in used), None)


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
