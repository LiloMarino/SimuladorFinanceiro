from backend.core.runtime.simulation_manager import SimulationManager


def get_active_simulation():
    """
    Dependency que retorna a simulação ativa.

    - Se não existir, SimulationManager levanta NoActiveSimulationError
    """
    return SimulationManager.get_active_simulation()
