from backend.core import repository
from backend.core.dto.simulation import (
    SimulationDTO,
    SimulationSettingsDTO,
    SimulationSummaryDTO,
)
from backend.core.exceptions.http_exceptions import UnprocessableEntityError
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.realtime import notify
from backend.features.simulation.simulation import Simulation
from backend.features.simulation.simulation_loop import simulation_controller


class SimulationLoader:
    @classmethod
    def create(cls, settings: SimulationSettingsDTO) -> SimulationDTO:
        """Persiste, instancia e inicia uma nova simulação."""
        simulation_id = repository.simulation.create_simulation(settings)
        repository.user.seed_simulation_users(
            simulation_id, settings.start_date, settings.starting_cash
        )

        sim = Simulation(SimulationDTO(id=simulation_id, **settings.model_dump()))
        SimulationManager.register_simulation(sim)
        SettingsManager.clear()
        simulation_controller.start()
        notify(
            "simulation_started", {"active": True, "simulation": sim.settings.to_json()}
        )
        return sim.settings

    @classmethod
    def load(cls, summary: SimulationSummaryDTO) -> SimulationDTO:
        """Retoma uma simulação existente a partir do último snapshot."""
        last_snapshot_date = repository.snapshot.get_last_snapshot_date(summary.id)
        resume_start = last_snapshot_date or summary.start_date

        if resume_start >= summary.end_date:
            raise UnprocessableEntityError(
                "A simulação já chegou na data final e não pode ser continuada."
            )

        sim = Simulation(
            SimulationDTO(
                id=summary.id,
                name=summary.name,
                start_date=resume_start,
                end_date=summary.end_date,
                starting_cash=summary.starting_cash,
                monthly_contribution=summary.monthly_contribution,
            )
        )
        repository.simulation.touch_last_simulated(summary.id)
        SimulationManager.register_simulation(sim)
        SettingsManager.clear()
        simulation_controller.start()
        notify(
            "simulation_started", {"active": True, "simulation": sim.settings.to_json()}
        )
        return sim.settings
