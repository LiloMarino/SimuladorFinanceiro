from backend.core import repository
from backend.core.dto.simulation import (
    SimulationDTO,
    SimulationSettingsDTO,
    SimulationStatusResponse,
    SimulationSummaryDTO,
)
from backend.core.exceptions.http_exceptions import UnprocessableEntityError
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.utils import next_business_day
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

        SimulationManager.clear_simulation()
        SimulationManager.set_simulation_id(simulation_id)
        sim = Simulation(SimulationDTO(id=simulation_id, **settings.model_dump()))
        SimulationManager.register_simulation(sim)
        SettingsManager.clear()
        simulation_controller.start()
        notify(
            "simulation_started",
            SimulationStatusResponse(active=True, simulation=sim.settings).to_json(),
        )
        return sim.settings

    @classmethod
    def load(cls, summary: SimulationSummaryDTO) -> SimulationDTO:
        """
        Retoma uma simulação existente no dia útil seguinte ao último dia registrado.

        Eventos são a fonte da verdade: um dia sem evento nem snapshot não mudou
        nada persistido, então reprocessar os dias depois do último registro chega
        ao mesmo estado em que o jogador parou.
        """
        last_dates = [
            d
            for d in (
                repository.event.get_last_event_date(summary.id),
                repository.snapshot.get_last_snapshot_date(summary.id),
            )
            if d is not None
        ]
        resume_from = max(last_dates) if last_dates else None

        if resume_from and next_business_day(resume_from) > summary.end_date:
            raise UnprocessableEntityError(
                "A simulação já chegou na data final e não pode ser continuada."
            )

        SimulationManager.clear_simulation()
        SimulationManager.set_simulation_id(summary.id)
        sim = Simulation(
            SimulationDTO(
                id=summary.id,
                name=summary.name,
                start_date=summary.start_date,
                end_date=summary.end_date,
                starting_cash=summary.starting_cash,
                monthly_contribution=summary.monthly_contribution,
                price_impact_enabled=summary.price_impact_enabled,
                price_impact_k=summary.price_impact_k,
                price_impact_decay_days=summary.price_impact_decay_days,
            ),
            resume_from=resume_from,
        )
        repository.simulation.touch_last_simulated(summary.id)
        SimulationManager.register_simulation(sim)
        SettingsManager.clear()
        simulation_controller.start()
        notify(
            "simulation_started",
            SimulationStatusResponse(active=True, simulation=sim.settings).to_json(),
        )
        return sim.settings
