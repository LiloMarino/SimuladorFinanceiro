from __future__ import annotations

from datetime import date

import pytest

from backend.core.dependencies.simulation import require_no_active_simulation
from backend.core.enum import IndicatorSeries
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.indicators import ensure_indicator_coverage
from backend.core.runtime.simulation_manager import SimulationManager
from tests.conftest import SetIndicator
from tests.fakes import daily_series, monthly_series

START = date(2020, 1, 6)


def _cover_all(indicators: SetIndicator, since: date) -> None:
    indicators(IndicatorSeries.CDI, daily_series(since, START, "0.04"))
    indicators(IndicatorSeries.SELIC, daily_series(since, START, "0.04"))
    indicators(IndicatorSeries.IPCA, monthly_series(since, 1, "0.3"))


def test_simulation_starts_when_every_index_covers_the_start(indicators):
    """CDI, SELIC e IPCA com dado até o início: a partida pode nascer."""
    _cover_all(indicators, date(2019, 12, 2))

    ensure_indicator_coverage(START)


def test_simulation_is_blocked_before_an_index_starts(indicators):
    """Início antes do primeiro CDI: a partida não nasce e a mensagem nomeia a série."""
    _cover_all(indicators, date(2019, 12, 2))
    indicators(
        IndicatorSeries.CDI, daily_series(date(2020, 2, 3), date(2020, 3, 2), "0.04")
    )

    with pytest.raises(ConflictError, match="CDI"):
        ensure_indicator_coverage(START)


def test_data_center_answers_only_outside_a_match(monkeypatch: pytest.MonkeyPatch):
    """Com partida ativa a Central responde 409; fora dela, segue."""
    require_no_active_simulation()

    monkeypatch.setattr(SimulationManager, "_active_simulation", object())
    with pytest.raises(ConflictError):
        require_no_active_simulation()
