"""
A política razoável de cada profissão: o que o bot faz com a mecânica dela, uma função
pura do estado, do dia, da economia do mês e da reserva do jogador. O módulo só conhece os tipos do núcleo e
da economia, para que quem simula fora do motor use a mesma regra do bot.
"""

from collections.abc import Callable
from datetime import date

from backend.core.dto.profession import MechanicAction, MechanicState
from backend.core.enum import Profession
from backend.features.economy.growth import MacroMonth
from backend.features.profession.clt import overtime_policy
from backend.features.profession.reserve import Reserve

# Devolve a ação do mês ou nulo quando a política não faz nada
Policy = Callable[[MechanicState, date, MacroMonth, Reserve], MechanicAction | None]

POLICIES: dict[Profession, Policy] = {
    Profession.CLT: overtime_policy,
}


def policy_action(
    profession: Profession,
    state: MechanicState,
    day: date,
    macro: MacroMonth,
    reserve: Reserve,
) -> MechanicAction | None:
    """A ação que a política da profissão toma no dia; nula quando a profissão não tem política."""
    policy = POLICIES.get(profession)
    return None if policy is None else policy(state, day, macro, reserve)
