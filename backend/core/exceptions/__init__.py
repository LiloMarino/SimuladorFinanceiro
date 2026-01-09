from werkzeug.exceptions import Forbidden, Unauthorized


class NoActiveSimulationError(Forbidden):
    """Não existe uma simulação ativa."""

    description = "Não existe uma simulação ativa"


class SessionNotInitializedError(Unauthorized):
    """Sessão do usuário não iniciada."""

    description = "Sessão não iniciada"


class InsufficentCashError(Forbidden):
    """O usuário não possui saldo suficiente para completar a operação."""

    description = "Saldo insuficiente para completar a operação"


class InsufficentPositionError(Forbidden):
    """O usuário não possui posição suficiente para completar a operação."""

    description = "Posição insuficiente para completar a operação"
