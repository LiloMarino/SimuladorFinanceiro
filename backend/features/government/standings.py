"""O ranking de partidos pelo capital político, sem os partidos do computador."""

from backend.core import repository
from backend.core.dto.statistics_report import PartyRankingDTO
from backend.features.government.capital import party_capital
from backend.features.government.state import replay

FALLBACK_COLOR = "#7d879b"


def party_ranking(simulation_id: int) -> list[PartyRankingDTO]:
    state = replay(repository.government.get_events(simulation_id))
    nicknames = {
        user.id: user.nickname
        for user in repository.simulation_player.participants(simulation_id)
    }
    ranked = party_capital(state)

    leader = ranked[0][1].total if ranked else 0
    return [
        PartyRankingDTO(
            party_id=party.id,
            abbr=party.abbr,
            name=party.name,
            color=party.color or FALLBACK_COLOR,
            position=position,
            members=[nicknames[u] for u in party.members if u in nicknames],
            capital=capital,
            leader_gap=leader - capital.total,
        )
        for position, (party, capital) in enumerate(ranked, start=1)
    ]
