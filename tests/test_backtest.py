"""Backtest: partida só de estratégias, rodada pelo host sem espera entre os pregões."""

from __future__ import annotations

import threading
import time
from collections.abc import Iterator
from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from backend.core import repository
from backend.core.dto.backtest import (
    BacktestConfigDTO,
    BacktestParticipantDTO,
    BacktestProgressEventDTO,
)
from backend.core.enum import (
    BacktestPriceImpact,
    IndicatorSeries,
    SimulationStatus,
)
from backend.core.models.models import Snapshots
from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.core.utils import next_business_day
from backend.features.backtest import config as backtest_config
from backend.features.backtest import service
from backend.features.backtest.progress import SAMPLE_EVERY, BacktestProgress
from backend.features.backtest.reference import (
    ReferenceWallet,
    references_from_contributions,
)
from backend.features.simulation.saved_simulation import describe
from backend.features.simulation.simulation_loader import SimulationLoader
from backend.features.simulation.simulation_loop import simulation_controller
from backend.features.strategy.moving_average import MovingAverageCross
from tests.fakes import simulation_settings
from tests.test_simulation_loader import started  # noqa: F401

START = date(2004, 3, 1)
END = date(2004, 5, 26)
TIMEOUT = 60

Events = list[tuple[str, dict]]


def participant(nickname: str, color: str, key: str = "buy_and_hold"):
    return BacktestParticipantDTO(nickname=nickname, color=color, strategy_key=key)


def config(**changes: object) -> BacktestConfigDTO:
    base = {
        "name": "Médias contra o mercado",
        "start_date": START,
        "end_date": END,
        "starting_cash": Decimal(10000),
        "monthly_contribution": Decimal(500),
        "price_impact": BacktestPriceImpact.OFF,
        "participants": [
            participant("Tio Patinhas", "chart-1"),
            participant("Rentista", "chart-2", "cdi_100"),
            participant("Grafista", "chart-3", "moving_average_cross"),
        ],
    }
    return BacktestConfigDTO.model_validate({**base, **changes})


@pytest.fixture
def events(started, monkeypatch: pytest.MonkeyPatch) -> Iterator[Events]:  # noqa: F811
    """Sala vazia, com as regras no período do histórico, e os avisos do backtest gravados."""
    monkeypatch.setattr(SettingsManager, "_settings", simulation_settings())
    sent: Events = []

    def notify(event: str, payload: dict, to: object = None) -> None:
        sent.append((event, payload))

    monkeypatch.setattr(
        RealtimeBrokerManager, "get_broker", lambda: SimpleNamespace(notify=notify)
    )
    yield sent
    # O teste que parou no meio deixa o loop parado; o que terminou já o liberou
    wait_released()


def wait_released() -> None:
    deadline = time.monotonic() + TIMEOUT
    while SimulationManager.has_backtest():
        assert time.monotonic() < deadline, "o backtest não terminou"
        time.sleep(0.05)


def names(events: Events) -> list[str]:
    return [event for event, _ in events]


def total_days() -> int:
    return backtest_config.trading_days(START, END)


def run_to_the_end(events: Events, **changes: object) -> int:
    simulation_id = service.start(config(**changes)).progress.simulation_id  # type: ignore[union-attr]
    wait_released()
    return simulation_id


def test_backtest_runs_to_the_end_without_waiting_or_per_day_events(events):
    started_at = time.monotonic()
    simulation_id = run_to_the_end(events)

    # Sem o `sleep` entre pregões, 63 pregões não levam nem segundos de jogo
    assert time.monotonic() - started_at < TIMEOUT
    emitted = names(events)
    assert "backtest_started" in emitted
    assert emitted[-1] == "backtest_ended"
    assert events[-1][1] == {"reason": "completed", "simulation_id": simulation_id}
    for per_day in (
        "simulation_update",
        "stocks_update",
        "portfolio_update",
        "snapshot_update",
        "simulation_started",
        "simulation_ended",
    ):
        assert per_day not in emitted


def test_progress_is_sent_every_twenty_days_and_at_the_last_one(events):
    run_to_the_end(events)

    progress = [
        BacktestProgressEventDTO.model_validate(payload)
        for event, payload in events
        if event == "backtest_progress"
    ]
    days = total_days()
    assert [p.progress.done_days for p in progress] == [
        *range(SAMPLE_EVERY, days, SAMPLE_EVERY),
        days,
    ]
    # Cada aviso leva só os pontos novos: um por passo
    assert all(len(p.points) == 1 for p in progress)
    last = progress[-1].points[0]
    assert len(last.equity) == 3
    assert last.contributed == Decimal(10000) + 3 * Decimal(500)


def test_the_finished_backtest_is_saved_as_a_backtest_with_every_day_recorded(events):
    simulation_id = run_to_the_end(events)

    summary = repository.simulation.get_simulation(simulation_id)
    assert summary is not None
    assert summary.is_backtest
    saved = describe(summary, None, [])
    assert saved.status is SimulationStatus.FINISHED
    assert saved.players_count == 3
    contributions = repository.snapshot.contributions(simulation_id)
    assert len(contributions) == total_days()
    # Os bots moram na partida salva; a sala continua sem eles
    assert UserManager.room_bots() == []


def test_light_snapshots_match_the_values_the_events_add_up_to(events, market: Engine):
    simulation_id = run_to_the_end(events)
    bots = repository.simulation_player.participants(simulation_id)
    last_day = nth_day(total_days())
    with Session(market) as session:
        stored = {
            row.user_id: row
            for row in session.scalars(
                select(Snapshots).where(
                    Snapshots.simulation_id == simulation_id,
                    Snapshots.snapshot_date == last_day,
                )
            )
        }
    assert set(stored) == {bot.id for bot in bots}

    SimulationManager.set_simulation_id(simulation_id)
    for bot in bots:
        # O caminho completo soma o caixa e o aporte direto dos eventos
        full = repository.snapshot.create_snapshot(
            user_id=bot.id,
            snapshot_date=last_day,
            total_equity=Decimal(0),
            total_fixed=Decimal(0),
            total_debt=Decimal(0),
        )
        assert stored[bot.id].total_cash == full.total_cash
        assert stored[bot.id].total_contribution == full.total_contribution
        assert stored[bot.id].total_networth == (
            stored[bot.id].total_cash
            + stored[bot.id].total_equity
            + stored[bot.id].total_fixed
            - stored[bot.id].total_debt
        )


def nth_day(n: int) -> date:
    day = next_business_day(START - timedelta(days=1))
    for _ in range(n - 1):
        day = next_business_day(day)
    return day


def hold_after_first_step(monkeypatch: pytest.MonkeyPatch) -> tuple[threading.Event]:
    """O loop espera no primeiro aviso de andamento até o host pedir para parar."""
    reached = threading.Event()
    original = BacktestProgress.publish

    def publish(self: BacktestProgress) -> None:
        original(self)
        reached.set()
        simulation_controller._stop_event.wait(TIMEOUT)

    monkeypatch.setattr(BacktestProgress, "publish", publish)
    return (reached,)


def test_stopping_saves_up_to_where_it_got_and_can_be_reviewed(events, monkeypatch):
    (reached,) = hold_after_first_step(monkeypatch)
    simulation_id = service.start(config()).progress.simulation_id  # type: ignore[union-attr]
    assert reached.wait(TIMEOUT)

    assert service.stop() == simulation_id

    assert not SimulationManager.has_running_simulation()
    assert events[-1] == (
        "backtest_ended",
        {"reason": "stopped", "simulation_id": simulation_id},
    )
    summary = repository.simulation.get_simulation(simulation_id)
    assert summary is not None
    saved = describe(summary, None, [])
    assert saved.status is SimulationStatus.PAUSED
    assert saved.resume_from == nth_day(SAMPLE_EVERY)
    # O lote pendente é gravado antes de liberar: nenhum pregão se perde
    assert len(repository.snapshot.contributions(simulation_id)) == SAMPLE_EVERY
    result = service.result(simulation_id)
    assert not result.finished
    assert result.stopped_on == nth_day(SAMPLE_EVERY)
    assert result.done_days == SAMPLE_EVERY


def test_discarding_deletes_the_backtest_and_its_bots(events, monkeypatch):
    (reached,) = hold_after_first_step(monkeypatch)
    simulation_id = service.start(config()).progress.simulation_id  # type: ignore[union-attr]
    assert reached.wait(TIMEOUT)
    bots = repository.simulation_player.participants(simulation_id)

    service.discard()

    assert repository.simulation.get_simulation(simulation_id) is None
    assert all(repository.user.get_by_client_id(b.client_id) is None for b in bots)
    assert events[-1][1]["reason"] == "discarded"


def test_a_match_in_progress_refuses_the_backtest(events, monkeypatch):
    monkeypatch.setattr(SimulationManager, "_active_simulation", object())

    with pytest.raises(HTTPException) as error:
        service.start(config())

    assert error.value.status_code == 409


def test_a_running_backtest_refuses_another_and_is_not_a_match(events, monkeypatch):
    (reached,) = hold_after_first_step(monkeypatch)
    service.start(config())
    assert reached.wait(TIMEOUT)

    # Para a sala não há partida, mas o motor está ocupado
    assert not SimulationManager.has_active_simulation()
    assert SimulationManager.has_running_simulation()
    with pytest.raises(HTTPException) as error:
        service.start(config(name="Outro"))
    assert error.value.status_code == 409
    assert service.status().progress is not None

    service.stop()


def test_the_room_bots_stay_as_they_are(events):
    room_bot = UserManager.add_bot("Bot da sala", "buy_and_hold", {})
    before = UserManager.room_bots()

    run_to_the_end(events)

    after = UserManager.room_bots()
    assert [b.id for b, _ in after] == [room_bot.id]
    assert after == before
    assert repository.user.get_by_client_id(room_bot.client_id) is not None


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"start_date": date(1990, 1, 1)}, "O mercado começa"),
        ({"end_date": date(2030, 1, 1)}, "O mercado vai até"),
        ({"end_date": date(2004, 4, 15)}, "ao menos"),
        (
            {
                "participants": [
                    participant("Igual", "chart-1"),
                    participant("igual", "chart-2"),
                ]
            },
            "se chamam",
        ),
        (
            {
                "participants": [
                    participant("Um", "chart-1"),
                    participant("Dois", "chart-1"),
                ]
            },
            "mesma cor",
        ),
    ],
)
def test_invalid_period_and_participants_are_refused_with_422(events, changes, message):
    with pytest.raises(HTTPException) as error:
        service.start(config(**changes))

    assert error.value.status_code == 422
    assert message in str(error.value.detail)
    assert repository.simulation.list_simulations() == []


def test_strategy_params_are_validated_by_the_strategy(events):
    bad = BacktestParticipantDTO(
        nickname="Quebrado",
        color="chart-1",
        strategy_key="moving_average_cross",
        params={"short_window": 500, "long_window": 5},
    )

    with pytest.raises(HTTPException) as error:
        service.start(config(participants=[bad]))

    assert error.value.status_code == 422


def test_eleven_participants_do_not_fit(events):
    many = [participant(f"Bot {n}", "chart-1") for n in range(11)]

    with pytest.raises(ValidationError):
        config(participants=many)


def test_the_same_strategy_can_enter_more_than_once(events):
    twice = [
        participant("Primeiro", "chart-1"),
        participant("Segundo", "chart-2"),
    ]

    simulation_id = run_to_the_end(events, participants=twice)

    assert len(repository.simulation_player.participants(simulation_id)) == 2


def test_config_of_returns_the_configuration_that_went_in(events):
    entered = config(price_impact=BacktestPriceImpact.STRONG)
    resolved = [p for p, _ in backtest_config.resolve(entered)]

    simulation_id = run_to_the_end(events, price_impact=BacktestPriceImpact.STRONG)

    assert backtest_config.config_of(simulation_id) == entered.model_copy(
        update={"participants": resolved}
    )


def test_setup_reopens_the_latest_backtest_with_a_free_name(events):
    empty = backtest_config.setup(None)
    assert empty.config is None
    assert empty.coverage.first_date is not None

    simulation_id = run_to_the_end(events)

    again = backtest_config.setup(None)
    assert again.config is not None
    assert again.config.name == "Médias contra o mercado (2)"
    assert backtest_config.setup(simulation_id).config == again.config


def test_a_backtest_cannot_be_continued_as_a_match(events):
    simulation_id = run_to_the_end(events)
    summary = repository.simulation.get_simulation(simulation_id)
    assert summary is not None

    with pytest.raises(HTTPException) as error:
        SimulationLoader.load(summary)

    assert error.value.status_code == 422


def test_the_result_has_the_reference_series_over_the_recorded_days(events):
    simulation_id = run_to_the_end(events)

    result = service.result(simulation_id)

    assert result.finished
    assert result.done_days == result.total_days == total_days()
    assert len(result.references) == total_days()
    assert result.references[0].contributed == Decimal(10500)
    assert result.references[-1].contributed == Decimal(10000) + 3 * Decimal(500)
    assert result.failures == []


def test_reference_wallet_matches_a_hand_calculation_with_monthly_deposits(
    indicators,
):
    days = [date(2004, 1, 5), date(2004, 1, 6), date(2004, 2, 2), date(2004, 2, 3)]
    # CDI de 0,05% ao dia e um Ibovespa que sobe 10% a cada mês
    indicators(
        IndicatorSeries.CDI,
        {date(2004, 1, 1) + timedelta(days=n): Decimal("0.05") for n in range(60)},
    )
    indicators(
        IndicatorSeries.IBOV,
        {
            days[0]: Decimal(100),
            days[1]: Decimal(100),
            days[2]: Decimal(110),
            days[3]: Decimal(110),
        },
    )
    contributions = [
        (days[0], Decimal(100)),
        (days[1], Decimal(100)),
        (days[2], Decimal(200)),
        (days[3], Decimal(200)),
    ]

    points = references_from_contributions(Decimal(1000), contributions)

    rate = Decimal("0.0005")
    # Dia 1: R$ 1.000 de saldo e R$ 100 do primeiro aporte entram juntos
    cdi = Decimal(1100)
    assert points[0].cdi == cdi
    assert points[0].ibov == Decimal(1100)
    # Dia 2: só rende
    cdi *= 1 + rate
    assert points[1].cdi == cdi
    # Dia 3: rende e entra o aporte de R$ 100 do segundo mês
    cdi = cdi * (1 + rate) + 100
    assert points[2].cdi == cdi
    assert points[2].contributed == Decimal(1200)
    # O Ibovespa: 11 cotas compradas a 100, mais 100/110 a 110, valendo 110 cada
    units = Decimal(11) + Decimal(100) / Decimal(110)
    assert points[2].ibov == units * 110
    cdi *= 1 + rate
    assert points[3].cdi == cdi


def test_reference_wallet_has_no_ibovespa_line_without_the_index(indicators):
    indicators(IndicatorSeries.CDI, {date(2004, 1, 5): Decimal("0.05")})
    wallet = ReferenceWallet(Decimal(1000))

    point = wallet.step(date(2004, 1, 5), Decimal(0))

    assert point.ibov is None
    assert point.cdi == Decimal(1000)


def test_strategy_failure_is_recorded_and_the_portfolio_stays(events, monkeypatch):
    def broken(self, ctx, params):
        raise RuntimeError("quebrou")

    monkeypatch.setattr(MovingAverageCross, "next", broken)

    simulation_id = run_to_the_end(events)

    result = service.result(simulation_id)
    assert result.finished
    assert [f.nickname for f in result.failures] == ["Grafista"]
    assert "deu erro" in result.failures[0].message
    progress = [
        BacktestProgressEventDTO.model_validate(p)
        for e, p in events
        if e == "backtest_progress"
    ]
    assert any(f.nickname == "Grafista" for p in progress for f in p.failures)
