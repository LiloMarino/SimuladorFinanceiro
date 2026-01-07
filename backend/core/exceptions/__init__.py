from werkzeug.exceptions import Forbidden, Unauthorized


class NoActiveSimulationError(Forbidden):
    """Não existe uma simulação ativa."""

    description = "Não existe uma simulação ativa"


class SessionNotInitializedError(Unauthorized):
    """Sessão do usuário não iniciada."""

    description = "Sessão não iniciada"
