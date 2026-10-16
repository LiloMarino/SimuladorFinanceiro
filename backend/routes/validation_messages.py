"""Frases em português para os erros de validação do Pydantic."""

from collections.abc import Sequence

from pydantic_core import ErrorDetails

from backend.routes.error import ValidationErrorItem

# Onde o FastAPI encontrou o valor; o que vem depois é o nome do campo
LOCATIONS = ("body", "query", "path", "header", "cookie")

# `{field}` é o nome do campo; os demais placeholders são o `ctx` do Pydantic
PHRASES = {
    "missing": "O campo {field} é obrigatório.",
    "int_parsing": "O campo {field} precisa ser um número inteiro.",
    "int_from_float": "O campo {field} precisa ser um número inteiro.",
    "int_type": "O campo {field} precisa ser um número inteiro.",
    "float_parsing": "O campo {field} precisa ser um número.",
    "float_type": "O campo {field} precisa ser um número.",
    "decimal_parsing": "O campo {field} precisa ser um número.",
    "decimal_type": "O campo {field} precisa ser um número.",
    "bool_parsing": "O campo {field} precisa ser verdadeiro ou falso.",
    "bool_type": "O campo {field} precisa ser verdadeiro ou falso.",
    "string_type": "O campo {field} precisa ser um texto.",
    "date_parsing": "O campo {field} precisa ser uma data válida (AAAA-MM-DD).",
    "date_from_datetime_parsing": "O campo {field} precisa ser uma data válida.",
    "date_type": "O campo {field} precisa ser uma data válida (AAAA-MM-DD).",
    "datetime_parsing": "O campo {field} precisa ser uma data e hora válidas.",
    "datetime_type": "O campo {field} precisa ser uma data e hora válidas.",
    "uuid_parsing": "O campo {field} precisa ser um identificador válido.",
    "uuid_type": "O campo {field} precisa ser um identificador válido.",
    "string_pattern_mismatch": "O campo {field} está em um formato não aceito.",
    "greater_than": "O campo {field} precisa ser maior que {gt:g}.",
    "greater_than_equal": "O campo {field} precisa ser no mínimo {ge:g}.",
    "less_than": "O campo {field} precisa ser menor que {lt:g}.",
    "less_than_equal": "O campo {field} precisa ser no máximo {le:g}.",
    "string_too_short": "O campo {field} é curto demais (mínimo de {min_length}).",
    "string_too_long": "O campo {field} é longo demais (máximo de {max_length}).",
    "enum": "O campo {field} aceita apenas: {expected}.",
    "literal_error": "O campo {field} aceita apenas: {expected}.",
}

# Falhas do corpo inteiro, sem campo para citar
BODY_PHRASES = {
    "json_invalid": "O corpo da requisição não é um JSON válido.",
    "model_type": "O corpo da requisição precisa ser um objeto.",
    "dict_type": "O corpo da requisição precisa ser um objeto.",
}

EMPTY_FIELD = "O campo {field} não pode ficar vazio."
FALLBACK_WITH_FIELD = "O campo {field} é inválido."
FALLBACK = "Os dados enviados não são válidos."


def field_name(loc: Sequence[str | int]) -> str | None:
    """Nome do campo no `loc`, sem o prefixo de onde ele veio (body, query...)."""
    names = [part for part in loc if isinstance(part, str) and part not in LOCATIONS]
    return names[-1] if names else None


def describe_validation_error(error: ErrorDetails) -> str:
    """A frase em português de uma falha de validação."""
    error_type = error["type"]
    ctx = error.get("ctx") or {}
    field = field_name(error["loc"])

    # O validador do projeto já escreve a frase em português
    if error_type == "value_error" and "error" in ctx:
        return str(ctx["error"])
    if error_type in BODY_PHRASES:
        return BODY_PHRASES[error_type]
    if field is None:
        return FALLBACK

    if error_type == "string_too_short" and ctx.get("min_length") == 1:
        return EMPTY_FIELD.format(field=field)
    template = PHRASES.get(error_type, FALLBACK_WITH_FIELD)
    return template.format(field=field, **ctx)


def format_validation_errors(errors: Sequence[ErrorDetails]) -> str:
    """Uma frase única para o `message`: as falhas em sequência, sem repetir."""
    phrases = dict.fromkeys(describe_validation_error(e) for e in errors)
    return " ".join(phrases) or FALLBACK


def to_items(errors: Sequence[ErrorDetails]) -> list[ValidationErrorItem]:
    return [
        ValidationErrorItem(
            loc=list(e["loc"]), msg=describe_validation_error(e), type=e["type"]
        )
        for e in errors
    ]
