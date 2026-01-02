from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from backend.core import repository
from backend.core.dto.events.fixed_income import (
    FixedIncomeEventDTO,
)
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.dto.fixed_income_position import FixedIncomePositionDTO
from backend.core.enum import FixedIncomeEventType
from backend.core.exceptions import FixedIncomeExpiredAssetError
from backend.core.logger import setup_logger
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.user_manager import UserManager
from backend.core.utils.lazy_dict import LazyDict
from backend.features.fixed_income.entities.fixed_income_position import (
    FixedIncomePosition,
)
from backend.features.realtime import notify

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

    def get_fixed_positions(self, client_id: str) -> dict[str, FixedIncomePosition]:
        return self._assets[client_id]

    def buy(self, client_id: str, asset: FixedIncomeAssetDTO, value: float):
        if value <= 0:
            raise ValueError("Valor do investimento deve ser maior que zero")

        if self._simulation_engine.current_date >= asset.maturity_date:
            raise FixedIncomeExpiredAssetError(
                f"Ativo {asset.name} já venceu em {asset.maturity_date}"
            )

        if self._simulation_engine.get_cash(client_id) < value:
            raise ValueError(f"Saldo insuficiente para investir em {asset.name}")

        self._simulation_engine.add_cash(client_id, -value)
        if asset.name in self._assets:
            self._assets[client_id][asset.name].invest(value)
        else:
            self._assets[client_id][asset.name] = FixedIncomePosition(
                asset=asset, total_applied=value
            )
        asset_id = repository.fixed_income.get_or_create_asset(asset)
        EventManager.push_event(
            FixedIncomeEventDTO(
                user_id=UserManager.get_user_id(client_id),
                event_type=FixedIncomeEventType.BUY,
                asset_id=asset_id,
                amount=Decimal(value),
                event_date=self._simulation_engine.current_date,
            )
        )
        logger.info(
            f"Investido {value:.2f} em {asset.name} ({asset.investment_type.value})"
        )

    def apply_daily_interest(self, current_date: date):
        for client_id, assets_by_client in list(self._assets.items()):
            user_id = UserManager.get_user_id(client_id)
            updates: list[FixedIncomePositionDTO] = []
            has_expired = False
            for asset_name, position in list(assets_by_client.items()):
                position.apply_daily_interest(current_date)
                if current_date >= position.asset.maturity_date:
                    self.redeem_position(
                        current_date,
                        client_id,
                        user_id,
                        asset_name,
                        position,
                    )
                    del assets_by_client[asset_name]
                    has_expired = True
                    continue

                updates.append(
                    FixedIncomePositionDTO(
                        asset=position.asset,
                        total_applied=position.total_applied,
                        current_value=position.current_value,
                    )
                )

            if updates or has_expired:
                notify(
                    "fixed_income_position_update",
                    {"positions": [update.to_json() for update in updates]},
                    client_id,
                )

    def redeem_position(
        self,
        current_date: date,
        client_id: str,
        user_id: int,
        asset_name: str,
        position: FixedIncomePosition,
    ) -> None:
        redeem_value = position.current_value

        self._simulation_engine.add_cash(client_id, redeem_value)
        asset_id = repository.fixed_income.get_or_create_asset(position.asset)
        EventManager.push_event(
            FixedIncomeEventDTO(
                user_id=user_id,
                event_type=FixedIncomeEventType.REDEEM,
                asset_id=asset_id,
                amount=Decimal(redeem_value),
                event_date=current_date,
            )
        )
        repository.fixed_income.delete_position(user_id=user_id, asset_id=asset_id)
        logger.info(f"REDEEM de {redeem_value:.2f} em {asset_name} (maturity)")
