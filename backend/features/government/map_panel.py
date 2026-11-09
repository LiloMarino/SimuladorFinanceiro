"""O mapa do Brasil: a pesquisa, o resultado, a rejeição e a aprovação em cada estado e região."""

from collections.abc import Callable
from datetime import date
from decimal import Decimal

from backend.core.dto.government import (
    GroupScoreDTO,
    MapApprovalDTO,
    MapPanelDTO,
    MapPartyDTO,
    MapPlaceDTO,
    MapPollDTO,
    MapPollPlaceDTO,
    MapRejectionDTO,
    MapResultDTO,
    MapResultEntryDTO,
    MapResultPlaceDTO,
    MapValueDTO,
)
from backend.core.dto.simulation import SimulationDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import ElectionPhase, PlaceKind, Region, VoterGroup
from backend.core.utils import is_business_day, next_month_turn
from backend.features.government import approval, election, places, second_round, voters
from backend.features.government.calendar import ElectionCycle
from backend.features.government.government_book import GovernmentBook
from backend.features.government.panel import phase_of
from backend.features.government.poll_panel import entries, place_vote
from backend.features.government.state import GovernmentState, Party, RoundResult


def build_map(
    book: GovernmentBook, settings: SimulationDTO, viewer: UserDTO, today: date
) -> MapPanelDTO:
    state = book.state
    cycle = book.cycle()
    phase = phase_of(state, cycle, today)
    running = sorted(
        (p for p in state.parties.values() if election.runs(state, p)),
        key=lambda p: p.id,
    )
    mine = state.party_of(viewer.id)
    all_places = places.all_places()
    current = book.approval(today)
    return MapPanelDTO(
        places=[_place(p, settings.poll_margin) for p in all_places],
        national_groups=_groups(voters.WEIGHTS),
        parties=[
            MapPartyDTO(id=p.id, abbr=p.abbr, name=p.name, color=p.color)
            for p in running
        ],
        viewer_party_id=(mine.id if mine is not None and mine in running else None),
        poll=_poll(book, settings, state, cycle, phase, today),
        result=_result(book, settings, phase),
        rejection=[_rejection(p, all_places) for p in running],
        approval=(
            MapApprovalDTO(
                national=approval.overall(current.satisfaction),
                places=[
                    MapValueDTO(
                        code=places.code(p),
                        value=approval.overall(current.satisfaction, places.mixture(p)),
                    )
                    for p in all_places
                ],
            )
            if current is not None
            else None
        ),
        opens_on=_opens_on(cycle),
        first_round=cycle.first_round,
        runoff=cycle.runoff,
        phase=phase,
    )


def _groups(mix: dict[VoterGroup, Decimal]) -> list[GroupScoreDTO]:
    return [GroupScoreDTO(group=g, score=mix[g]) for g in VoterGroup]


def _place(place: places.Place, with_margin: bool) -> MapPlaceDTO:
    is_region = isinstance(place, Region)
    return MapPlaceDTO(
        code=places.code(place),
        name=places.NAMES[place],
        kind=PlaceKind.REGION if is_region else PlaceKind.STATE,
        region=None if isinstance(place, Region) else places.REGION_OF[place],
        electorate=places.electorate(place),
        electorate_share=places.share(place),
        margin=places.margin(place) if with_margin else 0,
        groups=_groups(places.mixture(place)),
    )


def _opens_on(cycle: ElectionCycle) -> date:
    """O dia da primeira pesquisa da campanha: o fechamento do mês em que ela abre."""
    start = cycle.campaign_start
    month_first = start.replace(day=1)
    while not is_business_day(month_first):
        month_first = month_first.replace(day=month_first.day + 1)
    return month_first if start <= month_first else next_month_turn(start)


def _poll(
    book: GovernmentBook,
    settings: SimulationDTO,
    state: GovernmentState,
    cycle: ElectionCycle,
    phase: ElectionPhase,
    today: date,
) -> MapPollDTO | None:
    if phase is ElectionPhase.BETWEEN_ROUNDS:
        runoff = True
        series = [(p.day, p.vote) for p in state.race_polls]
        started = state.race_started
        days = (
            second_round.poll_days(started, cycle.donation_deadline)
            if started is not None
            else []
        )
        next_date = next((d for d in days if d > today), None)
    elif phase is ElectionPhase.CAMPAIGN:
        runoff = False
        series = [(p.day, p.vote) for p in state.polls]
        following = next_month_turn(today)
        next_date = following if following < cycle.first_round else None
    else:
        return None
    if not series:
        return None
    return _poll_at(book, settings, series, len(series) - 1, runoff, next_date)


def _poll_at(
    book: GovernmentBook,
    settings: SimulationDTO,
    series: list[tuple[date, voters.Vote]],
    index: int,
    runoff: bool,
    next_date: date | None,
) -> MapPollDTO:
    """A pesquisa do item `index` da série, com a anterior dela para a variação."""
    day, exact = series[index]
    before = series[index - 1] if index > 0 else None

    def local(vote: voters.Vote, on: date, place: places.Place) -> voters.Vote:
        return place_vote(vote, place, on, book.seed, settings.poll_margin)

    return MapPollDTO(
        date=day,
        previous_date=before[0] if before else None,
        next_date=next_date,
        runoff=runoff,
        places=[_poll_place(p, local, exact, day, before) for p in places.all_places()],
    )


def _poll_place(
    place: places.Place,
    local: Callable[[voters.Vote, date, places.Place], voters.Vote],
    exact: voters.Vote,
    day: date,
    before: tuple[date, voters.Vote] | None,
) -> MapPollPlaceDTO:
    now = local(exact, day, place)
    return MapPollPlaceDTO(
        code=places.code(place),
        entries=entries(now.total),
        undecided=now.undecided,
        previous_entries=(
            entries(local(before[1], before[0], place).total) if before else []
        ),
    )


def _result(
    book: GovernmentBook, settings: SimulationDTO, phase: ElectionPhase
) -> MapResultDTO | None:
    state = book.state
    if phase in (ElectionPhase.BEFORE_CAMPAIGN, ElectionPhase.CAMPAIGN):
        return None
    last = state.results[-1] if state.results else None
    if last is None or not last.groups:
        return None
    return _result_of(last, poll_before(book, settings, last))


def poll_before(
    book: GovernmentBook, settings: SimulationDTO, result: RoundResult
) -> MapPollDTO | None:
    """A última pesquisa antes do turno: a mensal antes do 1º e a semanal antes do 2º."""
    history = book.state.history_of(result.cycle)
    if history is None:
        return None
    series = (
        [(p.day, p.vote) for p in history.race_polls]
        if result.round == 2
        else [(p.day, p.vote) for p in history.polls]
    )
    if not series:
        return None
    return _poll_at(book, settings, series, len(series) - 1, result.round == 2, None)


def _result_of(result: RoundResult, previous: MapPollDTO | None) -> MapResultDTO:
    """A apuração do turno em cada lugar, com a pesquisa anterior para a variação."""
    before = {p.code: p.entries for p in previous.places} if previous else {}
    return MapResultDTO(
        round=result.round,
        date=result.day,
        previous_date=previous.date if previous else None,
        national=_result_entries(result.points),
        places=[
            MapResultPlaceDTO(
                code=places.code(p),
                entries=_result_entries(
                    voters.combine(result.groups, weights=places.mixture(p)).total
                ),
                previous_entries=before.get(places.code(p), []),
            )
            for p in places.all_places()
        ],
    )


def _result_entries(points: dict[int, Decimal]) -> list[MapResultEntryDTO]:
    shares = election.valid_shares(points)
    return [
        MapResultEntryDTO(
            party_id=pid, share=shares[pid] * voters.HUNDRED, points=points[pid]
        )
        for pid in sorted(points)
    ]


def _rejection(party: Party, all_places: list[places.Place]) -> MapRejectionDTO:
    felt = {g: party.felt_rejection(g) for g in VoterGroup}
    return MapRejectionDTO(
        party_id=party.id,
        national=approval.overall(felt),
        places=[
            MapValueDTO(
                code=places.code(p),
                value=approval.overall(felt, places.mixture(p)),
            )
            for p in all_places
        ],
    )
