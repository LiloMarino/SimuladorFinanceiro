"""A linha do tempo do mapa: os anos de eleição, os pontos da régua e os marcos de um ciclo."""

from collections import Counter
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from backend.core.dto.government import (
    MapMilestoneDTO,
    MapMilestoneItemDTO,
    MapPartyDTO,
    MapPollDTO,
    MapResultDTO,
    MapTimelineDTO,
    MapTimelinePointDTO,
    MapTimelineYearDTO,
)
from backend.core.dto.simulation import SimulationDTO
from backend.core.enum import (
    ElectionPhase,
    MilestoneKind,
    Region,
    TimelinePointKind,
    TimelineYearStatus,
    VoterGroup,
)
from backend.core.utils import next_month_turn
from backend.features.government import election, places, second_round, voters
from backend.features.government import measures as rules
from backend.features.government.government_book import GovernmentBook
from backend.features.government.map_panel import (
    _opens_on,
    _poll_at,
    _result_of,
    poll_before,
)
from backend.features.government.panel import phase_of
from backend.features.government.state import GovernmentState, RoundResult, Ticket

Series = list[tuple[date, voters.Vote]]


@dataclass(frozen=True)
class _Item:
    """Um fato do ciclo que vira item de marco: quem fez, quando e de que tipo."""

    day: date
    party_id: int
    kind: MilestoneKind
    item: MapMilestoneItemDTO


def build_timeline(
    book: GovernmentBook, settings: SimulationDTO, today: date, year: int | None
) -> MapTimelineDTO:
    state = book.state
    phase = phase_of(state, book.cycle(), today)
    years = _years(book, phase)
    chosen = _chosen(years, year)
    points = _points(book, settings, chosen, today)
    return MapTimelineDTO(
        years=years,
        year=chosen.year,
        parties=_parties(book, chosen),
        points=points,
        milestones=_milestones(book, chosen.cycle, [p.date for p in points]),
    )


def _years(book: GovernmentBook, phase: ElectionPhase) -> list[MapTimelineYearDTO]:
    """Um ano por eleição até a em curso; sem campanha aberta, a próxima fica como `UPCOMING`."""
    state = book.state
    opened = phase in (ElectionPhase.CAMPAIGN, ElectionPhase.BETWEEN_ROUNDS)
    years = []
    for index in range(state.cycle + 1):
        cycle = book.cycle(index)
        if index < state.cycle:
            status = TimelineYearStatus.DONE
        elif opened:
            status = TimelineYearStatus.CURRENT
        else:
            status = TimelineYearStatus.UPCOMING
        years.append(
            MapTimelineYearDTO(
                year=cycle.first_round.year,
                cycle=index,
                status=status,
                opens_on=cycle.campaign_start,
                winner=_winner(state, index),
            )
        )
    return years


def _winner(state: GovernmentState, cycle: int) -> MapPartyDTO | None:
    final = next(
        (r for r in state.results if r.cycle == cycle and r.winner_id is not None),
        None,
    )
    if final is None or final.winner_id is None:
        return None
    return _ticket_party(final.winner_id, final.tickets[final.winner_id])


def _ticket_party(party_id: int, ticket: Ticket) -> MapPartyDTO:
    return MapPartyDTO(
        id=party_id, abbr=ticket.abbr, name=ticket.name, color=ticket.color
    )


def _chosen(years: list[MapTimelineYearDTO], year: int | None) -> MapTimelineYearDTO:
    """O ano pedido; sem ele (ou desconhecido), o ciclo em curso, senão o último encerrado, senão o próximo."""
    asked = next((y for y in years if y.year == year), None)
    if asked is not None:
        return asked
    for status in (TimelineYearStatus.CURRENT, TimelineYearStatus.DONE):
        found = [y for y in years if y.status is status]
        if found:
            return found[-1]
    return years[-1]


def _parties(book: GovernmentBook, chosen: MapTimelineYearDTO) -> list[MapPartyDTO]:
    """Quem concorreu: as chapas do 1º turno no ciclo encerrado, os partidos em disputa no em curso."""
    state = book.state
    if chosen.status is TimelineYearStatus.DONE:
        first = next(
            (r for r in state.results if r.cycle == chosen.cycle and r.round == 1), None
        )
        tickets = first.tickets if first is not None else {}
        return [_ticket_party(pid, t) for pid, t in sorted(tickets.items())]
    return [
        MapPartyDTO(id=p.id, abbr=p.abbr, name=p.name, color=p.color)
        for p in sorted(
            (p for p in state.parties.values() if election.runs(state, p)),
            key=lambda p: p.id,
        )
    ]


def _points(
    book: GovernmentBook,
    settings: SimulationDTO,
    chosen: MapTimelineYearDTO,
    today: date,
) -> list[MapTimelinePointDTO]:
    state = book.state
    if chosen.status is TimelineYearStatus.UPCOMING:
        return []
    history = state.history_of(chosen.cycle)
    if history is None:
        return []
    cycle = book.cycle(chosen.cycle)
    current = chosen.status is TimelineYearStatus.CURRENT
    rounds = {r.round: r for r in state.results if r.cycle == chosen.cycle}
    first = rounds.get(1)

    monthly: Series = [(p.day, p.vote) for p in history.polls]
    weekly: Series = [(p.day, p.vote) for p in history.race_polls]
    monthly_days = [day for day, _ in monthly]
    weekly_days = [day for day, _ in weekly]
    if current:
        # Depois do 1º turno apurado não há mais pesquisa mensal
        if first is None:
            monthly_days += _coming_months(cycle.first_round, monthly_days, cycle)
        runoff_possible = first is None or (
            first.winner_id is None and len(first.finalists) == 2
        )
        if runoff_possible:
            weekly_days += [
                d
                for d in second_round.poll_days(
                    first.day if first else cycle.first_round, cycle.donation_deadline
                )
                if d not in weekly_days
            ]
    first_result = _round(book, settings, first)
    margin = voters.TOTAL_MARGIN if settings.poll_margin else 0

    points: list[MapTimelinePointDTO] = []
    for i, day in enumerate(monthly_days):
        if i < len(monthly):
            poll = _poll_at(
                book, settings, monthly, i, False, _following(monthly_days, i)
            )
            points.append(_poll_point(day, TimelinePointKind.POLL, poll, None, margin))
        else:
            points.append(_future(day, TimelinePointKind.POLL))
    if first is not None:
        points.append(
            MapTimelinePointDTO(
                date=first.day,
                kind=TimelinePointKind.FIRST_ROUND,
                happened=True,
                leaders=_round_leaders(first),
                poll=None,
                result=first_result,
            )
        )
    elif current:
        points.append(_future(cycle.first_round, TimelinePointKind.FIRST_ROUND))
    for i, day in enumerate(weekly_days):
        if i < len(weekly):
            poll = _poll_at(book, settings, weekly, i, True, _following(weekly_days, i))
            points.append(
                _poll_point(
                    day, TimelinePointKind.RUNOFF_POLL, poll, first_result, margin
                )
            )
        else:
            points.append(_future(day, TimelinePointKind.RUNOFF_POLL))
    second = rounds.get(2)
    if second is not None:
        points.append(
            MapTimelinePointDTO(
                date=second.day,
                kind=TimelinePointKind.RUNOFF,
                happened=True,
                leaders=_round_leaders(second),
                poll=None,
                result=_round(book, settings, second),
            )
        )
    elif current and (weekly_days or first is not None):
        points.append(_future(cycle.runoff, TimelinePointKind.RUNOFF))
    return points


def _coming_months(first_round: date, given: list[date], cycle) -> list[date]:
    """As pesquisas mensais que faltam até o 1º turno: a primeira da campanha, depois o mês seguinte a cada uma."""
    days = []
    day = _opens_on(cycle) if not given else next_month_turn(given[-1])
    while day < first_round:
        days.append(day)
        day = next_month_turn(day)
    return days


def _following(days: list[date], index: int) -> date | None:
    return days[index + 1] if index + 1 < len(days) else None


def _round(
    book: GovernmentBook, settings: SimulationDTO, result: RoundResult | None
) -> MapResultDTO | None:
    if result is None or not result.groups:
        return None
    return _result_of(result, poll_before(book, settings, result))


def _future(day: date, kind: TimelinePointKind) -> MapTimelinePointDTO:
    return MapTimelinePointDTO(
        date=day, kind=kind, happened=False, leaders=[], poll=None, result=None
    )


def _poll_point(
    day: date,
    kind: TimelinePointKind,
    poll: MapPollDTO,
    result: MapResultDTO | None,
    margin: int,
) -> MapTimelinePointDTO:
    return MapTimelinePointDTO(
        date=day,
        kind=kind,
        happened=True,
        leaders=_poll_leaders(poll, margin),
        poll=poll,
        result=result,
    )


def _poll_leaders(poll: MapPollDTO, margin: int) -> list[int]:
    """O líder nacional, ou os dois do empate técnico; o país é a soma das regiões pesada pelo eleitorado."""
    shares = {region.value: places.share(region) for region in Region}
    totals: dict[int, Decimal] = {}
    for place in poll.places:
        weight = shares.get(place.code)
        if weight is None:
            continue
        for entry in place.entries:
            totals[entry.party_id] = (
                totals.get(entry.party_id, Decimal(0)) + entry.points * weight
            )
    ranked = sorted(totals, key=lambda pid: (-totals[pid], pid))
    if len(ranked) < 2:
        return ranked
    gap = totals[ranked[0]] - totals[ranked[1]]
    tied = gap <= margin if margin > 0 else gap == 0
    return ranked[:2] if tied else ranked[:1]


def _round_leaders(result: RoundResult) -> list[int]:
    """O vencedor; sem ele, os dois finalistas na ordem dos votos."""
    if result.winner_id is not None:
        return [result.winner_id]
    return sorted(result.finalists, key=lambda pid: (-result.points.get(pid, 0), pid))


def _milestones(
    book: GovernmentBook, cycle: int, dates: list[date]
) -> list[MapMilestoneDTO]:
    """Os fatos do ciclo agrupados no intervalo entre duas pesquisas, por partido e tipo."""
    grouped: dict[tuple[int, MilestoneKind, int], list[_Item]] = {}
    for fact in _facts(book, cycle):
        slot = max((i for i, d in enumerate(dates) if d <= fact.day), default=None)
        # Antes do primeiro ponto e depois do último não há intervalo na régua
        if slot is None or slot + 1 >= len(dates):
            continue
        grouped.setdefault((slot, fact.kind, fact.party_id), []).append(fact)
    return [
        MapMilestoneDTO(
            after=dates[slot],
            before=dates[slot + 1],
            party_id=party_id,
            kind=kind,
            items=[f.item for f in sorted(facts, key=lambda f: f.day)],
            region=_aimed_region(facts) if kind is MilestoneKind.CAMPAIGN else None,
        )
        for (slot, kind, party_id), facts in sorted(
            grouped.items(),
            key=lambda entry: (entry[0][0], entry[0][1].value, entry[0][2]),
        )
    ]


def _facts(book: GovernmentBook, cycle: int) -> list[_Item]:
    state = book.state
    history = state.history_of(cycle)
    facts: list[_Item] = []
    if history is not None:
        facts.extend(
            _Item(
                action.day,
                action.party_id,
                MilestoneKind.CAMPAIGN,
                MapMilestoneItemDTO(
                    day=action.day,
                    action=action.kind,
                    group=action.group,
                    rival_id=action.rival_id,
                    partner_id=None,
                    title=None,
                ),
            )
            for action in history.actions
        )
        for declaration in history.declarations:
            if declaration.endorsed_id is None:
                continue
            facts.append(
                _Item(
                    declaration.day,
                    declaration.party_id,
                    MilestoneKind.ALLIANCE,
                    MapMilestoneItemDTO(
                        day=declaration.day,
                        action=None,
                        group=None,
                        rival_id=None,
                        partner_id=declaration.endorsed_id,
                        title=None,
                    ),
                )
            )
    for party in state.parties.values():
        made = list(party.promises) if cycle == state.cycle else []
        for record in party.past_promises:
            if record.cycle == cycle:
                made += record.promises
        facts.extend(
            _Item(
                promise.announced,
                party.id,
                MilestoneKind.PROMISE,
                MapMilestoneItemDTO(
                    day=promise.announced,
                    action=None,
                    group=None,
                    rival_id=None,
                    partner_id=None,
                    title=rules.promise_title(promise),
                ),
            )
            for promise in made
        )
    for federation in state.federations.values():
        if federation.cycle != cycle:
            continue
        facts.append(
            _Item(
                federation.formed_on,
                federation.parties[0],
                MilestoneKind.ALLIANCE,
                MapMilestoneItemDTO(
                    day=federation.formed_on,
                    action=None,
                    group=None,
                    rival_id=None,
                    partner_id=federation.parties[1],
                    title=federation.name,
                ),
            )
        )
    return facts


def _aimed_region(facts: list[_Item]) -> Region | None:
    """A região onde pesa mais o grupo que as ações mais miraram."""
    groups: Counter[VoterGroup] = Counter(
        f.item.group for f in facts if f.item.group is not None
    )
    if not groups:
        return None
    group = groups.most_common(1)[0][0]
    return max(Region, key=lambda region: places.region_mixture(region)[group])
