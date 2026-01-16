from backend.core.runtime.simulation_manager import SimulationManager


def get_active_simulation():
    return SimulationManager.get_active_simulation()
