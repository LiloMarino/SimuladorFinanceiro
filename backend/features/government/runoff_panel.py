"""A disputa do 2º turno traduzida para o que o jogador vê: pesquisa semanal, transferência e o que cada partido pode fazer."""

from datetime import date
from decimal import Decimal

from backend.core.dto.government import (
    DeclarationDTO,
    PollEntryDTO,
    RunoffContributionDTO,
    RunoffRaceDTO,
    TransferDTO,
    TransferGroupDTO,
)
from backend.core.dto.simulation import SimulationDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import VoterGroup
from backend.core.utils import required
from backend.features.government import second_round, voters
from backend.features.government.government_book import GovernmentBook
from backend.features.government.poll_panel import entries, poll_dto, publish
from backend.features.government.state import GovernmentState

ZERO = Decimal(0)


def build_race(
    book: GovernmentBook,
    settings: SimulationDTO,
    viewer: UserDTO,
    people: dict[int, UserDTO],
    today: date,
) -> RunoffRaceDTO:
    state = book.state
    race = required(state.race)
    cycle = book.cycle()
    open_today = today <= cycle.donation_deadline
    mine = state.party_of(viewer.id)
    is_founder = mine is not None and mine.founder_id == viewer.id
    eliminated = set(state.results[-1].tickets) - set(race.finalists)
    margin = settings.poll_margin
    days = second_round.poll_days(required(state.race_started), cycle.donation_deadline)
    return RunoffRaceDTO(
        finalists=list(race.finalists),
        polls=[
            poll_dto(p.day, publish(p.vote, p.day, book.seed, margin), margin)
            for p in state.race_polls
        ],
        next_poll=next((d for d in days if d > today), None),
        transfers=[
            _transfer(state, race, pid)
            for pid in sorted(eliminated)
            if pid in state.parties
        ],
        declarations=[
            DeclarationDTO(
                date=d.day,
                party_id=d.party_id,
                nickname=_nickname(people, d.user_id),
                endorsed_party_id=d.endorsed_id,
            )
            for d in state.declarations
        ],
        contributions=[
            RunoffContributionDTO(
                date=c.day,
                nickname=_nickname(people, c.user_id),
                party_id=c.party_id,
                amount=c.amount,
            )
            for c in state.race_contributions
        ],
        my_contribution=next(
            (c.amount for c in state.race_contributions if c.user_id == viewer.id),
            None,
        ),
        can_declare=(
            open_today
            and is_founder
            and mine is not None
            and mine.id in eliminated
            and mine.id not in race.endorsements
        ),
        can_contribute=(
            open_today
            and mine is not None
            and mine.id in race.finalists
            and all(c.user_id != viewer.id for c in state.race_contributions)
        ),
        can_add_promise=(
            open_today
            and is_founder
            and mine is not None
            and mine.id in race.finalists
            and len(mine.promises) < second_round.MAX_PROMISES
        ),
        promise_limit=second_round.MAX_PROMISES,
    )


def _nickname(people: dict[int, UserDTO], user_id: int | None) -> str | None:
    user = people.get(user_id) if user_id is not None else None
    return user.nickname if user else None


def _transfer(
    state: GovernmentState, race: second_round.Race, eliminated: int
) -> TransferDTO:
    """Para onde foram os votos do partido que saiu: por grupo e somados pelo peso de cada um."""
    party = state.parties[eliminated]
    groups = []
    voted = ZERO
    undecided = ZERO
    sent_total = dict.fromkeys(race.finalists, ZERO)
    for group in VoterGroup:
        disputed = race.groups[group]
        weight = voters.WEIGHTS[group]
        group_voted = disputed.voted.get(eliminated, ZERO)
        group_sent = disputed.sent.get(eliminated, {})
        group_undecided = group_voted - sum(group_sent.values(), ZERO)
        voted += weight * group_voted
        undecided += weight * group_undecided
        for finalist, amount in group_sent.items():
            sent_total[finalist] += weight * amount
        trust = second_round.trust(
            voters.affinity(group, party.radar) + party.loyalty[group],
            party.rejection[group],
        )
        pool = disputed.pools.get(eliminated, ZERO)
        groups.append(
            TransferGroupDTO(
                group=group,
                voted=group_voted,
                sent=entries(group_sent),
                undecided=group_undecided,
                undecided_now=pool,
                trust=trust,
                would_follow=second_round.FOLLOW_MAX * trust * pool,
            )
        )
    declared = eliminated in race.endorsements
    return TransferDTO(
        party_id=eliminated,
        groups=groups,
        voted=voted,
        sent=[
            PollEntryDTO(party_id=pid, points=value)
            for pid, value in sorted(sent_total.items())
        ],
        undecided=undecided,
        declared=declared,
        endorsed_party_id=race.endorsements.get(eliminated),
    )
