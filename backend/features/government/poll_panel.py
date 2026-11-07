"""A pesquisa como sai para o jogador: o voto exato com o erro sorteado dentro da margem de cada grupo."""

from datetime import date
from decimal import Decimal

from backend.core.dto.government import GroupPollDTO, PollDTO, PollEntryDTO
from backend.core.enum import Region
from backend.features.government import places, voters


def publish(exact: voters.Vote, day: date, seed: int, with_margin: bool) -> voters.Vote:
    """
    A pesquisa como sai: o voto de cada grupo com o erro sorteado dentro da margem do
    grupo, e o total somado deles. Assim o total e as barras dos grupos batem, e o erro
    do total fica perto dos 3 pontos que a pesquisa anuncia.
    """
    if not with_margin:
        return exact
    groups = {}
    for group, result in exact.groups.items():
        shares = {
            pid: voters.published(
                value, voters.MARGINS[group], seed, day, group.value, pid
            )
            for pid, value in result.shares.items()
        }
        rest = voters.HUNDRED - sum(shares.values(), Decimal(0))
        groups[group] = voters.GroupVote(shares, max(Decimal(0), rest))
    return voters.combine(groups)


def place_vote(
    exact: voters.Vote,
    place: places.Place,
    day: date,
    seed: int,
    with_margin: bool,
) -> voters.Vote:
    """
    A pesquisa num estado ou região, a partir do voto exato por grupo do país. O exato do
    estado soma os grupos pela mistura dele; o publicado traz o erro sorteado pela
    semente da partida, limitado à margem do estado. A região é a média dos estados
    publicados, pesada pelo eleitorado.
    """
    if isinstance(place, Region):
        return _region_vote(exact, place, day, seed, with_margin)
    local = voters.combine(exact.groups, weights=places.mixture(place))
    if not with_margin:
        return local
    margin = places.margin(place)
    total = {
        pid: voters.published(value, margin, seed, day, place.value, pid)
        for pid, value in local.total.items()
    }
    undecided = max(Decimal(0), voters.HUNDRED - sum(total.values(), Decimal(0)))
    return voters.Vote(groups=local.groups, total=total, undecided=undecided)


def _region_vote(
    exact: voters.Vote, region: Region, day: date, seed: int, with_margin: bool
) -> voters.Vote:
    states = places.states_of(region)
    votes = [place_vote(exact, s, day, seed, with_margin) for s in states]
    weights = [Decimal(places.ELECTORATE[s]) for s in states]
    whole = sum(weights, Decimal(0))
    parties = {pid for v in votes for pid in v.total}
    total = {
        pid: sum(
            (
                w * v.total.get(pid, Decimal(0))
                for w, v in zip(weights, votes, strict=True)
            ),
            Decimal(0),
        )
        / whole
        for pid in parties
    }
    undecided = (
        sum((w * v.undecided for w, v in zip(weights, votes, strict=True)), Decimal(0))
        / whole
    )
    return voters.Vote(groups={}, total=total, undecided=undecided)


def entries(points: dict[int, Decimal]) -> list[PollEntryDTO]:
    return [
        PollEntryDTO(party_id=pid, points=value)
        for pid, value in sorted(points.items())
    ]


def poll_dto(day: date, vote: voters.Vote, with_margin: bool) -> PollDTO:
    return PollDTO(
        date=day,
        entries=entries(vote.total),
        undecided=vote.undecided,
        margin=voters.TOTAL_MARGIN if with_margin else 0,
        groups=group_polls(vote, with_margin),
    )


def group_polls(vote: voters.Vote, with_margin: bool) -> list[GroupPollDTO]:
    return [
        GroupPollDTO(
            group=group,
            entries=entries(result.shares),
            undecided=result.undecided,
            margin=voters.MARGINS[group] if with_margin else 0,
        )
        for group, result in vote.groups.items()
    ]
