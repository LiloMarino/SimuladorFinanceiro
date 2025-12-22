from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from backend.core import repository
from backend.core.dto.events.fixed_income import (
    FixedIncomeEventDTO,
    FixedIncomeEventType,
)
from backend.core.logger import setup_logger
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.user_manager import UserManager
from backend.core.utils.lazy_dict import LazyDict
from backend.features.simulation.entities.fixed_income_position import (
    FixedIncomePosition,
)

if TYPE_CHECKING:
    from backend.features.simulation.simulation_engine import SimulationEngine

logger = setup_logger(__name__)


def load_fixed_assets(client_id: str) -> dict[str, FixedIncomePosition]:
    user_id = UserManager.get_user_id(client_id)

    dtos = repository.portfolio.get_fixed_income_positions(user_id)

    assets: dict[str, FixedIncomePosition] = {}

    for dto in dtos:
        assets[dto.asset.name] = FixedIncomePosition(
            asset=dto.asset,
            total_applied=dto.total_applied,
        )

    return assets


class FixedBroker:
    """Gerencia ativos de renda fixa e cálculo de juros"""

    def __init__(self, simulation_engine: SimulationEngine):
        self._simulation_engine = simulation_engine
        self._assets: LazyDict[str, dict[str, FixedIncomePosition]] = LazyDict(
            load_fixed_assets
        )

    def get_assets(self, client_id: str) -> dict[str, FixedIncomePosition]:
        return self._assets[client_id]

    def buy(self, client_id: str, asset_uuid: str, value: float):
        if value <= 0:
            raise ValueError("Valor do investimento deve ser maior que zero")

        asset = self._simulation_engine.fixed_income_market.get_asset(asset_uuid)
        if asset is None:
            raise ValueError(f"Asset {asset_uuid} not found")

        if self._simulation_engine.get_cash(client_id) < value:
            raise ValueError(f"Saldo insuficiente para investir em {asset.name}")

        self._simulation_engine.add_cash(client_id, -value)
        if asset.name in self._assets:
            self._assets[client_id][asset.name].invest(value)
        else:
            self._assets[client_id][asset.name] = FixedIncomePosition(
                asset=asset, total_applied=value
            )
        db_asset = repository.fixed_income.get_or_create_asset(asset)
        EventManager.push_event(
            FixedIncomeEventDTO(
                user_id=UserManager.get_user_id(client_id),
                event_type=FixedIncomeEventType.BUY,
                asset_id=db_asset.id,
                amount=Decimal(value),
                event_date=self._simulation_engine.current_date.date(),
            )
        )
        logger.info(
            f"Investido {value:.2f} em {asset.name} ({asset.investment_type.value})"
        )

    def apply_daily_interest(self, current_date: date):
        for assets_by_client in self._assets.values():
            for position in assets_by_client.values():
                position.apply_daily_interest(current_date)
