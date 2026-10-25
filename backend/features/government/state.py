"""
O estado político da partida é o replay dos eventos: quem fundou, filiou, contribuiu,
quanto cada partido já tem de apoio, o resultado de cada turno, o governo em vigor, a
fila do Congresso e a aprovação. `apply` é o único lugar que muda o estado, na partida
rodando e na retomada.
"""

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal

from backend.core.dto.events.government import GovernmentEventDTO
from backend.core.enum import GovernmentEventType as Event
from backend.core.enum import MeasureKind, MeasureStatus
from backend.core.utils import required

# Pontos de intenção de voto por gasto: R$ 8 mil num mês dão √8000 ÷ 64 = 1,4 ponto
# (de 100 eleitores). O apoio rende pela raiz quadrada, então dobrar a verba não
# dobra os votos.
SQRT_DIVISOR = Decimal(64)
ELECTORATE = Decimal(100)
# A medida aprovada vale depois da noventena
VIGENCE_DAYS = 90


def vote_points(amount: Decimal) -> Decimal:
    """Pontos de intenção de voto que um gasto de `amount` rende."""
    return amount.sqrt() / SQRT_DIVISOR if amount > 0 else Decimal(0)


@dataclass
class Party:
    id: int
    name: str
    abbr: str
    # Cor escolhida pelo fundador (hex); o partido do computador não tem
    color: str | None
    # Posição na régua de 1 (impostos baixos) a 5 (gasto alto)
    promise: int
    founder_id: int | None
    is_computer: bool
    founded: date
    # Nome do candidato do partido do computador
    candidate_name: str | None = None
    # Filiados na ordem de entrada e a contribuição mensal de cada um
    members: dict[int, Decimal] = field(default_factory=dict)
    candidate_id: int | None = None
    vice_id: int | None = None
    vice_accepted: bool = False
    # Pontos de intenção de voto e gasto acumulados na campanha em curso
    points: Decimal = Decimal(0)
    spent: Decimal = Decimal(0)

    @property
    def budget(self) -> Decimal:
        """Verba por mês: a soma das contribuições."""
        return sum(self.members.values(), Decimal(0))


@dataclass(frozen=True)
class Poll:
    day: date
    points: dict[int, Decimal]


@dataclass(frozen=True)
class Donation:
    day: date
    user_id: int
    party_id: int
    amount: Decimal


@dataclass(frozen=True)
class Ticket:
    """A chapa e os dados do partido na apuração, guardados como estavam."""

    candidate_id: int | None
    vice_id: int | None
    abbr: str
    name: str
    color: str | None
    is_computer: bool
    candidate_name: str | None


@dataclass(frozen=True)
class RoundResult:
    """O que um turno apurou, guardado como saiu (os partidos mudam depois)."""

    day: date
    cycle: int
    round: int
    # Pontos de cada partido na apuração; no 2º turno, já com a transferência
    points: dict[int, Decimal]
    shares: dict[int, Decimal]
    finalists: list[int]
    winner_id: int | None
    # Quem concorreu e a chapa de cada um
    tickets: dict[int, Ticket]
    # No 2º turno: para qual finalista foram os eleitores de cada partido que saiu
    transfers: dict[int, int]
    donations: dict[int, Decimal]


@dataclass(frozen=True)
class Term:
    """O governo em vigor; sem partido é o governo do computador."""

    party_id: int | None
    president_id: int | None
    vice_id: int | None
    start: date
    # Mandatos seguidos do mesmo presidente: o 2º é o último
    consecutive: int
    # A promessa do partido na campanha, na régua de 1 a 5
    promise: int | None = None
    # O vice assumiu depois de um impeachment, ou o computador ficou no lugar
    succession: bool = False


@dataclass
class Measure:
    """Uma proposta do presidente ao Congresso e o que aconteceu com ela."""

    id: int
    kind: MeasureKind
    # A alíquota (0.20), o teto em reais ou os pontos somados, conforme o tipo
    value: Decimal | None
    # O que a medida muda, como estava no dia da proposta
    before: Decimal | None
    sector: str | None
    segment: str | None
    proposer_id: int
    # Início do governo que propôs: a marca e o efeito na aprovação contam por governo
    term_start: date
    proposed: date
    status: MeasureStatus = MeasureStatus.QUEUED
    decided: date | None = None
    # A chance que a medida tinha no voto
    chance: Decimal | None = None
    effective: date | None = None


@dataclass(frozen=True)
class ApprovalPoint:
    day: date
    value: int


@dataclass(frozen=True)
class Impeachment:
    day: date
    president_id: int | None
    party_id: int | None
    # O vice que assumiu; nulo quando o computador ficou no lugar
    successor_id: int | None


@dataclass
class GovernmentState:
    parties: dict[int, Party] = field(default_factory=dict)
    next_party_id: int = 1
    # Eleições já concluídas: o índice do ciclo em curso
    cycle: int = 0
    last_collection: date | None = None
    polls: list[Poll] = field(default_factory=list)
    donations: list[Donation] = field(default_factory=list)
    results: list[RoundResult] = field(default_factory=list)
    # Finalistas enquanto o 2º turno não acontece
    runoff: list[int] | None = None
    # O eleito que espera a posse
    pending_term: Term | None = None
    term: Term | None = None
    measures: dict[int, Measure] = field(default_factory=dict)
    next_measure_id: int = 1
    # A aprovação medida no fechamento de cada mês do governo em curso
    approvals: list[ApprovalPoint] = field(default_factory=list)
    # Meses seguidos abaixo do piso; o impeachment vem quando chega ao limite
    low_streak: int = 0
    last_measured: date | None = None
    impeachments: list[Impeachment] = field(default_factory=list)

    def party_of(self, user_id: int) -> Party | None:
        return next(
            (p for p in self.parties.values() if user_id in p.members),
            None,
        )

    def player_parties(self) -> list[Party]:
        return [p for p in self.parties.values() if not p.is_computer]

    def computer_parties(self) -> list[Party]:
        return [p for p in self.parties.values() if p.is_computer]


def replay(events: Iterable[GovernmentEventDTO]) -> GovernmentState:
    state = GovernmentState()
    for event in events:
        apply(state, event)
    return state


def apply(state: GovernmentState, event: GovernmentEventDTO) -> None:
    p = event.payload
    day = event.event_date
    match event.event_type:
        case Event.PARTY_FOUNDED:
            party_id = _int(p, "party_id")
            founder = _int(p, "founder_id")
            state.parties[party_id] = Party(
                id=party_id,
                name=_str(p, "name"),
                abbr=_str(p, "abbr"),
                color=_str(p, "color"),
                promise=_int(p, "promise"),
                founder_id=founder,
                is_computer=False,
                founded=day,
                members={founder: _money(p, "contribution")},
            )
            state.next_party_id = max(state.next_party_id, party_id + 1)
        case Event.COMPUTER_PARTY_ADDED:
            party_id = _int(p, "party_id")
            state.parties[party_id] = Party(
                id=party_id,
                name=_str(p, "name"),
                abbr=_str(p, "abbr"),
                color=None,
                promise=_int(p, "promise"),
                founder_id=None,
                is_computer=True,
                founded=day,
                candidate_name=_str(p, "candidate_name"),
            )
            state.next_party_id = max(state.next_party_id, party_id + 1)
        case Event.COMPUTER_PARTY_REMOVED:
            state.parties.pop(_int(p, "party_id"), None)
        case Event.PARTY_JOINED:
            state.parties[_int(p, "party_id")].members[_int(p, "user_id")] = _money(
                p, "contribution"
            )
        case Event.PARTY_LEFT | Event.MEMBER_EXPELLED:
            _remove_member(state, _int(p, "user_id"))
        case Event.CONTRIBUTION_SET:
            user_id = _int(p, "user_id")
            party = state.party_of(user_id)
            if party is not None:
                party.members[user_id] = _money(p, "contribution")
        case Event.TICKET_SET:
            party = state.parties[_int(p, "party_id")]
            party.candidate_id = _int(p, "candidate_id")
            party.vice_id = _opt_int(p, "vice_id")
            party.vice_accepted = bool(p.get("vice_accepted", False))
        case Event.VICE_ANSWERED:
            party = state.parties[_int(p, "party_id")]
            if p["accepted"]:
                party.vice_accepted = True
            else:
                party.vice_id = None
                party.vice_accepted = False
        case Event.CAMPAIGN_SPENT:
            for party_id, amount in _money_map(p, "spent").items():
                party = state.parties.get(party_id)
                if party is not None:
                    party.spent += amount
                    party.points += vote_points(amount)
            state.last_collection = date.fromisoformat(_str(p, "month"))
            state.polls.append(
                Poll(day, {pid: party.points for pid, party in state.parties.items()})
            )
        case Event.DONATION_MADE:
            party_id = _int(p, "party_id")
            amount = _money(p, "amount")
            party = state.parties[party_id]
            party.spent += amount
            party.points += vote_points(amount)
            state.donations.append(Donation(day, _int(p, "user_id"), party_id, amount))
        case Event.ELECTION_ROUND:
            _apply_round(state, event)
        case Event.TERM_STARTED:
            state.term = Term(
                party_id=_opt_int(p, "party_id"),
                president_id=_opt_int(p, "president_id"),
                vice_id=_opt_int(p, "vice_id"),
                start=day,
                consecutive=_int(p, "consecutive"),
                promise=_opt_int(p, "promise"),
            )
            state.pending_term = None
            _reset_government(state)
        case Event.MEASURE_PROPOSED:
            measure_id = _int(p, "measure_id")
            state.measures[measure_id] = Measure(
                id=measure_id,
                kind=MeasureKind(_str(p, "kind")),
                value=_opt_money(p, "value"),
                before=_opt_money(p, "before"),
                sector=_opt_str(p, "sector"),
                segment=_opt_str(p, "segment"),
                proposer_id=_int(p, "proposer_id"),
                term_start=required(state.term).start,
                proposed=day,
            )
            state.next_measure_id = max(state.next_measure_id, measure_id + 1)
        case Event.MEASURE_WITHDRAWN:
            state.measures[_int(p, "measure_id")].status = MeasureStatus.WITHDRAWN
        case Event.MEASURE_VOTED:
            measure = state.measures[_int(p, "measure_id")]
            measure.decided = day
            measure.chance = _money(p, "chance")
            if p["approved"]:
                measure.status = MeasureStatus.APPROVED
                measure.effective = day + timedelta(days=VIGENCE_DAYS)
            else:
                measure.status = MeasureStatus.REJECTED
        case Event.APPROVAL_MEASURED:
            state.approvals.append(ApprovalPoint(day, _int(p, "value")))
            state.low_streak = _int(p, "low_streak")
            state.last_measured = date.fromisoformat(_str(p, "month"))
        case Event.IMPEACHED:
            _apply_impeachment(state, event)


def _reset_government(state: GovernmentState) -> None:
    """Um governo novo começa sem a fila do anterior e sem o histórico de aprovação."""
    for measure in state.measures.values():
        if measure.status is MeasureStatus.QUEUED:
            measure.status = MeasureStatus.DROPPED
    state.approvals = []
    state.low_streak = 0


def _apply_impeachment(state: GovernmentState, event: GovernmentEventDTO) -> None:
    term = required(state.term)
    successor = _opt_int(event.payload, "successor_id")
    state.impeachments.append(
        Impeachment(
            day=event.event_date,
            president_id=term.president_id,
            party_id=term.party_id,
            successor_id=successor,
        )
    )
    state.term = Term(
        party_id=term.party_id if successor is not None else None,
        president_id=successor,
        vice_id=None,
        start=event.event_date,
        consecutive=1,
        promise=term.promise if successor is not None else None,
        succession=True,
    )
    _reset_government(state)


def _remove_member(state: GovernmentState, user_id: int) -> None:
    party = state.party_of(user_id)
    if party is None:
        return
    del party.members[user_id]
    if not party.members:
        del state.parties[party.id]
        return
    # A fundação passa ao filiado mais antigo que ficou
    if party.founder_id == user_id:
        party.founder_id = next(iter(party.members))
    if party.candidate_id == user_id:
        party.candidate_id = None
    if party.vice_id == user_id:
        party.vice_id = None
        party.vice_accepted = False


def _apply_round(state: GovernmentState, event: GovernmentEventDTO) -> None:
    p = event.payload
    tickets = {
        int(pid): Ticket(
            candidate_id=_opt_int(t, "candidate_id"),
            vice_id=_opt_int(t, "vice_id"),
            abbr=_str(t, "abbr"),
            name=_str(t, "name"),
            color=_opt_str(t, "color"),
            is_computer=bool(t["is_computer"]),
            candidate_name=_opt_str(t, "candidate_name"),
        )
        for pid, t in _dict(p, "tickets").items()
    }
    winner = _opt_int(p, "winner_id")
    result = RoundResult(
        day=event.event_date,
        cycle=_int(p, "cycle"),
        round=_int(p, "round"),
        points=_money_map(p, "points"),
        shares=_money_map(p, "shares"),
        finalists=[int(x) for x in _list(p, "finalists")],  # type: ignore[call-overload]
        winner_id=winner,
        tickets=tickets,
        transfers={int(a): int(b) for a, b in _dict(p, "transfers").items()},  # type: ignore[call-overload]
        donations=_money_map(p, "donations"),
    )
    state.results.append(result)
    # Sem finalistas ninguém concorreu: o governo continua do computador
    if winner is None and result.finalists:
        state.runoff = result.finalists
        return

    ticket = tickets.get(winner) if winner is not None else None
    previous = state.term
    president = ticket.candidate_id if ticket else None
    same_president = (
        previous is not None
        and president is not None
        and previous.president_id == president
    )
    winner_party = state.parties.get(winner) if winner is not None else None
    state.pending_term = Term(
        party_id=winner,
        president_id=president,
        vice_id=ticket.vice_id if ticket else None,
        start=date(event.event_date.year + 1, 1, 1),
        consecutive=(previous.consecutive + 1 if previous and same_president else 1),
        promise=winner_party.promise if winner_party else None,
    )
    # A campanha seguinte recomeça do zero: os partidos ficam, o apoio não
    state.runoff = None
    state.cycle += 1
    state.polls = []
    state.donations = []
    for party in state.parties.values():
        party.points = Decimal(0)
        party.spent = Decimal(0)


def _int(p: dict[str, object], key: str) -> int:
    return int(p[key])  # type: ignore[call-overload]


def _opt_int(p: dict[str, object], key: str) -> int | None:
    value = p.get(key)
    return None if value is None else int(value)  # type: ignore[call-overload]


def _str(p: dict[str, object], key: str) -> str:
    return str(p[key])


def _opt_money(p: dict[str, object], key: str) -> Decimal | None:
    value = p.get(key)
    return None if value is None else Decimal(str(value))


def _opt_str(p: dict[str, object], key: str) -> str | None:
    value = p.get(key)
    return None if value is None else str(value)


def _money(p: dict[str, object], key: str) -> Decimal:
    return Decimal(str(p[key]))


def _dict(p: dict[str, object], key: str) -> dict[str, dict[str, object]]:
    return p[key]  # type: ignore[return-value]


def _list(p: dict[str, object], key: str) -> list[object]:
    return p[key]  # type: ignore[return-value]


def _money_map(p: dict[str, object], key: str) -> dict[int, Decimal]:
    return {int(k): Decimal(str(v)) for k, v in p[key].items()}  # type: ignore[attr-defined]
