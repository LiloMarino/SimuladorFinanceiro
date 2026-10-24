from backend.core import repository
from backend.core.dto.simulation import (
    SimulationDTO,
    SimulationSettingsDTO,
    SimulationStatusResponse,
    SimulationSummaryDTO,
)
from backend.core.enum import PlayerGrouping
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    UnprocessableEntityError,
)
from backend.core.indicators import ensure_indicator_coverage
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.realtime import notify
from backend.features.simulation.saved_simulation import (
    is_finished,
    leader_reached_goal,
    resume_point,
)
from backend.features.simulation.simulation import Simulation
from backend.features.simulation.simulation_loop import simulation_controller
from backend.features.statistics.report import build_overview_report


class SimulationLoader:
    @staticmethod
    def _ensure_no_backtest() -> None:
        if SimulationManager.has_backtest():
            raise ConflictError("Há um backtest em andamento.")

    @classmethod
    def create(cls, settings: SimulationSettingsDTO) -> SimulationDTO:
        """Persiste, instancia e inicia uma nova simulação com quem está na sala."""
        cls._ensure_no_backtest()
        ensure_indicator_coverage(settings.start_date)
        in_teams = settings.player_grouping is PlayerGrouping.TEAMS
        if in_teams:
            UserManager.ensure_teams_ready({})
        # As regras de agora valem para cada bot antes de a partida ser gravada
        UserManager.validate_bots(settings.start_date)
        bots = UserManager.room_bots()
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
        UserManager.release_bots()
        UserManager.release_saved_colors()
        UserManager.release_room_teams()

        SimulationManager.clear_simulation()
        SimulationManager.set_simulation_id(simulation_id)
        sim = Simulation(
            SimulationDTO(id=simulation_id, **settings.model_dump()),
            random_seed=repository.simulation.get_random_seed(simulation_id),
        )
        SimulationManager.register_simulation(sim)
        # Cada bot joga a estratégia dele desde o primeiro pregão que o relógio roda
        for bot, config in bots:
            sim.set_my_strategy(bot, config.strategy_key, config.params)
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
        cls._ensure_no_backtest()
        if summary.is_backtest:
            raise UnprocessableEntityError("Backtest não se continua: rode de novo.")
        resume_from = resume_point(summary.id)

        if is_finished(summary.end_date, resume_from):
            raise UnprocessableEntityError(
                "A simulação já chegou na data final e não pode ser continuada."
            )
        if leader_reached_goal(build_overview_report([summary.id])):
            raise UnprocessableEntityError(
                "Alguém já chegou à meta dessa simulação: ela não pode ser continuada."
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
        UserManager.release_bots()
        UserManager.release_saved_colors()
        UserManager.release_room_teams()

        # O registro das estratégias volta ao último dia processado, como os eventos
        if resume_from is not None:
            repository.strategy.rewind(summary.id, resume_from)

        SimulationManager.clear_simulation()
        SimulationManager.set_simulation_id(summary.id)
        sim = Simulation(
            SimulationDTO.model_validate(
                summary.model_dump(include=set(SimulationDTO.model_fields))
            ),
            resume_from=resume_from,
            random_seed=repository.simulation.get_random_seed(summary.id),
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
