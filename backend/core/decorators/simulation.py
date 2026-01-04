from functools import wraps

from backend.core.runtime.simulation_manager import SimulationManager


def require_simulation(func):
    """
    Decorator que injeta a simulação ativa como keyword argument `simulation`.

    - Se não houver simulação ativa, SimulationManager lança `NoActiveSimulationError`.
    - Pode ser usado em qualquer posição na assinatura da função.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        kwargs["simulation"] = SimulationManager.get_active_simulation()
        return func(*args, **kwargs)

    return wrapper
