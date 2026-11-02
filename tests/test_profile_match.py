"""O relatório do `profile:match` compara o começo e o fim da partida pela mediana e pelo p95."""

import pytest

from scripts.profile_match import median_ms, p95_ms, report


def test_p95_is_the_value_95_percent_of_days_stay_under() -> None:
    days = [float(n) for n in range(1, 101)]

    assert p95_ms(days) == 95.0
    assert p95_ms([]) == 0.0


def test_median_ignores_the_slow_outlier() -> None:
    assert median_ms([10.0, 11.0, 12.0, 900.0, 10.5]) == 11.0


def test_report_shows_the_growth_ratio_between_the_ends(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Dias que custam 10 ms no começo e 30 ms no fim: a razão é 3,00
    durations = {"Processar um dia": [10.0] * 20 + [30.0] * 20}

    report(durations, "Processar um dia", window=10)

    line = next(
        row for row in capsys.readouterr().out.splitlines() if "Processar" in row
    )
    assert line.split()[-1] == "3.00"
