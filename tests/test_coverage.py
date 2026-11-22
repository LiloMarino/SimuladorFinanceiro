from __future__ import annotations

from datetime import date

import pytest

from backend.core.dto.series_coverage import SeriesKind
from backend.core.enum import IndicatorSeries
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.indicators import ensure_indicator_coverage
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.import_data.coverage import get_series_coverage
from backend.routes.dependencies.simulation import require_no_active_simulation
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


def test_the_focus_does_not_limit_the_start_of_a_match(indicators):
    """O Focus de SELIC começa em 2004: a partida de 2020 só pede CDI, SELIC e IPCA."""
    _cover_all(indicators, date(2019, 12, 2))
    indicators(
        IndicatorSeries.FOCUS_SELIC,
        daily_series(date(2020, 2, 3), date(2020, 3, 2), "4.5"),
    )

    ensure_indicator_coverage(START)


def test_coverage_says_which_series_get_a_generated_future(indicators, database):
    """O Focus, o PIB e a PTAX não ganham futuro; CDI, o Fed Funds, o IVG-R, o IGP-M e a TR (da economia) ganham."""
    _cover_all(indicators, date(2019, 12, 2))

    gets_future = {s.key: s.has_generated_future for s in get_series_coverage()}

    assert gets_future["CDI"]
    assert gets_future["FED_FUNDS"]
    assert gets_future["IVG_R"]
    assert gets_future["IGP_M"]
    assert gets_future["TR"]
    assert not gets_future["GDP_GROWTH"]
    assert not gets_future["PTAX"]
    assert not gets_future["FOCUS_SELIC"]


def test_housing_series_are_economy_series_with_their_own_provider(
    indicators, database
):
    """O IVG-R, o IGP-M e a TR são da economia e dizem quem publica cada um."""
    by_key = {s.key: s for s in get_series_coverage()}

    assert by_key["IVG_R"].kind is SeriesKind.MACRO
    assert by_key["IGP_M"].provider == "FGV via Banco Central"
    assert by_key["TR"].provider == "Banco Central"


def test_series_that_start_after_the_match_do_not_block_it(indicators):
    """O IVG-R nasce em 2001: uma partida que começa antes disso só pede CDI, SELIC e IPCA."""
    _cover_all(indicators, date(1999, 12, 2))
    indicators(IndicatorSeries.IVG_R, monthly_series(date(2001, 4, 1), 1, "0.3"))

    ensure_indicator_coverage(date(2000, 1, 6))
