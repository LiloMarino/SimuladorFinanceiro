from __future__ import annotations

import logging
import threading
from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from backend.core import repository
from backend.core.dto.events.fixed_income import (
    FixedIncomeEventDTO,
)
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.enum import FixedIncomeEventType
from backend.core.exceptions import InsufficentCashError
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    UnprocessableEntityError,
)
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.user_manager import UserManager
from backend.core.utils import next_business_day
from backend.core.utils.lazy_dict import LazyDict
from backend.features.fixed_income.entities.fixed_income_position import (
    FixedIncomePosition,
)

if TYPE_CHECKING:
    from backend.features.simulation.simulation_engine import SimulationEngine

logger = logging.getLogger(__name__)


def load_fixed_assets(
    simulation_id: int, client_id: UUID, until: date
) -> dict[UUID, FixedIncomePosition]:
    """
    Reconstrói as posições em aberto a partir dos eventos, até o dia `until`.

    Repete a ordem do jogo ao vivo: em cada dia útil, primeiro o rendimento do
    dia (o tick) e depois as compras feitas naquele dia.
    """
    user_id = UserManager.get_user_id(client_id)

    assets: dict[UUID, FixedIncomeAssetDTO] = {}
    buys: dict[UUID, dict[date, list[Decimal]]] = defaultdict(lambda: defaultdict(list))
    redeemed: set[UUID] = set()
    for asset, event in repository.fixed_income.get_events(simulation_id, user_id):
        assets[asset.asset_uuid] = asset
        match event.event_type:
            case FixedIncomeEventType.BUY:
                buys[asset.asset_uuid][event.event_date].append(event.amount)
            case FixedIncomeEventType.REDEEM:
                redeemed.add(asset.asset_uuid)

    positions: dict[UUID, FixedIncomePosition] = {}
    for asset_uuid, buys_by_day in buys.items():
        if asset_uuid in redeemed:
            continue

        position: FixedIncomePosition | None = None
        day = min(buys_by_day)
        while day <= until:
            if position is not None:
                position.accrue(day)
            for amount in buys_by_day.get(day, []):
                if position is None:
                    position = FixedIncomePosition(
                        asset=assets[asset_uuid],
                        total_applied=amount,
                        first_applied_date=day,
                    )
                else:
                    position.invest(amount)
            day = next_business_day(day)

        if position is not None:
            positions[asset_uuid] = position

    return positions


class FixedBroker:
    """
    Gerenciador de operações e posições de renda fixa.

    Responsável por:
    - Executar compras de ativos de renda fixa (buy) com validação de saldo e vencimento
    - Manter posições dos players com cache lazy carregado do banco
    - Aplicar juros diários em todas as posições ativas
    - Processar vencimento de ativos e creditar valores ao player
    - Registrar eventos de renda fixa (BUY, REDEEM)
    """

    def __init__(self, simulation_engine: SimulationEngine, lock: threading.RLock):
        self._simulation_engine = simulation_engine
        self._lock = lock
        self._assets: LazyDict[UUID, dict[UUID, FixedIncomePosition]] = LazyDict(
            lambda client_id: load_fixed_assets(
                simulation_engine.simulation_id,
                client_id,
                simulation_engine.current_date,
            )
        )

    def get_fixed_positions(self, client_id: UUID) -> dict[UUID, FixedIncomePosition]:
        with self._lock:
            return self._assets[client_id]

    def buy(self, client_id: UUID, asset: FixedIncomeAssetDTO, value: Decimal):
        if value <= 0:
            raise UnprocessableEntityError(
                "Valor do investimento deve ser maior que zero"
            )

        if self._simulation_engine.current_date >= asset.maturity_date:
            raise ConflictError(
                f"Ativo {asset.name} já venceu em {asset.maturity_date}"
            )

        with self._lock:
            if self._simulation_engine.get_cash(client_id) < value:
                raise InsufficentCashError(
                    f"Saldo insuficiente para investir em {asset.name}"
                )

            self._simulation_engine.add_cash(client_id, -value)

            positions = self._assets[client_id]
            if asset.asset_uuid in positions:
                positions[asset.asset_uuid].invest(value)
            else:
                positions[asset.asset_uuid] = FixedIncomePosition(
                    asset=asset,
                    total_applied=value,
                    first_applied_date=self._simulation_engine.current_date,
                )

        asset_id = repository.fixed_income.get_or_create_asset(asset)
        EventManager.push_event(
            FixedIncomeEventDTO(
                simulation_id=self._simulation_engine.simulation_id,
                user_id=UserManager.get_user_id(client_id),
                event_type=FixedIncomeEventType.BUY,
                asset_id=asset_id,
                amount=value,
                event_date=self._simulation_engine.current_date,
            )
        )
        logger.info(
            f"Investido {value:.2f} em {asset.name} ({asset.investment_type.value})"
        )

    def apply_daily_interest(self, current_date: date):
        for client_id, assets_by_client in list(self._assets.items()):
            user_id = UserManager.get_user_id(client_id)
            for asset_uuid, position in list(assets_by_client.items()):
                with self._lock:
                    position.accrue(current_date)
                    expired = current_date >= position.redemption_date
                    if expired:
                        del assets_by_client[asset_uuid]

                if expired:
                    self.redeem_position(current_date, client_id, user_id, position)

    def redeem_position(
        self,
        current_date: date,
        client_id: UUID,
        user_id: int,
        position: FixedIncomePosition,
    ) -> None:
        redeem_value = position.net_redemption_value()

        self._simulation_engine.add_cash(client_id, redeem_value)
        asset_id = repository.fixed_income.get_or_create_asset(position.asset)
        simulation_id = self._simulation_engine.simulation_id
        EventManager.push_event(
            FixedIncomeEventDTO(
                simulation_id=simulation_id,
                user_id=user_id,
                event_type=FixedIncomeEventType.REDEEM,
                asset_id=asset_id,
                amount=redeem_value,
                event_date=current_date,
            )
        )
        logger.info(
            f"REDEEM de {redeem_value:.2f} em {position.asset.name} (vencimento)"
        )
