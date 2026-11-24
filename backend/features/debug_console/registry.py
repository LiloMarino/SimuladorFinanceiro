"""Os tipos dos comandos do console do modo debug: nome, argumentos tipados, ajuda e handler."""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from backend.core.dto.user import UserDTO
from backend.features.simulation.simulation import Simulation


class ArgumentKind(StrEnum):
    """O que o argumento é: o parser converte o texto digitado e o catálogo lista as escolhas de cada tipo."""

    PLAYER = "player"
    TICKER = "ticker"
    TITLE = "title"
    EVENT = "event"
    PARTY = "party"
    COMMAND = "command"
    MONEY = "money"
    QUANTITY = "quantity"
    PERCENT = "percent"


@dataclass(frozen=True)
class Argument:
    name: str
    kind: ArgumentKind
    help: str
    required: bool = True


@dataclass(frozen=True)
class ConsoleContext:
    """A partida e os jogadores dela no instante do comando; os handlers agem só por aqui."""

    simulation: Simulation
    players: list[UserDTO]


Handler = Callable[..., str]


@dataclass(frozen=True)
class Command:
    name: str
    help: str
    arguments: tuple[Argument, ...]
    handler: Handler

    @property
    def usage(self) -> str:
        """A linha de uso: `add_cash <jogador> <valor>`, com `[ ]` nos argumentos opcionais."""
        parts = [f"<{a.name}>" if a.required else f"[{a.name}]" for a in self.arguments]
        return " ".join([self.name, *parts])
