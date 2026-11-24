"""A linha do console vira um comando do registro com os argumentos convertidos."""

import shlex
from decimal import Decimal, InvalidOperation

from backend.core.exceptions.http_exceptions import (
    NotFoundError,
    UnprocessableEntityError,
)
from backend.features.debug_console.commands import COMMANDS
from backend.features.debug_console.registry import (
    Argument,
    ArgumentKind,
    Command,
    ConsoleContext,
)

CENTS = Decimal("0.01")
HUNDRED = Decimal(100)


def parse(line: str, context: ConsoleContext) -> tuple[Command, list[object]]:
    """O comando da linha e os argumentos convertidos; a linha malformada volta como erro em português."""
    try:
        words = shlex.split(line)
    except ValueError as error:
        raise UnprocessableEntityError(
            "Aspas sem fechar: feche-as ou tire-as da linha."
        ) from error
    if not words:
        raise UnprocessableEntityError("Digite um comando; help lista os disponíveis.")
    found = COMMANDS.get(words[0].lower())
    if found is None:
        raise UnprocessableEntityError(
            f"Comando desconhecido: {words[0]}. help lista os disponíveis."
        )
    given = words[1:]
    required = sum(1 for argument in found.arguments if argument.required)
    if len(given) < required:
        missing = found.arguments[len(given)]
        raise UnprocessableEntityError(
            f"Falta o argumento <{missing.name}>. Uso: {found.usage}"
        )
    if len(given) > len(found.arguments):
        raise UnprocessableEntityError(f"Argumentos demais. Uso: {found.usage}")
    values = [
        _convert(argument, text, context)
        for argument, text in zip(found.arguments, given, strict=False)
    ]
    return found, values


def _convert(argument: Argument, text: str, context: ConsoleContext) -> object:
    match argument.kind:
        case ArgumentKind.PLAYER:
            return _player(text, context)
        case ArgumentKind.TICKER | ArgumentKind.EVENT:
            return text.upper()
        case ArgumentKind.TITLE | ArgumentKind.COMMAND:
            return text.lower()
        case ArgumentKind.PARTY:
            return _party(text, context)
        case ArgumentKind.MONEY:
            return _number(argument, text).quantize(CENTS)
        case ArgumentKind.QUANTITY:
            return _number(argument, text)
        case ArgumentKind.PERCENT:
            return _number(argument, text) / HUNDRED


def _player(text: str, context: ConsoleContext):
    wanted = text.casefold()
    for player in context.players:
        if player.nickname.casefold() == wanted:
            return player
    raise NotFoundError(f"Não há jogador com o apelido {text} nesta partida.")


def _party(text: str, context: ConsoleContext) -> str:
    """A sigla como a partida a escreve, quando o texto bate sem diferenciar maiúsculas."""
    wanted = text.casefold()
    for abbr in context.simulation.party_abbrs():
        if abbr.casefold() == wanted:
            return abbr
    return text


def _number(argument: Argument, text: str) -> Decimal:
    """O número digitado, com ponto ou vírgula decimal; texto que não é número finito volta como erro."""
    normalized = text.replace(",", ".") if "." not in text else text
    try:
        number = Decimal(normalized)
    except InvalidOperation:
        number = None
    if number is None or not number.is_finite():
        raise UnprocessableEntityError(
            f"<{argument.name}> pede um número, e {text} não é um."
        )
    return number
