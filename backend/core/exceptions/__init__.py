from backend.core.exceptions.http_exceptions import ForbiddenError, UnauthorizedError


class NoActiveSimulationError(ForbiddenError):
    """Não existe uma simulação ativa."""

    def __init__(self, detail: str = "Não existe uma simulação ativa"):
        super().__init__(detail=detail)


class SessionNotInitializedError(UnauthorizedError):
    """Sessão do usuário não iniciada."""

    def __init__(self, detail: str = "Sessão não iniciada"):
        super().__init__(detail=detail)


class InsufficentCashError(ForbiddenError):
    """O usuário não possui saldo suficiente para completar a operação."""

    def __init__(self, detail: str = "Saldo insuficiente para completar a operação"):
        super().__init__(detail=detail)


class InsufficentPositionError(ForbiddenError):
    """O usuário não possui posição suficiente para completar a operação."""

    def __init__(self, detail: str = "Posição insuficiente para completar a operação"):
        super().__init__(detail=detail)
