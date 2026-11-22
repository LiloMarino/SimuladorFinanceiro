"""
As mecânicas das profissões: o que cada ação do jogador faz com o estado da mecânica
da profissão dele. Uma profissão com mecânica tem entrada aqui e o tipo do estado em
`STATE_TYPES`; a profissão sem entrada não tem mecânica e não aceita ação.
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date

from backend.core.dto.profession import MechanicAction, MechanicState
from backend.core.enum import Profession
from backend.core.exceptions.http_exceptions import ConflictError


@dataclass(frozen=True)
class Mechanic:
    """A mecânica de uma profissão: o tipo da ação e a regra que valida a ação e devolve o estado novo."""

    action_type: type[MechanicAction]
    # Recusa a ação que o estado ou o dia não permitem levantando um erro de requisição
    apply: Callable[[MechanicState, MechanicAction, date], MechanicState]


MECHANICS: dict[Profession, Mechanic] = {}


def apply_action(
    profession: Profession,
    state: MechanicState,
    action: MechanicAction,
    day: date,
) -> MechanicState:
    """O estado depois da ação, ou o erro de quem a pediu: a profissão sem mecânica e a ação de outra mecânica não passam."""
    mechanic = MECHANICS.get(profession)
    if mechanic is None:
        raise ConflictError("Esta profissão não tem mecânica.")
    if not isinstance(action, mechanic.action_type):
        raise ConflictError("Esta ação não é da mecânica da profissão.")
    return mechanic.apply(state, action, day)
