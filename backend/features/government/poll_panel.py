"""A pesquisa como sai para o jogador: o voto exato com o erro sorteado dentro da margem de cada grupo."""

from datetime import date
from decimal import Decimal

from backend.core.dto.government import GroupPollDTO, PollDTO, PollEntryDTO
from backend.features.government import voters


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
