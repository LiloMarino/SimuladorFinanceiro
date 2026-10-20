"""Regra da corrida à meta: quem chega ao patrimônio-alvo encerra a partida."""

from collections import defaultdict
from datetime import date
from decimal import Decimal

from backend.core.dto.simulation import SimulationSettingsDTO
from backend.core.enum import GameType
from backend.features.simulation.life_events import LifeBudget
from backend.features.statistics.teams import mean


def goal_on(settings: SimulationSettingsDTO, day: date) -> Decimal:
    """A meta do dia: a fixa da corrida, ou a do viver de renda, que sobe com a despesa."""
    if settings.game_type is GameType.FINANCIAL_INDEPENDENCE:
        return LifeBudget.of(settings).goal_on(day)
    return settings.goal_net_worth


def goal_steps(
    settings: SimulationSettingsDTO, until: date
) -> list[tuple[date, Decimal]]:
    """A meta em degraus até `until`: um ponto no início e outro a cada reajuste pelo IPCA."""
    if settings.game_type is GameType.FINANCIAL_INDEPENDENCE:
        days = LifeBudget.of(settings).readjustments(until)
    else:
        days = [settings.start_date]
    return [(day, goal_on(settings, day)) for day in days]


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
