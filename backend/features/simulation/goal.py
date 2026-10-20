"""Regra da corrida à meta: quem chega ao patrimônio-alvo encerra a partida."""

from collections import defaultdict
from decimal import Decimal

from backend.features.statistics.teams import mean


def goal_reached(
    networths: dict[int, Decimal],
    teams: dict[int, int],
    goal: Decimal,
    in_teams: bool,
) -> bool:
    """
    Alguém chegou à meta: o patrimônio de um jogador (`networths`, por id) ou, em
    equipes, a média do patrimônio dos membros (`teams`, id → equipe).
    """
    if not in_teams:
        return any(networth >= goal for networth in networths.values())

    members: defaultdict[int, list[Decimal]] = defaultdict(list)
    for user_id, networth in networths.items():
        if user_id in teams:
            members[teams[user_id]].append(networth)
    return any((mean(values) or Decimal(0)) >= goal for values in members.values())
