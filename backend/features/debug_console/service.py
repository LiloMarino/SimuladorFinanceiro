"""O catálogo e a execução dos comandos do console do modo debug sobre a partida em andamento."""

from backend.core import repository
from backend.core.dto.debug_console import (
    DebugArgumentDTO,
    DebugChoiceDTO,
    DebugCommandDTO,
    DebugCommandResultDTO,
    DebugCommandsDTO,
)
from backend.features.debug_console.commands import COMMANDS
from backend.features.debug_console.parser import parse
from backend.features.debug_console.registry import (
    Argument,
    ArgumentKind,
    ConsoleContext,
)
from backend.features.simulation.simulation import Simulation


def _context(simulation: Simulation) -> ConsoleContext:
    return ConsoleContext(
        simulation=simulation,
        players=repository.simulation_player.participants(simulation.settings.id),
    )


def _choices(
    argument: Argument, context: ConsoleContext
) -> list[DebugChoiceDTO] | None:
    """As escolhas que o argumento aceita agora; nulas quando o argumento é um valor livre."""
    simulation = context.simulation
    match argument.kind:
        case ArgumentKind.PLAYER:
            return [
                DebugChoiceDTO(value=p.nickname, label="bot" if p.is_bot else None)
                for p in context.players
            ]
        case ArgumentKind.TICKER:
            return [
                DebugChoiceDTO(value=t, label=None) for t in simulation.debug_tickers()
            ]
        case ArgumentKind.TITLE:
            return [
                DebugChoiceDTO(value=code, label=asset.name)
                for code, asset in simulation.debug_titles(None).items()
            ]
        case ArgumentKind.EVENT:
            return [
                DebugChoiceDTO(value=e.key, label=e.label)
                for e in simulation.debug_life_events()
            ]
        case ArgumentKind.PARTY:
            return [
                DebugChoiceDTO(value=abbr, label=None)
                for abbr in simulation.debug_party_abbrs()
            ]
        case ArgumentKind.COMMAND:
            return [DebugChoiceDTO(value=name, label=None) for name in COMMANDS]
        case ArgumentKind.MONEY | ArgumentKind.QUANTITY | ArgumentKind.PERCENT:
            return None


def catalog(simulation: Simulation) -> DebugCommandsDTO:
    """Os comandos com as escolhas atuais de cada argumento."""
    with simulation.lock:
        context = _context(simulation)
        return DebugCommandsDTO(
            commands=[
                DebugCommandDTO(
                    name=command.name,
                    help=command.help,
                    arguments=[
                        DebugArgumentDTO(
                            name=argument.name,
                            help=argument.help,
                            required=argument.required,
                            choices=_choices(argument, context),
                        )
                        for argument in command.arguments
                    ],
                )
                for command in COMMANDS.values()
            ]
        )


def run(simulation: Simulation, line: str) -> DebugCommandResultDTO:
    """Interpreta a linha e executa o comando sob o lock da partida; o erro do comando volta como erro do projeto."""
    with simulation.lock:
        context = _context(simulation)
        command, values = parse(line, context)
        return DebugCommandResultDTO(message=command.handler(context, *values))
