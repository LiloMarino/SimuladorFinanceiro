"""O Congresso para o painel: a casa eleita, as bancadas, o placar de cada votação e o pedido de impeachment."""

from collections.abc import Callable
from datetime import date, timedelta
from decimal import Decimal

from backend.core.dto.government import (
    BlocDTO,
    BlocVoteDTO,
    CongressDTO,
    GuidanceRuleDTO,
    GuideDTO,
    GuideScenarioDTO,
    HouseDTO,
    ImpeachmentRequestDTO,
    PastVoteDTO,
    ValueMoveDTO,
    VoteDTO,
)
from backend.core.dto.user import UserDTO
from backend.core.enum import MeasureStatus, VoterGroup, VoterValue
from backend.features.government import congress, house, voters
from backend.features.government import measures as rules
from backend.features.government.government_book import GovernmentBook
from backend.features.government.state import ElectedHouse, Measure, Party

PERCENT = Decimal(100)


def build_congress(
    book: GovernmentBook,
    viewer: UserDTO,
    today: date,
    people: dict[int, UserDTO],
) -> CongressDTO:
    state = book.state
    mine = state.party_of(viewer.id)
    leader_bloc = _leading_bloc(book, mine, viewer, today) if mine is not None else None
    elected = state.elected_house()
    in_office = state.house_on(today)
    waiting = elected if elected is not None and elected.takes_office > today else None
    stats = _stats(book)
    return CongressDTO(
        house=_house(
            book, in_office, elected_in_office(book, today), leader_bloc, stats
        ),
        elected=(
            _house(book, waiting.house, waiting, leader_bloc, stats)
            if waiting is not None
            else None
        ),
        impeachment_request=_request(book, viewer, today, people),
        history=_history(book, today),
        low_streak=state.low_streak,
    )


def elected_in_office(book: GovernmentBook, today: date) -> ElectedHouse | None:
    """A eleição que formou a casa em exercício; nula na casa inicial do computador."""
    seated = [e for e in book.state.houses if e.takes_office <= today]
    return seated[-1] if seated else None


def guidance_rules(party: Party) -> list[GuidanceRuleDTO]:
    return [
        GuidanceRuleDTO(value=value, yes=party.rules[value]) for value in VoterValue
    ]


def vote_dto(
    book: GovernmentBook,
    viewer: UserDTO,
    today: date,
    measure: Measure | None,
) -> VoteDTO | None:
    """O placar de uma medida: o exato se já foi votada, o previsto em faixa se está na fila."""
    if measure is None:
        return None
    if measure.status is MeasureStatus.QUEUED:
        orientations, guided, wanted = book.measure_orientations(measure, today)
        effects = book.effects_of(measure)
        proposer = book.proposer_party(measure)
        proposer_party = proposer.id if proposer is not None else None
        moves = (
            [
                ValueMoveDTO(value=v, points=points)
                for v, points in voters.radar_moves(
                    measure.kind, measure.value, measure.before
                ).items()
            ]
            if not measure.kind.is_spending
            else []
        )
        return _open_vote(
            book,
            viewer,
            today,
            house.MAJORITY,
            congress.next_vote_date(today),
            orientations,
            guided,
            wanted,
            house.reactions(effects),
            house.pulled_value(effects),
            moves,
            lambda bloc: _default(
                book,
                bloc,
                house.pulled_value(effects),
                orientations,
                proposer_party,
                today,
            ),
            with_deals=True,
        )
    if measure.tally is None or measure.decided is None:
        return None
    return _closed_vote(
        book,
        measure.tally,
        measure.decided,
        house.MAJORITY,
    )


def _open_vote(
    book: GovernmentBook,
    viewer: UserDTO,
    today: date,
    needed: int,
    vote_day: date,
    orientations: dict[int, bool],
    guided: dict[int, bool],
    wanted: dict[int, Decimal],
    reactions: dict[VoterGroup, Decimal],
    pulled: VoterValue | None,
    yes_moves: list[ValueMoveDTO],
    standard: Callable[[house.Bloc], bool],
    with_deals: bool = False,
) -> VoteDTO:
    current = book.state.house_on(today)
    low, high = house.forecast(current, orientations, wanted)
    mine = book.state.party_of(viewer.id)
    leading = _leading_bloc(book, mine, viewer, today) if mine is not None else None
    blocs = []
    for bloc in current.seated:
        cause, share = _cause(bloc, reactions, orientations[bloc.key])
        by_deal = with_deals and book.state.deal_of(bloc.key, today) is not None
        blocs.append(
            BlocVoteDTO(
                key=bloc.key,
                abbr=bloc.abbr,
                color=bloc.color,
                seats=bloc.seats,
                orientation=orientations[bloc.key],
                guided=guided[bloc.key],
                may_defect=house.may_defect(
                    bloc.seats, orientations[bloc.key], wanted[bloc.key]
                ),
                yes=None,
                no=None,
                defected=None,
                cause=cause,
                cause_share=share,
                by_deal=by_deal,
            )
        )
    guide = None
    if leading is not None and today < vote_day:
        guide = GuideDTO(
            bloc_key=leading.key,
            abbr=leading.abbr,
            seats=leading.seats,
            deadline=vote_day - timedelta(days=1),
            default_orientation=standard(leading),
            pulled_value=pulled,
            scenarios=[
                _scenario(
                    current, leading, orientations, wanted, reactions, orientation
                )
                for orientation in (True, False)
            ],
            yes_moves=[] if _governing(book, leading) else yes_moves,
            by_deal=with_deals and book.state.deal_of(leading.key, today) is not None,
        )
    return VoteDTO(
        blocs=blocs,
        needed=needed,
        yes=None,
        no=None,
        defected=None,
        low=low,
        high=high,
        guide=guide,
    )


def _governing(book: GovernmentBook, bloc: house.Bloc) -> bool:
    term = book.state.term
    return term is not None and bloc.party_id == term.party_id


def _default(
    book: GovernmentBook,
    bloc: house.Bloc,
    pulled: VoterValue | None,
    orientations: dict[int, bool],
    proposer_party: int | None,
    today: date,
) -> bool:
    """A orientação que vale quando o líder não orienta: Sim na medida do próprio governo ou com acordo em vigor, senão a regra do partido para o valor da medida."""
    if bloc.party_id is not None and bloc.party_id == proposer_party:
        return True
    if book.state.deal_of(bloc.key, today) is not None:
        return True
    party = book.state.parties.get(bloc.party_id) if bloc.party_id else None
    if party is None:
        return orientations[bloc.key]
    return False if pulled is None else party.rules[pulled]


def _scenario(
    current: house.House,
    bloc: house.Bloc,
    orientations: dict[int, bool],
    wanted: dict[int, Decimal],
    reactions: dict[VoterGroup, Decimal],
    orientation: bool,
) -> GuideScenarioDTO:
    changed = {**orientations, bloc.key: orientation}
    low, high = house.forecast(current, changed, wanted)
    cause, share = _cause(bloc, reactions, orientation)
    return GuideScenarioDTO(
        orientation=orientation,
        low=low,
        high=high,
        may_defect=house.may_defect(bloc.seats, orientation, wanted[bloc.key]),
        cause=cause,
        cause_share=share,
    )


def _cause(
    bloc: house.Bloc, reactions: dict[VoterGroup, Decimal], orientation: bool
) -> tuple[VoterGroup | None, Decimal | None]:
    """O grupo que mais quer o voto contrário ao orientado e o peso dele nos eleitores da bancada."""
    group = house.contrary_group(bloc.mix, reactions, orientation)
    return (group, bloc.mix[group]) if group is not None else (None, None)


def _closed_vote(
    book: GovernmentBook, tally: house.Tally, day: date, needed: int
) -> VoteDTO:
    current = book.state.house_on(day)
    blocs = []
    for key, vote in sorted(tally.blocs.items()):
        bloc = current.bloc(key)
        blocs.append(
            BlocVoteDTO(
                key=key,
                abbr=bloc.abbr if bloc else "?",
                color=bloc.color if bloc else None,
                seats=vote.seats,
                orientation=vote.orientation,
                guided=True,
                may_defect=vote.defected,
                yes=vote.yes,
                no=vote.no,
                defected=vote.defected,
                cause=vote.cause,
                cause_share=bloc.mix[vote.cause] if bloc and vote.cause else None,
                by_deal=any(
                    d.bloc_key == key and d.covers(day)
                    for d in book.state.deals.values()
                ),
            )
        )
    return VoteDTO(
        blocs=blocs,
        needed=needed,
        yes=tally.yes,
        no=tally.no,
        defected=tally.defected,
        low=None,
        high=None,
        guide=None,
    )


def _request(
    book: GovernmentBook, viewer: UserDTO, today: date, people: dict[int, UserDTO]
) -> ImpeachmentRequestDTO | None:
    request = book.state.request
    if request is None:
        return None
    president = book.president()
    orientations, guided, wanted = book.impeachment_orientations(today)
    reactions = house.impeachment_reactions(book.state.satisfaction)
    return ImpeachmentRequestDTO(
        opened=request.opened,
        vote_day=request.vote_day,
        president=president.nickname if president else None,
        vote=_open_vote(
            book,
            viewer,
            today,
            house.IMPEACHMENT_VOTES,
            request.vote_day,
            orientations,
            guided,
            wanted,
            reactions,
            None,
            [],
            lambda bloc: (
                not _governing(book, bloc)
                and house.impeachment_orientation(
                    house.mood(bloc.mix, book.state.satisfaction)
                )
            ),
        ),
    )


def _history(book: GovernmentBook, today: date) -> list[PastVoteDTO]:
    past = [
        PastVoteDTO(
            day=measure.decided,
            title=rules.title(measure),
            approved=measure.status is MeasureStatus.APPROVED,
            yes=measure.tally.yes,
            no=measure.tally.no,
            defected=measure.tally.defected,
            is_impeachment=False,
        )
        for measure in book.state.measures.values()
        if measure.tally is not None and measure.decided is not None
    ]
    past.extend(
        PastVoteDTO(
            day=vote.day,
            title="Pedido de impeachment",
            approved=vote.approved,
            yes=vote.tally.yes,
            no=vote.tally.no,
            defected=vote.tally.defected,
            is_impeachment=True,
        )
        for vote in book.state.impeachment_votes
    )
    return sorted(past, key=lambda v: v.day, reverse=True)


def _leading_bloc(
    book: GovernmentBook, party: Party, viewer: UserDTO, today: date
) -> house.Bloc | None:
    """A bancada do partido do jogador, se ele é o líder e ela tem cadeira."""
    if party.founder_id != viewer.id:
        return None
    bloc = book.state.house_on(today).of_party(party.id)
    return bloc if bloc is not None and bloc.seats > 0 else None


def _stats(book: GovernmentBook) -> dict[int, tuple[int, int, int, int]]:
    """Por bancada: votações, Sim, cadeiras que votaram e deputados que desobedeceram."""
    totals: dict[int, list[int]] = {}
    tallies = [m.tally for m in book.state.measures.values() if m.tally is not None]
    for tally in tallies:
        for key, vote in tally.blocs.items():
            row = totals.setdefault(key, [0, 0, 0, 0])
            row[0] += 1
            row[1] += vote.yes
            row[2] += vote.seats
            row[3] += vote.defected
    return {key: (r[0], r[1], r[2], r[3]) for key, r in totals.items()}


def _house(
    book: GovernmentBook,
    current: house.House,
    elected: ElectedHouse | None,
    leader_bloc: house.Bloc | None,
    stats: dict[int, tuple[int, int, int, int]],
) -> HouseDTO:
    state = book.state
    term = state.term
    previous = _previous(book, elected)
    return HouseDTO(
        elected=elected.day if elected else None,
        takes_office=elected.takes_office if elected else None,
        seats=house.SEATS,
        majority=house.MAJORITY,
        impeachment_votes=house.IMPEACHMENT_VOTES,
        barrier=house.BARRIER,
        blocs=[
            _bloc(
                bloc,
                previous,
                term is not None and bloc.party_id == term.party_id,
                leader_bloc is not None and leader_bloc.key == bloc.key,
                stats.get(bloc.key),
            )
            for bloc in sorted(current.blocs, key=lambda b: (-b.seats, b.key))
        ],
        below=[b.abbr for b in current.blocs if b.key in current.below],
        last_quotient=current.last,
        next_quotient=current.upcoming,
    )


def _previous(book: GovernmentBook, elected: ElectedHouse | None) -> house.House | None:
    """A casa que veio antes da eleita, para contar as cadeiras ganhas e perdidas."""
    if elected is None:
        return None
    houses = book.state.houses
    index = houses.index(elected)
    return houses[index - 1].house if index > 0 else house.initial_house()


def _bloc(
    bloc: house.Bloc,
    previous: house.House | None,
    governing: bool,
    mine: bool,
    stat: tuple[int, int, int, int] | None,
) -> BlocDTO:
    votes, yes, seats, defected = stat or (0, 0, 0, 0)
    before = previous.bloc(bloc.key) if previous is not None else None
    return BlocDTO(
        key=bloc.key,
        party_id=bloc.party_id,
        abbr=bloc.abbr,
        name=bloc.name,
        color=bloc.color,
        is_computer=bloc.is_computer,
        votes=bloc.votes,
        seats=bloc.seats,
        previous_seats=(
            (before.seats if before is not None else 0)
            if previous is not None
            else None
        ),
        governing=governing,
        votes_cast=votes,
        yes_share=PERCENT * yes / seats if seats else None,
        defection_share=PERCENT * defected / seats if seats else None,
        is_mine=mine,
    )
