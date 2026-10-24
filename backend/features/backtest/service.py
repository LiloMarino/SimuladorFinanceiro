"""Início, parada e descarte do backtest, e o resultado de um backtest salvo."""

import logging
from uuid import uuid4

from backend import config as app_config
from backend.core import repository
from backend.core.dto.backtest import (
    BacktestConfigDTO,
    BacktestEndedEventDTO,
    BacktestFailureDTO,
    BacktestReferencePointDTO,
    BacktestResultDTO,
    BacktestStatusDTO,
)
from backend.core.dto.simulation import SimulationDTO
from backend.core.enum import StrategyLogKind
from backend.core.exceptions.http_exceptions import ConflictError, NotFoundError
from backend.core.indicators import ensure_indicator_coverage
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.backtest import config as backtest_config
from backend.features.backtest.progress import BacktestProgress
from backend.features.backtest.reference import references_from_contributions
from backend.features.realtime import notify
from backend.features.simulation.saved_simulation import is_finished, resume_point
from backend.features.simulation.simulation import Simulation
from backend.features.simulation.simulation_loop import simulation_controller

logger = logging.getLogger(__name__)


def start(config: BacktestConfigDTO) -> BacktestStatusDTO:
    """
    Grava e inicia o backtest. O molde é o início de uma partida (`SimulationLoader`)
    sem as partes da sala: os participantes são bots criados só para ele, e a sala,
    as cores dela e as últimas regras ficam como estão.
    """
    if SimulationManager.has_running_simulation():
        raise ConflictError(
            "Já há uma partida ou um backtest em andamento: espere ele acabar."
        )
    participants = backtest_config.resolve(config)
    settings = backtest_config.settings_of(config)
    ensure_indicator_coverage(settings.start_date)

    simulation_id = repository.simulation.create_simulation(settings, is_backtest=True)
    try:
        bots = [
            repository.user.create_user(uuid4(), participant.nickname, is_bot=True)
            for participant, _ in participants
        ]
        repository.simulation_player.save(
            simulation_id,
            {bot.id: p.color for bot, (p, _) in zip(bots, participants, strict=True)},
        )
        repository.user.seed_simulation_users(
            simulation_id,
            [bot.id for bot in bots],
            settings.start_date,
            settings.starting_cash,
        )

        SimulationManager.clear_simulation()
        SimulationManager.set_simulation_id(simulation_id)
        progress = BacktestProgress(
            simulation_id=simulation_id,
            name=settings.name,
            host_nickname=app_config.toml.host.nickname,
            start_date=settings.start_date,
            end_date=settings.end_date,
            starting_cash=settings.starting_cash,
            total_days=backtest_config.trading_days(
                settings.start_date, settings.end_date
            ),
            participants=[p for p, _ in participants],
            user_ids=[bot.id for bot in bots],
        )
        sim = Simulation(
            SimulationDTO(id=simulation_id, **settings.model_dump()),
            random_seed=repository.simulation.get_random_seed(simulation_id),
            backtest=progress,
        )
        SimulationManager.register_simulation(sim, backtest=True)
        # Cada participante joga a estratégia dele desde o primeiro pregão que corre
        for bot, (_, bot_config) in zip(bots, participants, strict=True):
            sim.set_my_strategy(bot, bot_config.strategy_key, bot_config.params)
    except Exception:
        logger.exception(
            "Falha ao preparar o backtest; a partida gravada é descartada."
        )
        SimulationManager.clear_simulation()
        repository.simulation.delete(simulation_id)
        raise

    status = progress.status()
    simulation_controller.start()
    notify("backtest_started", status.to_json())
    return status


def status() -> BacktestStatusDTO:
    """O andamento do backtest que roda; sem ele, o andamento vem vazio."""
    backtest = (
        SimulationManager.get_active_simulation().backtest
        if SimulationManager.has_backtest()
        else None
    )
    if backtest is None:
        return BacktestStatusDTO(progress=None, participants=[], points=[], failures=[])
    return backtest.status()


def _end(reason: str) -> int:
    """Para o loop, que grava o lote pendente e libera o motor, e avisa a sala."""
    if not SimulationManager.has_backtest():
        raise ConflictError("Não há backtest em andamento.")
    simulation_id = SimulationManager.get_active_simulation_id()
    try:
        simulation_controller.stop()
    except ValueError:
        # O backtest acabou sozinho entre a conferência e a parada
        raise ConflictError("Não há backtest em andamento.") from None
    notify(
        "backtest_ended",
        BacktestEndedEventDTO(reason=reason, simulation_id=simulation_id).to_json(),
    )
    return simulation_id


def stop() -> int:
    """Para o backtest e o deixa salvo até onde chegou; devolve o id dele."""
    return _end("stopped")


def discard() -> None:
    """Para o backtest e apaga o que ele gravou."""
    repository.simulation.delete(_end("discarded"))


def result(simulation_id: int) -> BacktestResultDTO:
    """O backtest salvo: a configuração, onde parou e a série de referência do relatório."""
    config = backtest_config.config_of(simulation_id)
    summary = repository.simulation.get_simulation(simulation_id)
    if summary is None:
        raise NotFoundError("Backtest não encontrado.")

    contributions = repository.snapshot.contributions(simulation_id)
    references = references_from_contributions(summary.starting_cash, contributions)
    resumed = resume_point(simulation_id)

    nicknames = {
        user.id: user.nickname
        for user in repository.simulation_player.participants(simulation_id)
    }
    failures = [
        BacktestFailureDTO(
            nickname=nicknames.get(row.user_id, ""),
            day=row.event_date,
            message=row.reason or "",
        )
        for row in repository.strategy.mode_rows(simulation_id)
        if row.kind is StrategyLogKind.ERROR
    ]
    return BacktestResultDTO(
        simulation_id=simulation_id,
        config=config,
        stopped_on=resumed,
        finished=is_finished(summary.end_date, resumed),
        total_days=backtest_config.trading_days(summary.start_date, summary.end_date),
        done_days=len(contributions),
        references=[
            BacktestReferencePointDTO(
                day=point.day,
                contributed=point.contributed,
                cdi=point.cdi,
                ibov=point.ibov,
            )
            for point in references
        ],
        failures=failures,
    )
