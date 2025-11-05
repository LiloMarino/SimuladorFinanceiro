# backend/simulation/fixed_income_market.py
from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import List

from backend.simulation.entities.fixed_income_asset import (
    FixedIncomeAsset,
    FixedIncomeType,
    RateIndexType,
)


class FixedIncomeMarket:
    """Gera e mantém o hall de ativos de renda fixa disponíveis."""

    def __init__(self):
        self._current_month = None
        self._available_assets: List[FixedIncomeAsset] = []

    def refresh_assets(self, current_date: datetime):
        """Atualiza a lista de ativos no início de cada mês."""
        if self._current_month == (current_date.year, current_date.month):
            return  # já atualizado

        self._current_month = (current_date.year, current_date.month)
        self._available_assets = self._generate_assets(current_date)

    def get_available_assets(self) -> List[FixedIncomeAsset]:
        """Retorna os ativos disponíveis no hall atual."""
        return self._available_assets

    def _generate_assets(self, current_date: datetime) -> List[FixedIncomeAsset]:
        """Gera ativos randômicos para o mês atual."""
        assets = []
        num_assets = random.randint(3, 6)

        for i in range(num_assets):
            investment_type = random.choice(list(FixedIncomeType))
            rate_index = random.choice(list(RateIndexType))
            rate = self._random_rate_for_index(rate_index)
            maturity = current_date + timedelta(days=random.randint(180, 1080))

            asset = FixedIncomeAsset(
                name=f"{investment_type.value}-{rate_index.value}-{i}",
                invested_amount=0.0,
                interest_rate=rate if rate_index == RateIndexType.PREFIXADO else None,
                rate_index=rate_index,
                investment_type=investment_type,
                maturity_date=maturity,
            )
            assets.append(asset)
        return assets

    @staticmethod
    def _random_rate_for_index(rate_index: RateIndexType) -> float:
        if rate_index == RateIndexType.PREFIXADO:
            return random.uniform(0.08, 0.15)  # 8% a 15% a.a.
        return 0.0  # pós-fixado não usa taxa fixa
