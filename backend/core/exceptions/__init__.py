from werkzeug.exceptions import Conflict, Forbidden, Unauthorized


class FixedIncomeExpiredAssetError(Conflict):
    """Exceção lançada quando um ativo de renda fixa expirou."""

    pass


class NoActiveSimulationError(Forbidden):
    """Não existe uma simulação ativa."""

    description = "Não existe uma simulação ativa"


class SessionNotInitializedError(Unauthorized):
    """Sessão do usuário não iniciada."""

    description = "Sessão não iniciada"


class PermissionDeniedError(Forbidden):
    """Usuário sem permissão para executar a ação."""

    description = "Permissão negada"
