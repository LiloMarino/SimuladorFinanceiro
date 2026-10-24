from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core.dto.simulation import SimulationResultDTO
from backend.core.exceptions.http_exceptions import ConflictError, NotFoundError
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.simulation import saved_simulation
from backend.features.simulation.saved_simulation import is_finished
from backend.routes import simulation as simulation_routes
from backend.routes.simulation import (
    UpdateSettingsRequest,
    delete_simulation,
    price_impact_preview,
    update_simulation_settings,
)

END = date(2023, 3, 31)  # sexta-feira


@pytest.mark.parametrize(
    ("resume_from", "expected"),
    [
        (None, False),  # nunca simulou: pausada no começo
        (date(2023, 3, 14), False),  # parou no meio
        (date(2023, 3, 30), False),  # ainda falta o último pregão
        (END, True),  # simulou o último pregão
    ],
)
def test_is_finished_when_next_trading_day_passes_end_date(
    resume_from: date | None, expected: bool
) -> None:
    assert is_finished(END, resume_from) is expected


def test_price_impact_preview_matches_example_and_returns_to_history() -> None:
    preview = price_impact_preview(k=0.02, decay_days=20)

    # Comprar 10% do volume médio com k = 0,02 sobe o preço ~0,63%
    assert preview.volume_share == pytest.approx(0.10)
    assert preview.first_day_impact == pytest.approx(0.0063246, rel=1e-4)
    assert preview.curve[0].impact == pytest.approx(preview.first_day_impact)
    # O efeito some em T pregões
    assert len(preview.curve) == 21
    assert preview.curve[-1].impact == 0


def _settings_payload() -> UpdateSettingsRequest:
    return UpdateSettingsRequest(
        name="Teste",
        start_date=date(2023, 1, 2),
        end_date=END,
        starting_cash=Decimal(10000),
        goal_net_worth=Decimal(100000),
        price_impact_k=0.02,
        price_impact_decay_days=20,
    )


def test_settings_update_is_refused_while_a_saved_simulation_is_selected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(SettingsManager, "_selected_simulation_id", 7)
    monkeypatch.setattr(SettingsManager, "_settings", None)

    with pytest.raises(ConflictError):
        update_simulation_settings(_settings_payload(), None)  # type: ignore[arg-type]

    assert SettingsManager._settings is None  # type: ignore[reportPrivateUsage]


@pytest.mark.usefixtures("database")
def test_settings_update_is_accepted_without_a_selection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(SettingsManager, "_selected_simulation_id", None)
    monkeypatch.setattr(SettingsManager, "_settings", None)
    monkeypatch.setattr(simulation_routes, "notify", lambda *_args, **_kwargs: None)

    settings = update_simulation_settings(_settings_payload(), None)  # type: ignore[arg-type]

    assert settings.name == "Teste"


@pytest.fixture
def deleted(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    """Os ids que o repositório apagou; só a partida 5 existe."""
    ids: list[int] = []

    def delete(simulation_id: int) -> bool:
        ids.append(simulation_id)
        return simulation_id == 5

    monkeypatch.setattr(simulation_routes.repository.simulation, "delete", delete)
    monkeypatch.setattr(SimulationManager, "_active_simulation", None)
    monkeypatch.setattr(SimulationManager, "_simulation_id", None)
    monkeypatch.setattr(SettingsManager, "_selected_simulation_id", None)
    return ids


def test_delete_removes_the_match_and_notifies_the_room(
    monkeypatch: pytest.MonkeyPatch, deleted: list[int]
) -> None:
    sent: list[tuple[str, dict]] = []
    monkeypatch.setattr(
        simulation_routes,
        "notify",
        lambda event, payload: sent.append((event, payload)),
    )

    delete_simulation(5, None)

    assert deleted == [5]
    assert sent == [("simulation_deleted", {"simulation_id": 5})]


def test_delete_is_refused_for_the_selected_match(
    monkeypatch: pytest.MonkeyPatch, deleted: list[int]
) -> None:
    monkeypatch.setattr(SettingsManager, "_selected_simulation_id", 5)

    with pytest.raises(ConflictError):
        delete_simulation(5, None)

    assert deleted == []


def test_delete_is_refused_for_the_active_match(
    monkeypatch: pytest.MonkeyPatch, deleted: list[int]
) -> None:
    monkeypatch.setattr(SimulationManager, "_active_simulation", object())
    monkeypatch.setattr(SimulationManager, "_simulation_id", 5)

    with pytest.raises(ConflictError):
        delete_simulation(5, None)

    assert deleted == []


def test_delete_is_accepted_for_a_saved_match_while_another_is_active(
    monkeypatch: pytest.MonkeyPatch, deleted: list[int]
) -> None:
    monkeypatch.setattr(SimulationManager, "_active_simulation", object())
    monkeypatch.setattr(SimulationManager, "_simulation_id", 9)
    monkeypatch.setattr(simulation_routes, "notify", lambda *_args, **_kwargs: None)

    delete_simulation(5, None)

    assert deleted == [5]


def test_delete_of_a_missing_match_is_not_found(
    monkeypatch: pytest.MonkeyPatch, deleted: list[int]
) -> None:
    monkeypatch.setattr(simulation_routes, "notify", lambda *_args, **_kwargs: None)

    with pytest.raises(NotFoundError):
        delete_simulation(404, None)


class _StoredResults:
    """O repositório de resultados guardados, em memória, contando os recálculos."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.rows: dict[int, tuple[date | None, SimulationResultDTO]] = {}
        self.computed = 0
        repo = saved_simulation.repository.simulation
        monkeypatch.setattr(repo, "get_result", self.rows.get)
        monkeypatch.setattr(
            repo,
            "save_result",
            lambda simulation_id, as_of, result: self.rows.__setitem__(
                simulation_id, (as_of, result)
            ),
        )
        monkeypatch.setattr(saved_simulation, "compute_result", self._compute)
        monkeypatch.setattr(SimulationManager, "_simulation_id", None)

    def _compute(self, _simulation_id: int) -> SimulationResultDTO:
        self.computed += 1
        return SimulationResultDTO(
            leader_reached_goal=False,
            players_count=2,
            leader_name="ana",
            positions={"ana": 1, "bia": 2},
        )


def test_saved_result_is_computed_once_while_the_simulation_does_not_advance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stored = _StoredResults(monkeypatch)
    day = date(2023, 3, 14)

    saved_simulation.saved_result(3, day)
    result = saved_simulation.saved_result(3, day)

    assert stored.computed == 1
    assert result.positions == {"ana": 1, "bia": 2}


def test_saved_result_is_recomputed_when_the_simulation_advances(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stored = _StoredResults(monkeypatch)

    saved_simulation.saved_result(3, date(2023, 3, 14))
    saved_simulation.saved_result(3, date(2023, 3, 15))

    assert stored.computed == 2
    assert stored.rows[3][0] == date(2023, 3, 15)


def test_saved_result_of_the_running_simulation_is_not_stored(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stored = _StoredResults(monkeypatch)
    monkeypatch.setattr(SimulationManager, "_simulation_id", 3)

    saved_simulation.saved_result(3, date(2023, 3, 14))

    assert stored.rows == {}
