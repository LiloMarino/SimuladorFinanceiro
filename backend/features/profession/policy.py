"""
A política razoável de cada profissão: o que o bot faz com a mecânica dela, uma função
pura do estado, do dia e da economia do mês. O módulo só conhece os tipos do núcleo e
da economia, para que quem simula fora do motor use a mesma regra do bot.
"""

from collections.abc import Callable
from datetime import date

from backend.core.dto.profession import MechanicAction, MechanicState
from backend.core.enum import Profession
from backend.features.economy.growth import MacroMonth

# Devolve a ação do mês ou nulo quando a política não faz nada
Policy = Callable[[MechanicState, date, MacroMonth], MechanicAction | None]

POLICIES: dict[Profession, Policy] = {}


def policy_action(
    profession: Profession,
    state: MechanicState,
    day: date,
    macro: MacroMonth,
) -> MechanicAction | None:
    """A ação que a política da profissão toma no dia; nula quando a profissão não tem política."""
    policy = POLICIES.get(profession)
    return None if policy is None else policy(state, day, macro)
