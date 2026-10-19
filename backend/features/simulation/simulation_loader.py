from backend.core import repository
from backend.core.dto.simulation import (
    SimulationDTO,
    SimulationSettingsDTO,
    SimulationStatusResponse,
    SimulationSummaryDTO,
)
from backend.core.enum import PlayerGrouping
from backend.core.exceptions.http_exceptions import UnprocessableEntityError
from backend.core.indicators import ensure_indicator_coverage
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.realtime import notify
from backend.features.simulation.saved_simulation import is_finished, resume_point
from backend.features.simulation.simulation import Simulation
from backend.features.simulation.simulation_loop import simulation_controller


class SimulationLoader:
    @classmethod
    def create(cls, settings: SimulationSettingsDTO) -> SimulationDTO:
        """Persiste, instancia e inicia uma nova simulação com quem está na sala."""
        ensure_indicator_coverage(settings.start_date)
        in_teams = settings.player_grouping is PlayerGrouping.TEAMS
        if in_teams:
            UserManager.ensure_teams_ready({})
        simulation_id = repository.simulation.create_simulation(settings)

        # O primeiro tick da Simulation já lê os participantes, que gravam antes dela
        room_colors = UserManager.room_colors()
        repository.simulation_player.save(
            simulation_id, room_colors, UserManager.chosen_teams() if in_teams else None
        )
        repository.user.seed_simulation_users(
            simulation_id,
            list(room_colors),
            settings.start_date,
            settings.starting_cash,
        )
        UserManager.release_saved_colors()
        UserManager.release_room_teams()

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

        Quem está na sala e nunca jogou essa partida entra nela agora, com a cor
        que tem na sala e o depósito inicial datado do último dia processado.
        """
        resume_from = resume_point(summary.id)

        if is_finished(summary.end_date, resume_from):
            raise UnprocessableEntityError(
                "A simulação já chegou na data final e não pode ser continuada."
            )
        ensure_indicator_coverage(summary.start_date)

        saved = repository.simulation_player.colors(summary.id)
        in_teams = summary.player_grouping is PlayerGrouping.TEAMS
        if in_teams:
            UserManager.ensure_teams_ready(
                repository.simulation_player.teams(summary.id)
            )
        newcomers = {
            user_id: color
            for user_id, color in UserManager.room_colors().items()
            if user_id not in saved
        }
        room_teams = UserManager.chosen_teams() if in_teams else {}
        repository.simulation_player.save(
            summary.id,
            newcomers,
            {user_id: room_teams[user_id] for user_id in newcomers}
            if in_teams
            else None,
        )
        repository.user.seed_simulation_users(
            summary.id,
            list(newcomers),
            resume_from or summary.start_date,
            summary.starting_cash,
        )
        UserManager.release_saved_colors()
        UserManager.release_room_teams()

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
                victory_criterion=summary.victory_criterion,
                player_grouping=summary.player_grouping,
                team_naming=summary.team_naming,
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
