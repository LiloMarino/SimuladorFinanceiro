"""A base do governo no Congresso para o painel: os aliados pagos com emenda, o hemiciclo e a prévia de uma proposta."""

from datetime import date

from backend.core.dto.government import (
    AmendmentSummaryDTO,
    BaseBlocDTO,
    BaseVoteDTO,
    CongressBaseDTO,
    DealDTO,
    DealPreviewDTO,
)
from backend.core.dto.user import UserDTO
from backend.core.enum import DealStatus
from backend.core.exceptions.http_exceptions import NotFoundError
from backend.features.government import deals as deal_rules
from backend.features.government import house
from backend.features.government.deals import Deal
from backend.features.government.government_book import GovernmentBook
from backend.features.government.state import Party


def build_base(
    book: GovernmentBook, users: list[UserDTO], viewer: UserDTO, today: date
) -> CongressBaseDTO:
    state = book.state
    people = {user.id: user for user in users}
    current = state.house_on(today)
    term = state.term
    president = book.president()
    governing = book.governing_bloc(today)
    governing_party = _party(book, term.party_id) if term else None
    mine = state.party_of(viewer.id)
    leading = mine is not None and mine.founder_id == viewer.id
    shown = [
        d
        for d in sorted(state.deals.values(), key=lambda d: d.id)
        if d.status is DealStatus.PENDING or d.in_force(today)
    ]
    proposal = book.incoming_deal(viewer)
    ratio = deal_rules.amendments(state.deals.values(), today)
    return CongressBaseDTO(
        governing_abbr=(governing_party.abbr if governing_party is not None else None),
        governing_seats=governing.seats if governing else 0,
        seats=book.base_seats(today),
        majority=house.MAJORITY,
        impeachment_votes=house.IMPEACHMENT_VOTES,
        president=president.nickname if president else None,
        is_president=president is not None and president.id == viewer.id,
        my_deal=next(
            (
                _deal(book, d, people, today)
                for d in shown
                if leading
                and mine is not None
                and d.party_id == mine.id
                and d.in_force(today)
            ),
            None,
        ),
        my_proposal=_deal(book, proposal, people, today) if proposal else None,
        deals=[_deal(book, d, people, today) for d in shown],
        blocs=[
            _bloc(book, bloc, people, today)
            for bloc in sorted(current.seated, key=lambda b: (-b.seats, b.key))
        ],
        amendments=AmendmentSummaryDTO(ratio=ratio, monthly=book.monthly(ratio, today)),
        last_vote=_last_vote(book, governing),
        blocker=(
            "O impeachment está em votação: nenhum acordo novo até o resultado."
            if state.request is not None
            else None
        ),
        answer_days=deal_rules.ANSWER_DAYS,
        term_months=deal_rules.TERM_MONTHS,
    )


def build_preview(
    book: GovernmentBook,
    users: list[UserDTO],
    today: date,
    bloc_key: int,
) -> DealPreviewDTO:
    """O que a proposta à bancada faz: preço, base, dívida no fim do mandato e se o computador deve aceitar."""
    people = {user.id: user for user in users}
    bloc = book.state.house_on(today).bloc(bloc_key)
    if bloc is None or bloc.seats == 0:
        raise NotFoundError("Esse partido não tem bancada na casa.")
    ratio = deal_rules.price(bloc.abbr, bloc.seats)
    active = book.state.deal_of(bloc.key, today)
    base = book.base_seats(today)
    debt = book.deal_debt(ratio, today, active)
    likely, shared = book.deal_odds(bloc.abbr, bloc.party_id)
    blocker = book.deal_blocker(bloc, today)
    return DealPreviewDTO(
        bloc_key=bloc.key,
        abbr=bloc.abbr,
        name=bloc.name,
        color=bloc.color,
        seats=bloc.seats,
        leader=_leader(book, bloc, people),
        is_computer=likely is not None,
        centrao=bloc.abbr == deal_rules.CENTRAO,
        ratio=ratio,
        monthly=book.monthly(ratio, today),
        start=today,
        end=deal_rules.last_day(today, book.term_end()),
        base_before=base,
        base_after=base if active is not None else base + bloc.seats,
        debt_before=debt[0] if debt else None,
        debt_after=debt[1] if debt else None,
        debt_end=debt[2] if debt else None,
        ally_groups=deal_rules.strongest_groups(bloc.mix),
        likely=likely,
        shared_flags=shared,
        blocker=blocker[0] if blocker else None,
    )


def _party(book: GovernmentBook, party_id: int | None) -> Party | None:
    return book.state.parties.get(party_id) if party_id is not None else None


def _leader(
    book: GovernmentBook, bloc: house.Bloc, people: dict[int, UserDTO]
) -> str | None:
    party = _party(book, bloc.party_id)
    if party is None or party.is_computer or party.founder_id is None:
        return None
    person = people.get(party.founder_id)
    return person.nickname if person else None


def _deal(
    book: GovernmentBook, deal: Deal, people: dict[int, UserDTO], today: date
) -> DealDTO:
    state = book.state
    current = state.house_on(today)
    bloc = current.bloc(deal.bloc_key)
    governing = book.governing_bloc(today)
    party = _party(book, deal.party_id)
    leader = people.get(party.founder_id) if party and party.founder_id else None
    votes = yes = 0
    for measure in state.measures.values():
        tally, decided = measure.tally, measure.decided
        if tally is None or decided is None or not deal.covers(decided):
            continue
        vote = tally.blocs.get(deal.bloc_key)
        if vote is not None:
            votes += 1
            yes += 1 if vote.orientation else 0
    seats = bloc.seats if bloc is not None else deal.seats
    base = book.base_seats(today)
    in_force = deal.in_force(today)
    days_left = (deal.end - today).days if in_force and deal.end else None
    return DealDTO(
        id=deal.id,
        bloc_key=deal.bloc_key,
        party_id=deal.party_id,
        abbr=deal.abbr,
        name=bloc.name if bloc else deal.abbr,
        color=bloc.color if bloc else None,
        seats=seats,
        status=deal.status,
        leader=(
            leader.nickname
            if leader is not None and party is not None and not party.is_computer
            else None
        ),
        is_computer=deal.is_computer,
        centrao=deal.abbr == deal_rules.CENTRAO,
        ratio=deal.ratio,
        monthly=book.monthly(deal.ratio, today),
        answer_by=deal.answer_by,
        start=deal.start,
        end=deal.end,
        days_left=days_left,
        renewable=days_left is not None and days_left <= deal_rules.RENEW_DAYS,
        votes=votes,
        yes=yes,
        base_after=base - seats if in_force else base + seats,
        ally_groups=deal_rules.strongest_groups(bloc.mix if bloc else {}),
        government_groups=deal_rules.strongest_groups(
            governing.mix if governing else {}
        ),
    )


def _bloc(
    book: GovernmentBook, bloc: house.Bloc, people: dict[int, UserDTO], today: date
) -> BaseBlocDTO:
    state = book.state
    term = state.term
    governing = term is not None and bloc.party_id == term.party_id
    ratio = deal_rules.price(bloc.abbr, bloc.seats)
    blocker = None if governing else book.deal_blocker(bloc, today)
    return BaseBlocDTO(
        key=bloc.key,
        party_id=bloc.party_id,
        abbr=bloc.abbr,
        name=bloc.name,
        color=bloc.color,
        seats=bloc.seats,
        is_computer=bloc.is_computer,
        centrao=bloc.abbr == deal_rules.CENTRAO,
        leader=_leader(book, bloc, people),
        governing=governing,
        in_base=state.deal_of(bloc.key, today) is not None,
        pending=state.pending_deal_of(bloc.key) is not None,
        ratio=ratio,
        monthly=book.monthly(ratio, today),
        blocker=blocker[0] if blocker else None,
        retry_from=blocker[1] if blocker else None,
        declined_on=state.last_refusal(bloc.key),
    )


def _last_vote(
    book: GovernmentBook, governing: house.Bloc | None
) -> BaseVoteDTO | None:
    """A votação de medida mais recente e quantos deputados da base votaram contra a orientação."""
    state = book.state
    decided = [m for m in state.measures.values() if m.tally is not None and m.decided]
    if not decided:
        return None
    last = max(decided, key=lambda m: (m.decided, m.id))
    tally, day = last.tally, last.decided
    if tally is None or day is None:
        return None
    base_keys = {d.bloc_key for d in state.deals.values() if d.covers(day)}
    if governing is not None:
        base_keys.add(governing.key)
    return BaseVoteDTO(
        day=day,
        defected=sum(v.defected for k, v in tally.blocs.items() if k in base_keys),
    )
