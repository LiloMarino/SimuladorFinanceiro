"""O ranking de partidos: a soma do patrimônio dos filiados, sem os partidos do computador."""

from decimal import Decimal

from backend.core import repository
from backend.core.dto.player_history import PlayerHistoryDTO
from backend.core.dto.statistics_report import PartyRankingDTO
from backend.features.government.state import replay

FALLBACK_COLOR = "#7d879b"


def party_ranking(
    simulation_id: int, players: list[PlayerHistoryDTO]
) -> list[PartyRankingDTO]:
    state = replay(repository.government.get_events(simulation_id))
    nicknames = {
        user.id: user.nickname
        for user in repository.simulation_player.participants(simulation_id)
    }
    networth = {p.player_nickname: p.history[-1].total_networth for p in players}

    totals = []
    for party in state.player_parties():
        members = [nicknames[u] for u in party.members if u in nicknames]
        totals.append(
            (
                party,
                members,
                sum((networth.get(m, Decimal(0)) for m in members), Decimal(0)),
            )
        )
    totals.sort(key=lambda item: (-item[2], item[0].id))

    leader = totals[0][2] if totals else Decimal(0)
    return [
        PartyRankingDTO(
            party_id=party.id,
            abbr=party.abbr,
            name=party.name,
            color=party.color or FALLBACK_COLOR,
            position=position,
            members=members,
            total_networth=value,
            leader_gap=leader - value,
        )
        for position, (party, members, value) in enumerate(totals, start=1)
    ]
