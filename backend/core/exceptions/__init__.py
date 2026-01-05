class FixedIncomeExpiredAssetError(Exception):
    """Exceção lançada quando um ativo de renda fixa expirou."""

    pass


class NoActiveSimulationError(Exception):
    """Exceção lançada quando não há simulação ativa."""

    pass


class SessionNotInitializedError(Exception):
    """Raised when client_id cookie is missing."""

    pass


class PermissionDeniedError(Exception):
    """Raised when user lacks permission to access a resource."""

    pass
