"""Ciclo de vida do loop da partida, com uma simulação dublê de tick instantâneo."""

from __future__ import annotations

import contextlib
import logging
import threading
from collections.abc import Callable, Iterator
from types import SimpleNamespace

import pytest

from backend.core.exceptions import NoActiveSimulationError
from backend.core.exceptions.http_exceptions import ServiceUnavailableError
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.simulation import simulation_loop
from backend.features.simulation.simulation_loop import SimulationLoopController

SIMULATION_ID = 7
TIMEOUT = 5


class _FakeSimulation:
    """
    Partida de `days` pregões. `on_tick[n]` roda dentro do pregão n, na thread do
    loop, e `fail_on` faz o pregão de número dado levantar.
    """

    def __init__(
        self,
        log: list[str],
        days: int,
        speed: int = 1000,
        fail_on: int | None = None,
    ) -> None:
        self.settings = SimpleNamespace(id=SIMULATION_ID)
        self.log = log
        self.days = days
        self.ticks = 0
        self.fail_on = fail_on
        self.on_tick: dict[int, Callable[[], object]] = {}
        self.ticked = threading.Event()
        self.paused = threading.Event()
        self._speed = speed
        self.lock = threading.RLock()

    def get_speed(self) -> int:
        if self._speed <= 0:
            self.paused.set()
        return self._speed

    def set_speed(self, speed: int) -> None:
        self._speed = speed

    def next_tick(self) -> None:
        if self.ticks >= self.days:
            raise StopIteration
        self.ticks += 1
        self.ticked.set()
        if self.ticks == self.fail_on:
            raise RuntimeError("pregão quebrado")
        if self.ticks in self.on_tick:
            self.on_tick[self.ticks]()

    def cancel_open_orders(self) -> int:
        self.log.append("cancel_open_orders")
        return 0

    def end_match(self) -> None:
        self.log.append("end_match")


class _Loop:
    def __init__(self, controller: SimulationLoopController, log: list[str]) -> None:
        self.controller = controller
        self.log = log
        self.sleeps: list[float] = []
        self.ended: list[dict] = []
        self.still_active_at_end: list[bool] = []

    def play(
        self, simulation: _FakeSimulation, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(SimulationManager, "_active_simulation", simulation)
        monkeypatch.setattr(SimulationManager, "_simulation_id", SIMULATION_ID)
        self.controller.start()

    def join(self) -> None:
        """Espera a thread do loop terminar."""
        for thread in threading.enumerate():
            if thread.name == "simulation-loop":
                thread.join(TIMEOUT)
                assert not thread.is_alive()


@pytest.fixture
def loop(monkeypatch: pytest.MonkeyPatch) -> Iterator[_Loop]:
    """Controlador novo, com flush, notificação e espera entre pregões gravados."""
    log: list[str] = []
    fake = _Loop(SimulationLoopController(), log)
    monkeypatch.setattr(SimulationManager, "_active_simulation", None)
    monkeypatch.setattr(SimulationManager, "_simulation_id", None)
    monkeypatch.setattr(EventManager, "flush", lambda: log.append("flush"))
    monkeypatch.setattr(simulation_loop.time, "sleep", fake.sleeps.append)

    def _notify(event: str, payload: dict, to: object = None) -> None:
        log.append(event)
        if event == "simulation_ended":
            fake.ended.append(payload)
            fake.still_active_at_end.append(SimulationManager.has_active_simulation())

    monkeypatch.setattr(simulation_loop, "notify", _notify)
    yield fake

    # O teste que já encerrou a partida deixa o loop parado
    with contextlib.suppress(ValueError):
        fake.controller.stop()
    fake.join()


def test_match_runs_to_the_end_and_releases_the_simulation(loop, monkeypatch):
    simulation = _FakeSimulation(loop.log, days=3)

    loop.play(simulation, monkeypatch)
    loop.join()

    assert simulation.ticks == 3
    assert loop.log == [
        "cancel_open_orders",
        "flush",
        "end_match",
        "simulation_ended",
    ]
    assert loop.ended == [{"reason": "completed", "simulation_id": SIMULATION_ID}]
    assert loop.still_active_at_end == [False]
    assert not SimulationManager.has_active_simulation()


def test_start_without_simulation_is_refused(loop):
    with pytest.raises(NoActiveSimulationError):
        loop.controller.start()


def test_second_start_while_running_is_ignored(loop, monkeypatch):
    simulation = _FakeSimulation(loop.log, days=3, speed=0)
    loop.play(simulation, monkeypatch)
    assert simulation.paused.wait(TIMEOUT)

    loop.controller.start()

    loops = [t for t in threading.enumerate() if t.name == "simulation-loop"]
    assert len(loops) == 1


def test_paused_match_waits_and_resumes_where_it_stopped(loop, monkeypatch):
    simulation = _FakeSimulation(loop.log, days=5)

    def pause() -> None:
        simulation.set_speed(0)
        loop.controller.pause()

    simulation.on_tick[2] = pause
    loop.play(simulation, monkeypatch)

    assert simulation.paused.wait(TIMEOUT)
    assert simulation.ticks == 2
    assert loop.ended == []

    simulation.set_speed(1000)
    loop.controller.unpause()
    loop.join()

    assert simulation.ticks == 5
    assert len(loop.ended) == 1


def test_interval_between_days_follows_the_speed(loop, monkeypatch):
    simulation = _FakeSimulation(loop.log, days=4, speed=2)
    # A velocidade nova vale a partir do pregão seguinte ao da troca
    simulation.on_tick[2] = lambda: simulation.set_speed(4)

    loop.play(simulation, monkeypatch)
    loop.join()

    assert loop.sleeps == [0.5, 0.5, 0.25, 0.25]


def test_pause_between_speed_read_and_tick_does_not_start_another_day(
    loop, monkeypatch
):
    simulation = _FakeSimulation(loop.log, days=1)
    original = simulation.get_speed
    first = True

    def read_speed():
        nonlocal first
        speed = original()
        if first:
            first = False
            simulation.set_speed(0)
            loop.controller.pause()
        return speed

    monkeypatch.setattr(simulation, "get_speed", read_speed)
    loop.play(simulation, monkeypatch)
    assert simulation.paused.wait(TIMEOUT)
    assert simulation.ticks == 0
    simulation.set_speed(1000)
    loop.controller.unpause()
    loop.join()
    assert simulation.ticks == 1


def test_stop_ends_the_running_match(loop, monkeypatch):
    simulation = _FakeSimulation(loop.log, days=10**9)
    loop.play(simulation, monkeypatch)
    assert simulation.ticked.wait(TIMEOUT)

    loop.controller.stop()

    assert loop.log[-2:] == ["cancel_open_orders", "flush"]
    assert not SimulationManager.has_active_simulation()
    # O aviso de fim pelo host sai da rota, não do loop
    assert loop.ended == []
    assert "end_match" not in loop.log
    with pytest.raises(ValueError, match="Nenhuma simulação"):
        loop.controller.stop()


def test_error_in_a_day_releases_the_simulation_and_warns_the_players(
    loop, monkeypatch, caplog
):
    simulation = _FakeSimulation(loop.log, days=5, fail_on=2)

    with caplog.at_level(logging.CRITICAL):
        loop.play(simulation, monkeypatch)
        loop.join()

    assert simulation.ticks == 2
    critical = [r for r in caplog.records if r.levelno == logging.CRITICAL]
    assert len(critical) == 1
    assert critical[0].exc_info is not None
    assert loop.log == ["cancel_open_orders", "flush", "simulation_ended"]
    assert loop.ended == [{"reason": "error", "simulation_id": SIMULATION_ID}]
    assert loop.still_active_at_end == [False]
    assert not SimulationManager.has_active_simulation()
    with pytest.raises(ValueError, match="Nenhuma simulação"):
        loop.controller.stop()


def test_failure_while_closing_the_match_still_releases_it(loop, monkeypatch, caplog):
    simulation = _FakeSimulation(loop.log, days=5, fail_on=1)

    def broken_flush() -> None:
        raise RuntimeError("banco fora")

    monkeypatch.setattr(EventManager, "flush", broken_flush)

    with caplog.at_level(logging.CRITICAL):
        loop.play(simulation, monkeypatch)
        loop.join()

    assert loop.ended == [{"reason": "error", "simulation_id": SIMULATION_ID}]
    assert not SimulationManager.has_active_simulation()
    # O loop parado aceita a próxima partida
    loop.play(_FakeSimulation(loop.log, days=1), monkeypatch)
    loop.join()
    assert len(loop.ended) == 2


def test_stop_past_the_timeout_leaves_the_match_to_the_thread(loop, monkeypatch):
    simulation = _FakeSimulation(loop.log, days=10**9)
    release = threading.Event()
    simulation.on_tick[1] = lambda: release.wait(TIMEOUT)
    monkeypatch.setattr(simulation_loop, "STOP_TIMEOUT", 0.05)
    loop.play(simulation, monkeypatch)
    assert simulation.ticked.wait(TIMEOUT)

    with pytest.raises(ServiceUnavailableError):
        loop.controller.stop()

    # O pregão em andamento segue com a partida registrada
    assert "flush" not in loop.log
    assert SimulationManager.has_active_simulation()

    release.set()
    loop.join()

    assert loop.log == ["cancel_open_orders", "flush"]
    assert not SimulationManager.has_active_simulation()
    assert loop.ended == []


def test_pause_arriving_after_stop_does_not_hold_the_thread(loop, monkeypatch):
    simulation = _FakeSimulation(loop.log, days=3, speed=0)
    original = simulation.get_speed
    errors: list[BaseException] = []

    def stop() -> None:
        try:
            loop.controller.stop()
        except BaseException as exc:
            errors.append(exc)

    stopping = threading.Thread(target=stop)

    def read_speed():
        # Entre a leitura da velocidade e a espera da pausa, o host encerra e um
        # pedido de pausa chega logo atrás
        if stopping.ident is None:
            stopping.start()
            assert loop.controller._stop_event.wait(TIMEOUT)
            loop.controller.pause()
        return original()

    monkeypatch.setattr(simulation, "get_speed", read_speed)
    monkeypatch.setattr(simulation_loop, "STOP_TIMEOUT", 1.0)
    loop.play(simulation, monkeypatch)
    assert simulation.paused.wait(TIMEOUT)
    stopping.join(TIMEOUT)
    loop.join()

    assert errors == []
    assert not SimulationManager.has_active_simulation()
