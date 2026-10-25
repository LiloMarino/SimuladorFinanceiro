"""A página da eleição: o estado político traduzido para o que o jogador vê."""

from datetime import date
from decimal import Decimal

from backend.core.dto.government import (
    DonationDTO,
    ElectionDatesDTO,
    ElectionPanelDTO,
    MyPartyDTO,
    PartyCandidateDTO,
    PartyDTO,
    PartyMemberDTO,
    PartyStandingDTO,
    PlayerStandingDTO,
    PollDTO,
    PollEntryDTO,
    RoundPartyDTO,
    RoundResultDTO,
    RunoffEntryDTO,
    RunoffSimulationDTO,
    TermDTO,
)
from backend.core.dto.simulation import SimulationDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import ElectionPhase, GameType, VicePhase
from backend.core.runtime.user_manager import UserManager
from backend.core.utils import required
from backend.features.government import election
from backend.features.government.calendar import ElectionCycle
from backend.features.government.government_book import GovernmentBook
from backend.features.government.state import (
    GovernmentState,
    Party,
    RoundResult,
    Term,
    Ticket,
)

DEFAULT_COLOR = "chart-1"


def build_panel(
    book: GovernmentBook,
    settings: SimulationDTO,
    users: list[UserDTO],
    viewer: UserDTO,
    today: date,
    networths: dict[int, Decimal],
) -> ElectionPanelDTO:
    state = book.state
    people = {user.id: user for user in users}
    phase = _phase(state, book.cycle(), today)
    # Entre a apuração e a posse o ciclo já avançou: as datas são as da eleição que acabou
    cycle = book.cycle(
        state.cycle - 1 if phase is ElectionPhase.AWAITING_TERM else None
    )
    poll = election.intention(state)
    ranked = sorted(poll.points, key=lambda pid: (-poll.points[pid], pid))

    in_campaign = phase is ElectionPhase.CAMPAIGN
    mine = state.party_of(viewer.id)
    is_founder = mine is not None and mine.founder_id == viewer.id

    return ElectionPanelDTO(
        today=today,
        phase=phase,
        election_year=cycle.first_round.year,
        dates=ElectionDatesDTO(
            campaign_start=cycle.campaign_start,
            ticket_deadline=cycle.ticket_deadline,
            first_round=cycle.first_round,
            runoff=cycle.runoff,
            donation_deadline=cycle.donation_deadline,
            inauguration=cycle.inauguration,
        ),
        parties=[
            _party(state, p, people, poll)
            for p in sorted(state.parties.values(), key=lambda p: p.id)
        ],
        undecided=poll.undecided,
        polls=[
            PollDTO(
                date=entry.day,
                entries=[
                    PollEntryDTO(party_id=pid, points=value)
                    for pid, value in sorted(entry.points.items())
                ],
            )
            for entry in state.polls
        ],
        runoff_simulation=_simulation(state, poll, ranked),
        finalists=state.runoff or [],
        donations=[
            DonationDTO(
                date=d.day,
                nickname=_nickname(people, d.user_id),
                party_id=d.party_id,
                amount=d.amount,
            )
            for d in state.donations
        ],
        my_party=(
            MyPartyDTO(
                party_id=mine.id,
                is_founder=is_founder,
                is_candidate=election.effective_ticket(state, mine)[0] == viewer.id,
                vice=_vice_phase(mine, viewer.id),
                contribution=mine.members[viewer.id],
            )
            if mine is not None
            else None
        ),
        can_found_or_join=in_campaign and mine is None and not viewer.is_bot,
        can_edit_ticket=(
            is_founder
            and phase is not ElectionPhase.BETWEEN_ROUNDS
            and today <= cycle.ticket_deadline
        ),
        can_donate=(
            phase is ElectionPhase.BETWEEN_ROUNDS
            and mine is not None
            and mine.id not in (state.runoff or [])
            and today <= cycle.donation_deadline
        ),
        last_result=_round(state.results[-1], people) if state.results else None,
        results=[_round(r, people) for r in state.results],
        term=build_term(state.term, state, people),
        pending_term=build_term(state.pending_term, state, people),
        decides_match=settings.game_type is GameType.POLITICAL,
        player_standings=_players(state, users, networths),
        party_standings=_parties(state, people, networths),
        computer_budget_factor=settings.computer_difficulty.budget_factor,
    )


def _phase(state: GovernmentState, cycle: ElectionCycle, today: date) -> ElectionPhase:
    if state.runoff is not None:
        return ElectionPhase.BETWEEN_ROUNDS
    if state.pending_term is not None:
        return ElectionPhase.AWAITING_TERM
    if cycle.campaign_start <= today < cycle.first_round:
        return ElectionPhase.CAMPAIGN
    if state.term is not None:
        return ElectionPhase.TERM
    return ElectionPhase.BEFORE_CAMPAIGN


def _nickname(people: dict[int, UserDTO], user_id: int | None) -> str:
    user = people.get(user_id) if user_id is not None else None
    return user.nickname if user else "?"


def _color(user_id: int) -> str:
    return UserManager.get_color(user_id) or DEFAULT_COLOR


def _vice_phase(party: Party, user_id: int) -> VicePhase:
    if party.vice_id != user_id:
        return VicePhase.NONE
    return VicePhase.ACCEPTED if party.vice_accepted else VicePhase.PENDING


def _person(
    people: dict[int, UserDTO], user_id: int | None
) -> PartyCandidateDTO | None:
    if user_id is None:
        return None
    user = people.get(user_id)
    return PartyCandidateDTO(
        nickname=user.nickname if user else "?",
        name=_nickname(people, user_id),
        color=_color(user_id),
    )


def _candidate(
    people: dict[int, UserDTO],
    candidate_id: int | None,
    computer_name: str | None,
) -> PartyCandidateDTO | None:
    if computer_name is not None:
        return PartyCandidateDTO(nickname=None, name=computer_name, color=None)
    return _person(people, candidate_id)


def _party(
    state: GovernmentState,
    party: Party,
    people: dict[int, UserDTO],
    poll: election.Intention,
) -> PartyDTO:
    candidate_id, vice_id = election.effective_ticket(state, party)
    vice_phase = VicePhase.NONE
    if party.vice_id is not None and not party.is_computer:
        vice_phase = VicePhase.ACCEPTED if party.vice_accepted else VicePhase.PENDING
    return PartyDTO(
        id=party.id,
        name=party.name,
        abbr=party.abbr,
        color=party.color,
        is_computer=party.is_computer,
        promise=party.promise,
        founder=(
            _nickname(people, party.founder_id)
            if party.founder_id is not None
            else None
        ),
        founded=party.founded,
        members=[
            PartyMemberDTO(
                nickname=_nickname(people, user_id),
                color=_color(user_id),
                contribution=contribution,
                is_founder=user_id == party.founder_id,
                is_candidate=user_id == candidate_id,
                vice=_vice_phase(party, user_id),
            )
            for user_id, contribution in party.members.items()
        ],
        budget=party.budget,
        spent=party.spent,
        intention_points=poll.points.get(party.id, Decimal(0)),
        valid_share=poll.valid_shares.get(party.id, Decimal(0)),
        candidate=_candidate(people, candidate_id, party.candidate_name),
        # O convidado aparece na chapa mesmo antes de aceitar
        vice=_person(people, party.vice_id if party.vice_id is not None else vice_id),
        vice_phase=vice_phase,
        ticket_chosen=party.candidate_id is not None,
    )


def _simulation(
    state: GovernmentState, poll: election.Intention, ranked: list[int]
) -> RunoffSimulationDTO | None:
    """O 2º turno como seria hoje, entre os dois primeiros da pesquisa."""
    if len(ranked) < 2:
        return None
    finalists = ranked[:2]
    points = {pid: state.parties[pid].points for pid in poll.points}
    return _runoff_dto(state, points, finalists, {})


def _runoff_dto(
    state: GovernmentState,
    points: dict[int, Decimal],
    finalists: list[int],
    donations: dict[int, Decimal],
) -> RunoffSimulationDTO:
    result = election.runoff(state, points, finalists)
    entries = []
    for pid, value in sorted(points.items()):
        is_finalist = pid in finalists
        entries.append(
            RunoffEntryDTO(
                party_id=pid,
                own_points=value,
                received_points=result.votes[pid] - value
                if is_finalist
                else Decimal(0),
                share=result.shares.get(pid, Decimal(0)),
                transfer_to=None if is_finalist else result.transfers[pid],
                donated=donations.get(pid, Decimal(0)),
            )
        )
    return RunoffSimulationDTO(
        finalists=finalists, entries=entries, winner=result.winner_id
    )


def _round(result: RoundResult, people: dict[int, UserDTO]) -> RoundResultDTO:
    parties = [
        _round_party(pid, ticket, result, people)
        for pid, ticket in sorted(result.tickets.items())
    ]
    runoff = None
    if result.round == 2:
        runoff = _stored_runoff(result)
    return RoundResultDTO(
        date=result.day,
        election_year=result.day.year,
        round=result.round,
        parties=parties,
        finalists=result.finalists,
        winner=result.winner_id,
        runoff=runoff,
    )


def _stored_runoff(result: RoundResult) -> RunoffSimulationDTO:
    """O 2º turno como foi apurado: os pontos guardados já trazem a transferência."""
    entries = [
        RunoffEntryDTO(
            party_id=pid,
            own_points=result.points[pid]
            - sum(
                (
                    result.points[src]
                    for src, dst in result.transfers.items()
                    if dst == pid
                ),
                Decimal(0),
            ),
            received_points=sum(
                (
                    result.points[src]
                    for src, dst in result.transfers.items()
                    if dst == pid
                ),
                Decimal(0),
            ),
            share=result.shares.get(pid, Decimal(0)),
            transfer_to=result.transfers.get(pid),
            donated=result.donations.get(pid, Decimal(0)),
        )
        for pid in sorted(result.points)
    ]
    return RunoffSimulationDTO(
        finalists=result.finalists, entries=entries, winner=required(result.winner_id)
    )


def _round_party(
    pid: int, ticket: Ticket, result: RoundResult, people: dict[int, UserDTO]
) -> RoundPartyDTO:
    return RoundPartyDTO(
        party_id=pid,
        abbr=ticket.abbr,
        name=ticket.name,
        color=ticket.color,
        is_computer=ticket.is_computer,
        candidate=_candidate(people, ticket.candidate_id, ticket.candidate_name),
        vice=_person(people, ticket.vice_id),
        points=result.points.get(pid, Decimal(0)),
        share=result.shares.get(pid, Decimal(0)),
    )


def build_term(
    term: Term | None, state: GovernmentState, people: dict[int, UserDTO]
) -> TermDTO | None:
    if term is None:
        return None
    party = state.parties.get(term.party_id) if term.party_id is not None else None
    return TermDTO(
        party_id=term.party_id,
        president=_candidate(
            people,
            term.president_id,
            party.candidate_name if party and party.is_computer else None,
        ),
        vice=_person(people, term.vice_id),
        start=term.start,
        consecutive=term.consecutive,
        promise=term.promise,
        succession=term.succession,
    )


def _players(
    state: GovernmentState, users: list[UserDTO], networths: dict[int, Decimal]
) -> list[PlayerStandingDTO]:
    standings = []
    for user in users:
        party = state.party_of(user.id)
        standings.append(
            PlayerStandingDTO(
                nickname=user.nickname,
                color=_color(user.id),
                party_id=party.id if party else None,
                total_networth=networths.get(user.id, Decimal(0)),
            )
        )
    return sorted(standings, key=lambda s: s.total_networth, reverse=True)


def _parties(
    state: GovernmentState, people: dict[int, UserDTO], networths: dict[int, Decimal]
) -> list[PartyStandingDTO]:
    """O patrimônio do partido é a soma do dos filiados; o do computador fica fora."""
    standings = [
        PartyStandingDTO(
            party_id=p.id,
            abbr=p.abbr,
            name=p.name,
            color=p.color,
            members=[_nickname(people, u) for u in p.members],
            total_networth=party_networth(p, networths),
        )
        for p in state.player_parties()
    ]
    return sorted(standings, key=lambda s: s.total_networth, reverse=True)


def party_networth(party: Party, networths: dict[int, Decimal]) -> Decimal:
    return sum((networths.get(u, Decimal(0)) for u in party.members), Decimal(0))
