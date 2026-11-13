from __future__ import annotations

from datetime import date
from types import SimpleNamespace
from typing import cast

from backend.features.simulation.simulation import Simulation
from backend.routes.dependencies import ActiveSimulation
from backend.routes.statistics import get_next_update


def _simulation(current: date, start: date, end: date) -> ActiveSimulation:
    """Simulação mínima: só a data corrente e as datas das regras que o aviso lê."""
    simulation = SimpleNamespace(
        _current_date=current,
        settings=SimpleNamespace(start_date=start, end_date=end),
    )
    for name in ("next_statistics_update", "last_statistics_update"):
        method = getattr(Simulation, name)
        method = getattr(method, "__wrapped__", method)
        setattr(simulation, name, lambda method=method: method(simulation))
    return cast(ActiveSimulation, simulation)


def test_update_dates_are_the_month_turns_around_today():
    """A última atualização é a virada deste mês, e a próxima a do mês seguinte."""
    result = get_next_update(
        _simulation(date(2020, 3, 18), date(2020, 1, 6), date(2021, 1, 4))
    )
    assert result.last_update_date == date(2020, 3, 2)
    assert result.next_update_date == date(2020, 4, 1)


def test_no_last_update_before_the_first_month_turn():
    """Na primeira virada ainda por vir, não há atualização passada; a partida que acaba antes não tem próxima."""
    result = get_next_update(
        _simulation(date(2020, 1, 20), date(2020, 1, 6), date(2020, 1, 31))
    )
    assert result.last_update_date is None
    assert result.next_update_date is None
