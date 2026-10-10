from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.runtime.simulation_manager import SimulationManager


def get_active_simulation():
    return SimulationManager.get_active_simulation()


def require_no_active_simulation() -> None:
    """A rota só responde fora da partida: o motor lê as séries a cada tick."""
    if SimulationManager.has_active_simulation():
        raise ConflictError("A Central de dados só abre fora da partida.")
