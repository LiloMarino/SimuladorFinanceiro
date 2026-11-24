"""O catálogo e a execução dos comandos do console do modo debug."""

from pydantic import Field

from backend.core.dto.base import BaseDTO


class DebugChoiceDTO(BaseDTO):
    """Um valor que o argumento aceita agora, com a descrição que o console mostra ao lado."""

    value: str
    label: str | None


class DebugArgumentDTO(BaseDTO):
    name: str
    help: str
    required: bool
    # As escolhas atuais da partida; nulo quando o argumento é livre (um valor digitado)
    choices: list[DebugChoiceDTO] | None


class DebugCommandDTO(BaseDTO):
    name: str
    help: str
    arguments: list[DebugArgumentDTO]


class DebugCommandsDTO(BaseDTO):
    commands: list[DebugCommandDTO]


class DebugCommandRequest(BaseDTO):
    line: str = Field(min_length=1, max_length=300)


class DebugCommandResultDTO(BaseDTO):
    message: str
