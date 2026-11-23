from dataclasses import replace
from datetime import date
from decimal import ROUND_CEILING, Decimal

from backend.core import repository
from backend.core.dto.fund import FundContributionRequest, FundFoundRequest
from backend.core.dto.simulation import (
    SimulationDTO,
    SimulationSettingsDTO,
    SimulationStatusResponse,
    SimulationSummaryDTO,
)
from backend.core.dto.user import UserDTO
from backend.core.enum import PlayerGrouping, Profession
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    UnprocessableEntityError,
)
from backend.core.indicators import ensure_indicator_coverage
from backend.core.life_budget import LifeBudget
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.core.utils import format_money
from backend.features.candle_challenge.game import candle_game
from backend.features.government import preparation
from backend.features.government.room_preparation import RoomPreparation
from backend.features.realtime import notify
from backend.features.simulation.room_fund_preparation import RoomFundPreparation
from backend.features.simulation.saved_simulation import (
    is_finished,
    leader_reached_goal,
    resume_point,
)
from backend.features.simulation.simulation import Simulation
from backend.features.simulation.simulation_loop import simulation_controller
from backend.features.statistics.report import build_overview_report
from backend.features.strategy.bots import validate_room_bots


class SimulationLoader:
    @staticmethod
    def _ensure_no_backtest() -> None:
        if SimulationManager.has_backtest():
            raise ConflictError("Há um backtest em andamento.")

    @staticmethod
    def _starting_cash_by_user(
        settings: SimulationSettingsDTO,
        professions: dict[int, Profession],
        user_ids: list[int],
        joined: date,
    ) -> dict[int, Decimal]:
        """O caixa inicial de cada jogador pela profissão dele; sem profissões, o da sala vale para todos (mapa vazio)."""
        if not settings.uses_professions:
            return {}
        life = LifeBudget.of(settings)
        return {
            user_id: life.for_profession(professions[user_id]).starting_capital(
                settings.starting_cash, joined, settings.end_date
            )
            for user_id in user_ids
        }

    @staticmethod
    def _opening_professions(
        settings: SimulationSettingsDTO,
        professions: dict[int, Profession],
        user_ids: list[int],
    ) -> dict[int, Profession]:
        """A profissão com que cada jogador abre o primeiro período; sem profissões, todos são CLT."""
        return {
            user_id: professions.get(user_id, Profession.CLT)
            if settings.uses_professions
            else Profession.CLT
            for user_id in user_ids
        }

    @classmethod
    def _ensure_goal_above_room_capital(cls, settings: SimulationSettingsDTO) -> None:
        """A meta passa do maior capital inicial da sala, humanos e bots; abaixo disso alguém vence no primeiro dia."""
        if not settings.uses_professions:
            return
        players = UserManager.list_active_players()
        capitals = cls._starting_cash_by_user(
            settings,
            UserManager.chosen_professions(),
            [p.id for p in players],
            settings.start_date,
        )
        richest = max(players, key=lambda p: capitals[p.id], default=None)
        if richest is None:
            return
        capital = capitals[richest.id]
        if LifeBudget.of(settings).goal_on(settings.start_date) <= capital:
            minimum = format_money(capital.to_integral_value(rounding=ROUND_CEILING))
            raise UnprocessableEntityError(
                f"Meta mínima de {minimum.removesuffix(',00')} por causa de {richest.nickname}."
            )

    @staticmethod
    def _ensure_commissioned_parties(humans: list[UserDTO]) -> None:
        """Conferido ao iniciar: todo Comissionado da sala leva o partido de uma sigla que a partida terá."""
        valid = RoomPreparation.party_abbrs(humans)
        parties = UserManager.chosen_parties()
        stale = [
            p.nickname
            for p in humans
            if UserManager.get_profession(p.id) is Profession.COMMISSIONED
            and parties.get(p.id) not in valid
        ]
        if stale:
            raise ConflictError(
                f"Escolha de novo o partido do Comissionado: {', '.join(stale)}."
            )

    @classmethod
    def create(cls, settings: SimulationSettingsDTO) -> SimulationDTO:
        """Persiste, instancia e inicia uma nova simulação com quem está na sala."""
        cls._ensure_no_backtest()
        ensure_indicator_coverage(settings.start_date)
        in_teams = settings.player_grouping is PlayerGrouping.TEAMS
        # Na aquisição hostil em equipes a equipe nasce das gestoras e o bot joga sem equipe
        if in_teams and not settings.is_takeover_teams:
            UserManager.ensure_teams_ready({})
        humans = [p for p in UserManager.list_active_players() if not p.is_bot]
        RoomPreparation.ensure_ready(humans)
        if settings.uses_professions:
            cls._ensure_commissioned_parties(humans)
        RoomFundPreparation.ensure_ready(
            humans,
            enabled=settings.funds_enabled,
            takeover=settings.is_fund_takeover,
            teams=settings.is_takeover_teams,
        )
        # As regras de agora valem para cada bot antes de a partida ser gravada
        validate_room_bots(settings.start_date)
        cls._ensure_goal_above_room_capital(settings)
        bots = UserManager.room_bots()
        simulation_id = repository.simulation.create_simulation(settings)
        # As estatais da base viram as estatais da partida, só quando há governo
        if settings.government_enabled:
            repository.state_company.copy_marks(simulation_id)

        # O primeiro tick da Simulation já lê os participantes, que gravam antes dela
        room_colors = UserManager.room_colors()
        repository.simulation_player.save(
            simulation_id,
            room_colors,
            (
                RoomFundPreparation.teams(humans)
                if settings.is_takeover_teams
                else UserManager.chosen_teams()
            )
            if in_teams
            else None,
            UserManager.chosen_professions() if settings.uses_professions else None,
            UserManager.chosen_parties() if settings.uses_professions else None,
        )
        repository.profession.open(
            simulation_id,
            cls._opening_professions(
                settings, UserManager.chosen_professions(), list(room_colors)
            ),
            settings.start_date,
        )
        portfolios = repository.portfolio.open(
            simulation_id,
            list(room_colors),
            settings.start_date,
            settings.starting_cash,
            cls._starting_cash_by_user(
                settings,
                UserManager.chosen_professions(),
                list(room_colors),
                settings.start_date,
            ),
        )
        # A preparação do lobby vira evento da partida, cada jogador com a contribuição do perfil
        preparation.record(
            simulation_id,
            settings.start_date,
            [
                replace(
                    p,
                    contribution=repository.settings.get_party_contribution(p.user_id),
                )
                for p in RoomPreparation.prepared(humans)
            ],
        )
        RoomPreparation.clear()
        founders = RoomFundPreparation.prepared(humans)
        comanagers = RoomFundPreparation.accepted_comanagers(humans)
        RoomFundPreparation.clear()
        UserManager.release_bots()
        UserManager.release_saved_colors()
        UserManager.release_room_teams()

        SimulationManager.clear_simulation()
        SimulationManager.set_simulation_id(simulation_id, portfolios)
        sim = Simulation(
            SimulationDTO(id=simulation_id, **settings.model_dump()),
            random_seed=repository.simulation.get_random_seed(simulation_id),
        )
        SimulationManager.register_simulation(sim)
        # Quem escolheu fundar leva a gestora (fechada, taxas zero) já no 1º dia
        if settings.funds_enabled:
            for founder, identity in founders:
                fund = sim.found_fund(
                    founder,
                    FundFoundRequest(
                        name=identity.name,
                        ticker=identity.ticker,
                        management_fee=Decimal(0),
                        performance_fee=Decimal(0),
                    ),
                )
                # Os co-gestores combinados no lobby entram ativos, com a parte valendo desde o 1º mês
                for guest, share in comanagers.get(founder.id, []):
                    sim.seat_fund_comanager(fund.id, guest.id, share)
                # No modo aquisição hostil toda a carteira do jogador entra na gestora no 1º dia
                if settings.is_fund_takeover:
                    sim.contribute_to_fund(
                        founder,
                        fund.id,
                        FundContributionRequest(cash=sim.get_cash(founder.client_id)),
                    )
                # Em equipes o caixa de cada co-gestor também entra na gestora da equipe e vira cotas dele
                if settings.is_takeover_teams:
                    for guest, _ in comanagers.get(founder.id, []):
                        sim.pool_cash_into_fund(fund.id, guest)
        # Cada bot joga a estratégia dele desde o primeiro pregão que o relógio roda
        for bot, config in bots:
            sim.set_my_strategy(bot, config.strategy_key, config.params)
        SettingsManager.clear()
        # A partida começa: o desafio da vela do lobby, se rolava, é descartado
        candle_game.abort()
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
        overview = build_overview_report([summary.id])
        if leader_reached_goal(overview):
            raise UnprocessableEntityError(
                "Alguém já chegou à meta dessa simulação: ela não pode ser continuada."
            )
        if overview.survivor_nickname is not None:
            raise UnprocessableEntityError(
                "Só restou um jogador ativo nessa simulação: ela não pode ser continuada."
            )
        ensure_indicator_coverage(summary.start_date)

        saved = repository.simulation_player.colors(summary.id)
        in_teams = summary.player_grouping is PlayerGrouping.TEAMS
        # Na aquisição hostil em equipes os times são os da largada; quem chega depois joga sem equipe
        if in_teams and not summary.is_takeover_teams:
            UserManager.ensure_teams_ready(
                repository.simulation_player.teams(summary.id)
            )
        newcomers = {
            user_id: color
            for user_id, color in UserManager.room_colors().items()
            if user_id not in saved
        }
        room_teams = (
            UserManager.chosen_teams()
            if in_teams and not summary.is_takeover_teams
            else {}
        )
        room_professions = (
            UserManager.chosen_professions() if summary.uses_professions else {}
        )
        repository.simulation_player.save(
            summary.id,
            newcomers,
            {
                user_id: room_teams[user_id]
                for user_id in newcomers
                if user_id in room_teams
            }
            if in_teams
            else None,
            {user_id: room_professions[user_id] for user_id in newcomers}
            if summary.uses_professions
            else None,
            {
                user_id: party
                for user_id, party in UserManager.chosen_parties().items()
                if user_id in newcomers
            }
            if summary.uses_professions
            else None,
        )
        repository.profession.open(
            summary.id,
            cls._opening_professions(summary, room_professions, list(newcomers)),
            resume_from or summary.start_date,
        )
        repository.portfolio.open(
            summary.id,
            list(newcomers),
            resume_from or summary.start_date,
            summary.starting_cash,
            cls._starting_cash_by_user(
                summary,
                room_professions,
                list(newcomers),
                resume_from or summary.start_date,
            ),
        )
        RoomPreparation.clear()
        RoomFundPreparation.clear()
        UserManager.release_bots()
        UserManager.release_saved_colors()
        UserManager.release_room_teams()

        # O registro das estratégias volta ao último dia processado, como os eventos
        if resume_from is not None:
            repository.strategy.rewind(summary.id, resume_from)
            repository.house_report.rewind(summary.id, resume_from)

        SimulationManager.clear_simulation()
        SimulationManager.set_simulation_id(
            summary.id, repository.portfolio.ids(summary.id)
        )
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
        # A partida começa: o desafio da vela do lobby, se rolava, é descartado
        candle_game.abort()
        simulation_controller.start()
        notify(
            "simulation_started",
            SimulationStatusResponse(active=True, simulation=sim.settings).to_json(),
        )
        return sim.settings
