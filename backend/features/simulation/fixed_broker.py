from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from backend.core.logger import setup_logger
from backend.core.runtime.user_manager import UserManager
from backend.core.utils.lazy_dict import LazyDict
from backend.features.simulation.entities.fixed_income_asset import FixedIncomeAsset

if TYPE_CHECKING:
    from backend.features.simulation.simulation_engine import SimulationEngine

logger = setup_logger(__name__)


def load_fixed_assets(client_id: str) -> dict[str, FixedIncomeAsset]:
    user_id = UserManager.get_user_id(client_id)


class FixedBroker:
    """Gerencia ativos de renda fixa e cálculo de juros"""

    def __init__(self, simulation_engine: SimulationEngine):
        self._simulation_engine = simulation_engine
        self._assets: LazyDict[str, dict[str, FixedIncomeAsset]] = LazyDict(
            load_fixed_assets
        )

    def buy(self, client_id: str, asset: FixedIncomeAsset, value: float):
        if value <= 0:
            raise ValueError("Valor do investimento deve ser maior que zero")

        if self._simulation_engine.get_cash(client_id) < value:
            raise ValueError(f"Saldo insuficiente para investir em {asset.name}")

        self._simulation_engine.add_cash(client_id, -value)

        if asset.name in self._assets:
            self._assets[asset.name].invested_amount += value
        else:
            self._assets[asset.name] = FixedIncomeAsset(
                name=asset.name,
                issuer=asset.issuer,
                interest_rate=asset.interest_rate,
                rate_index=asset.rate_index,
                investment_type=asset.investment_type,
                maturity_date=asset.maturity_date,
                uuid=asset.uuid,
            )

        logger.info(
            f"Investido {value:.2f} em {asset.name} ({asset.investment_type.value})"
        )

    def apply_daily_interest(self, current_date: date):
        for asset in self._assets.values():
            asset.apply_daily_interest(current_date)

    def get_assets(self) -> dict[str, FixedIncomeAsset]:
        return self._assets
