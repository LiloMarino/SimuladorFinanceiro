from backend.core.exceptions.http_exceptions import ForbiddenError, UnauthorizedError


class NoActiveSimulationError(ForbiddenError):
    """Não existe uma simulação ativa."""

    description = "Não existe uma simulação ativa"


class SessionNotInitializedError(UnauthorizedError):
    """Sessão do usuário não iniciada."""

    description = "Sessão não iniciada"


class InsufficentCashError(ForbiddenError):
    """O usuário não possui saldo suficiente para completar a operação."""

    description = "Saldo insuficiente para completar a operação"


class InsufficentPositionError(ForbiddenError):
    """O usuário não possui posição suficiente para completar a operação."""

    description = "Posição insuficiente para completar a operação"
