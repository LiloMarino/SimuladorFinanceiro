from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from backend.core.logger import setup_logger
from backend.features.simulation.entities.fixed_income_asset import FixedIncomeAsset

if TYPE_CHECKING:
    from backend.features.simulation.simulation_engine import SimulationEngine

logger = setup_logger(__name__)


class FixedBroker:
    """Gerencia ativos de renda fixa e cálculo de juros"""

    def __init__(self, simulation_engine: SimulationEngine):
        self._simulation_engine = simulation_engine
        self._assets: dict[str, FixedIncomeAsset] = {}

    def invest(self, asset: FixedIncomeAsset, value: float):
        if value <= 0:
            raise ValueError("Valor do investimento deve ser maior que zero")

        if self._simulation_engine.get_cash() < value:
            raise ValueError(f"Saldo insuficiente para investir em {asset.name}")

        self._simulation_engine.add_cash(-value)

        if asset.name in self._assets:
            self._assets[asset.name].invested_amount += value
        else:
            self._assets[asset.name] = FixedIncomeAsset(
                name=asset.name,
                invested_amount=value,
                interest_rate=asset.interest_rate,
                rate_index=asset.rate_index,
                investment_type=asset.investment_type,
                maturity_date=asset.maturity_date,
            )

        logger.info(
            f"Investido {value:.2f} em {asset.name} ({asset.investment_type.value})"
        )

    def apply_daily_interest(self, current_date: date):
        for asset in self._assets.values():
            asset.apply_daily_interest(current_date)

    def get_assets(self) -> dict[str, FixedIncomeAsset]:
        return self._assets
