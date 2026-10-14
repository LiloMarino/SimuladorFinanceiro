from __future__ import annotations

from datetime import date

import pytest

from backend.features.simulation.saved_simulation import is_finished
from backend.routes.simulation import price_impact_preview

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
