"""A página da eleição: o estado político traduzido para o que o jogador vê."""

from datetime import date
from decimal import Decimal

from backend.core.dto.government import (
    DonationDTO,
    ElectionDatesDTO,
    ElectionPanelDTO,
    ElectorateRowDTO,
    GroupPollDTO,
    GroupScoreDTO,
    MyPartyDTO,
    MyViceDTO,
    PartyCandidateDTO,
    PartyDTO,
    PartyMemberDTO,
    PartyStandingDTO,
    PlayerStandingDTO,
    PollDTO,
    PollEntryDTO,
    ProfileMoveDTO,
    RoundPartyDTO,
    RoundResultDTO,
    RunoffEntryDTO,
    RunoffSimulationDTO,
    TermDTO,
    ValueMoveDTO,
    ValueScoreDTO,
    ViceOptionDTO,
    VoterGroupDTO,
)
from backend.core.dto.simulation import SimulationDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import ElectionPhase, GameType, VicePhase, VoterGroup, VoterValue
from backend.core.runtime.user_manager import UserManager
from backend.core.utils import required
from backend.features.government import election, voters
from backend.features.government import measures as rules
from backend.features.government.calendar import ElectionCycle
from backend.features.government.government_book import GovernmentBook
from backend.features.government.state import (
    GovernmentState,
    Party,
    Poll,
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
    # Os números de campanha chegam a hoje com a queda do tempo aplicada
    state.advance(today)
    people = {user.id: user for user in users}
    phase = _phase(state, book.cycle(), today)
    # Entre a apuração e a posse o ciclo já avançou: as datas são as da eleição que acabou
    cycle = book.cycle(
        state.cycle - 1 if phase is ElectionPhase.AWAITING_TERM else None
    )
    published = [_published(p, book.seed, settings.poll_margin) for p in state.polls]
    latest = published[-1] if published else None

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
        groups=[_group(g) for g in VoterGroup],
        affinity_base=voters.AFFINITY_BASE,
        radar_neutral=voters.RADAR_NEUTRAL,
        radar_flag=voters.RADAR_FLAG,
        poll_margin=settings.poll_margin,
        parties=[
            _party(state, p, people, latest)
            for p in sorted(state.parties.values(), key=lambda p: p.id)
        ],
        undecided=latest.undecided if latest else voters.HUNDRED,
        polls=[
            _poll(poll.day, vote, settings.poll_margin)
            for poll, vote in zip(state.polls, published, strict=True)
        ],
        electorate=_electorate(state, mine) if mine is not None else [],
        runoff_simulation=_simulation(state, latest),
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
                contribution=mine.members[viewer.id],
            )
            if mine is not None
            else None
        ),
        my_vice=_my_vice(state, viewer.id),
        vice_options=_vice_options(state, mine, users) if is_founder else [],
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
        last_result=(
            _round(state.results[-1], state, people) if state.results else None
        ),
        results=[_round(r, state, people) for r in state.results],
        term=build_term(state.term, state, people),
        pending_term=build_term(state.pending_term, state, people),
        decides_match=settings.game_type is GameType.POLITICAL,
        player_standings=_players(state, users, networths),
        party_standings=_parties(state, people, networths),
        computer_budget_factor=settings.computer_difficulty.budget_factor,
    )


def _scores(scores: dict[VoterValue, Decimal]) -> list[ValueScoreDTO]:
    return [ValueScoreDTO(value=v, score=scores[v]) for v in VoterValue]


def _affinity(radar: dict[VoterValue, Decimal]) -> list[GroupScoreDTO]:
    return [GroupScoreDTO(group=g, score=voters.affinity(g, radar)) for g in VoterGroup]


def _group(group: VoterGroup) -> VoterGroupDTO:
    positions = voters.POSITIONS[group]
    return VoterGroupDTO(
        group=group,
        weight=voters.WEIGHTS[group],
        margin=voters.MARGINS[group],
        readings=list(voters.READINGS[group]),
        wants=_scores({v: (pos + 1) * 50 for v, pos in positions.items()}),
        flag_affinity=_scores(
            {v: voters.AFFINITY_PER_POSITION * pos for v, pos in positions.items()}
        ),
    )


def _published(poll: Poll, seed: int, with_margin: bool) -> voters.Vote:
    """
    A pesquisa como sai: o voto de cada grupo com o erro sorteado dentro da margem do
    grupo, e o total somado deles. Assim o total e as barras dos grupos batem, e o erro
    do total fica perto dos 3 pontos que a pesquisa anuncia.
    """
    exact = voters.vote(poll.standings)
    if not with_margin:
        return exact
    groups = {}
    for group, result in exact.groups.items():
        shares = {
            pid: voters.published(
                value, voters.MARGINS[group], seed, poll.day, group.value, pid
            )
            for pid, value in result.shares.items()
        }
        rest = voters.HUNDRED - sum(shares.values(), Decimal(0))
        groups[group] = voters.GroupVote(shares, max(Decimal(0), rest))
    return voters.combine(groups)


def _entries(points: dict[int, Decimal]) -> list[PollEntryDTO]:
    return [
        PollEntryDTO(party_id=pid, points=value)
        for pid, value in sorted(points.items())
    ]


def _poll(day: date, vote: voters.Vote, with_margin: bool) -> PollDTO:
    return PollDTO(
        date=day,
        entries=_entries(vote.total),
        undecided=vote.undecided,
        margin=voters.TOTAL_MARGIN if with_margin else 0,
        groups=[
            GroupPollDTO(
                group=group,
                entries=_entries(result.shares),
                undecided=result.undecided,
                margin=voters.MARGINS[group] if with_margin else 0,
            )
            for group, result in vote.groups.items()
        ],
    )


def _electorate(state: GovernmentState, party: Party) -> list[ElectorateRowDTO]:
    """O apoio e a rejeição exatos do partido em cada grupo e a mudança entre as duas últimas pesquisas."""
    history = [p.standings[party.id] for p in state.polls if party.id in p.standings]
    before, after = (history[-2], history[-1]) if len(history) >= 2 else (None, None)
    rows = []
    for group in VoterGroup:
        now = party.standing(group)
        rows.append(
            ElectorateRowDTO(
                group=group,
                affinity=voters.affinity(group, party.radar),
                support=now.support,
                rejection=now.rejection,
                support_change=(
                    after[group].support - before[group].support
                    if before and after
                    else None
                ),
                rejection_change=(
                    after[group].rejection - before[group].rejection
                    if before and after
                    else None
                ),
            )
        )
    return rows


def _moves(state: GovernmentState, party: Party) -> list[ProfileMoveDTO]:
    return [
        ProfileMoveDTO(
            date=move.day,
            description=rules.title(state.measures[move.measure_id]),
            moves=[
                ValueMoveDTO(value=v, points=points)
                for v, points in move.changes.items()
            ],
        )
        for move in reversed(party.moves)
    ]


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


def _my_vice(state: GovernmentState, user_id: int) -> MyViceDTO | None:
    party = next((p for p in state.player_parties() if p.vice_id == user_id), None)
    if party is None:
        return None
    return MyViceDTO(party_id=party.id, phase=_vice_phase(party, user_id))


def _vice_options(
    state: GovernmentState, party: Party | None, users: list[UserDTO]
) -> list[ViceOptionDTO]:
    """Todo jogador da sala, com o partido dele e o motivo quando não pode ser convidado."""
    if party is None:
        return []
    options = []
    for user in users:
        if user.is_bot:
            continue
        home = state.party_of(user.id)
        options.append(
            ViceOptionDTO(
                nickname=user.nickname,
                color=_color(user.id),
                party_abbr=home.abbr if home else None,
                blocked=election.vice_blocker(state, party, user.id),
            )
        )
    return options


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
    latest: voters.Vote | None,
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
        flags=list(party.flags) if party.flags is not None else None,
        radar=_scores(party.radar),
        founding_radar=_scores(voters.initial_radar(party.flags)),
        affinity=_affinity(party.radar),
        founding_affinity=_affinity(voters.initial_radar(party.flags)),
        moves=_moves(state, party),
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
        intention_points=latest.total.get(party.id, Decimal(0))
        if latest
        else Decimal(0),
        valid_share=(
            election.valid_shares(latest.total).get(party.id, Decimal(0))
            if latest
            else Decimal(0)
        ),
        candidate=_candidate(people, candidate_id, party.candidate_name),
        # O convidado aparece na chapa mesmo antes de aceitar
        vice=_person(people, party.vice_id if party.vice_id is not None else vice_id),
        vice_phase=vice_phase,
        ticket_chosen=party.candidate_id is not None,
    )


def _simulation(
    state: GovernmentState, latest: voters.Vote | None
) -> RunoffSimulationDTO | None:
    """O 2º turno pela última pesquisa publicada, entre os finalistas ou os dois primeiros dela."""
    if latest is None:
        return None
    finalists = state.runoff or election.top_two(latest.total)
    if len(finalists) < 2:
        return None
    result = election.runoff(latest, finalists)
    entries = []
    for pid, own in sorted(latest.total.items()):
        is_finalist = pid in finalists
        entries.append(
            RunoffEntryDTO(
                party_id=pid,
                own_points=own,
                received_points=result.votes[pid] - own if is_finalist else Decimal(0),
                share=result.shares.get(pid, Decimal(0)),
                transfer_to=None if is_finalist else result.transfers[pid],
                donated=Decimal(0),
            )
        )
    return RunoffSimulationDTO(
        finalists=finalists, entries=entries, winner=result.winner_id
    )


def _round(
    result: RoundResult, state: GovernmentState, people: dict[int, UserDTO]
) -> RoundResultDTO:
    parties = [
        _round_party(pid, ticket, result, people)
        for pid, ticket in sorted(result.tickets.items())
    ]
    runoff = None
    if result.round == 2:
        first = next(
            (r for r in state.results if r.cycle == result.cycle and r.round == 1),
            None,
        )
        runoff = _stored_runoff(result, first)
    return RoundResultDTO(
        date=result.day,
        election_year=result.day.year,
        round=result.round,
        parties=parties,
        finalists=result.finalists,
        winner=result.winner_id,
        runoff=runoff,
    )


def _stored_runoff(
    result: RoundResult, first: RoundResult | None
) -> RunoffSimulationDTO:
    """
    O 2º turno como foi apurado: o finalista tem guardado o voto final, e o que ele
    trazia é o do 1º turno; a diferença veio de quem saiu (e das doações).
    """
    entries = []
    for pid in sorted(result.points):
        total = result.points[pid]
        own = total
        if pid in result.finalists and first is not None:
            own = min(total, first.points.get(pid, total))
        entries.append(
            RunoffEntryDTO(
                party_id=pid,
                own_points=own,
                received_points=total - own,
                share=result.shares.get(pid, Decimal(0)),
                transfer_to=result.transfers.get(pid),
                donated=result.donations.get(pid, Decimal(0)),
            )
        )
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
