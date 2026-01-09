from backend.core.exceptions.http_exceptions import ForbiddenError, UnauthorizedError


class NoActiveSimulationError(ForbiddenError):
    """Não existe uma simulação ativa."""

    def __init__(self):
        super().__init__(detail="Não existe uma simulação ativa")


class SessionNotInitializedError(UnauthorizedError):
    """Sessão do usuário não iniciada."""

    def __init__(self):
        super().__init__(detail="Sessão não iniciada")


class InsufficentCashError(ForbiddenError):
    """O usuário não possui saldo suficiente para completar a operação."""

    def __init__(self):
        super().__init__(detail="Saldo insuficiente para completar a operação")


class InsufficentPositionError(ForbiddenError):
    """O usuário não possui posição suficiente para completar a operação."""

    def __init__(self):
        super().__init__(detail="Posição insuficiente para completar a operação")
