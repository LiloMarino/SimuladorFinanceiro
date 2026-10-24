from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.runtime.simulation_manager import SimulationManager


def get_active_simulation():
    if SimulationManager.has_backtest():
        raise ConflictError("Há um backtest em andamento: não há partida para a sala.")
    return SimulationManager.get_active_simulation()


def require_no_active_simulation() -> None:
    """A rota só responde com o motor parado: ele lê as séries a cada tick."""
    if SimulationManager.has_running_simulation():
        raise ConflictError("A Central de dados só abre fora da partida e do backtest.")
