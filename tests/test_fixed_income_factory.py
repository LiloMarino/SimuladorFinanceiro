from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from decimal import Decimal

import pytest

from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.enum import FixedIncomeType, IndicatorSeries, RateIndexType
from backend.features.fixed_income.factory import FixedIncomeFactory
from tests.conftest import SetIndicator
from tests.fakes import daily_series, monthly_series

TODAY = date(2020, 1, 1)
COMBINATIONS = 12  # 4 tipos x 3 indexadores


@pytest.fixture(autouse=True)
def economic_rates(indicators: SetIndicator):
    """Indicadores fixos no lugar da série histórica do banco (≈10%, 11% e 4% a.a.)."""
    indicators(IndicatorSeries.CDI, daily_series(TODAY, TODAY, "0.0378"))
    indicators(IndicatorSeries.SELIC, daily_series(TODAY, TODAY, "0.0414"))
    indicators(IndicatorSeries.IPCA, monthly_series(date(2019, 1, 1), 13, "0.33"))


def _generate(n: int, seed: int = 42) -> list[FixedIncomeAssetDTO]:
    return list(FixedIncomeFactory.generate_assets(TODAY, n=n, seed=seed).values())


def test_same_seed_generates_same_assets():
    """Mesmo seed gera os mesmos títulos (a menos do UUID)."""

    def _fingerprint(assets: list[FixedIncomeAssetDTO]) -> list[dict]:
        return [a.model_dump(exclude={"asset_uuid"}) for a in assets]

    assert _fingerprint(_generate(10)) == _fingerprint(_generate(10))


def test_every_type_and_index_is_balanced():
    """Com N múltiplo das combinações, cada tipo+indexador aparece o mesmo número de vezes."""
    assets = _generate(2 * COMBINATIONS)

    counts = Counter((a.investment_type, a.rate_index) for a in assets)

    assert len(counts) == COMBINATIONS
    assert set(counts.values()) == {2}


def test_maturity_respects_each_issuer_range():
    """Vencimento nunca antecede a geração; Tesouro vence em 3 anos ou mais."""
    for seed in range(20):
        for asset in _generate(COMBINATIONS, seed):
            assert asset.maturity_date >= TODAY
            if asset.investment_type == FixedIncomeType.TESOURO_DIRETO:
                assert asset.maturity_date >= TODAY + timedelta(days=3 * 365)


def test_rates_stay_in_range_and_fit_database_precision():
    """Taxas ficam na faixa do indexador e com até 6 casas, a precisão do banco."""
    for seed in range(20):
        for asset in _generate(COMBINATIONS, seed):
            rate = asset.interest_rate
            assert rate == rate.quantize(Decimal("0.000001"))
            match asset.rate_index:
                case RateIndexType.CDI:
                    # 85% a 120% do CDI, em passos de 0,5 p.p.
                    assert Decimal("0.85") <= rate <= Decimal("1.2")
                    assert rate % Decimal("0.005") == 0
                case RateIndexType.SELIC:
                    assert Decimal("0.0005") <= rate <= Decimal("0.002")
                case RateIndexType.PREFIXADO | RateIndexType.IPCA:
                    assert Decimal(0) < rate < Decimal("0.2")
