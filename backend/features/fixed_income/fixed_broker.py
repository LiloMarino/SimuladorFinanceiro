from __future__ import annotations

import logging
import threading
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_EVEN, Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from backend.core import repository
from backend.core.dto.events.fixed_income import (
    FixedIncomeEventDTO,
)
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.enum import FixedIncomeEventType, FixedIncomeType
from backend.core.exceptions import InsufficentCashError
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.user_manager import UserManager
from backend.core.utils import format_money, next_business_day
from backend.core.utils.lazy_dict import LazyDict
from backend.features.fixed_income.accrual import RedemptionBreakdown
from backend.features.fixed_income.entities.fixed_income_position import (
    FixedIncomePosition,
)
from backend.features.fixed_income.liquidity import cover_order, redeemable_today
from backend.features.fixed_income.quotes import FixedIncomeQuotes
from backend.features.tax_policy import TaxPolicy

if TYPE_CHECKING:
    from backend.features.simulation.simulation_engine import SimulationEngine

logger = logging.getLogger(__name__)

CENT = Decimal("0.01")
# O saldo em US$ vai ao evento com a precisão da coluna: o centavo de dólar vale mais de R$ 0,02
MICRO_DOLLAR = Decimal("0.000001")


def _event_amount(position: FixedIncomePosition, units: Decimal) -> Decimal:
    """O `amount` do resgate: reais em centavos, ou US$ com a precisão da coluna na conta em dólar."""
    return units.quantize(
        MICRO_DOLLAR if position.marked_by_dollar else CENT, ROUND_HALF_EVEN
    )


def _withheld(breakdown: RedemptionBreakdown) -> Decimal:
    """O que o resgate retém em IR e IOF: o bruto menos o líquido que vai ao caixa."""
    return (breakdown.gross - breakdown.net).quantize(CENT, ROUND_HALF_EVEN)


@dataclass(frozen=True)
class CoverSale:
    """Um título vendido pela cobertura automática e o líquido que ele mandou ao caixa."""

    asset: FixedIncomeAssetDTO
    net: Decimal


def load_fixed_assets(
    simulation_id: int, client_id: UUID, until: date
) -> dict[UUID, FixedIncomePosition]:
    """
    Reconstrói as posições em aberto a partir dos eventos, até o dia `until`.

    Repete a ordem do jogo ao vivo: em cada dia útil, primeiro o rendimento do
    dia (o tick) e depois as compras e os resgates daquele dia, na ordem em que
    aconteceram. O `amount` do resgate é o que saiu do título; um resgate em ou
    depois do vencimento fecha a posição inteira, como o vencimento ao vivo. Na conta
    em dólar o `amount` da compra é em reais e o do resgate, em US$, cada um com o dólar
    do dia no `fx_rate`; o IOF do câmbio é o da política padrão, que nenhuma medida muda.
    """
    user_id = UserManager.get_user_id(client_id)

    assets: dict[UUID, FixedIncomeAssetDTO] = {}
    trades: dict[
        UUID, dict[date, list[tuple[FixedIncomeEventType, Decimal, Decimal | None]]]
    ] = defaultdict(lambda: defaultdict(list))
    for asset, event in repository.fixed_income.get_events(simulation_id, user_id):
        assets[asset.asset_uuid] = asset
        trades[asset.asset_uuid][event.event_date].append(
            (event.event_type, event.amount, event.fx_rate)
        )

    positions: dict[UUID, FixedIncomePosition] = {}
    for asset_uuid, trades_by_day in trades.items():
        position: FixedIncomePosition | None = None
        day = min(trades_by_day)
        while day <= until:
            if position is not None:
                position.accrue(day)
            for event_type, amount, fx_rate in trades_by_day.get(day, []):
                if event_type is FixedIncomeEventType.BUY:
                    # A compra na conta em dólar guarda o dólar do dia em que entrou
                    quotes = FixedIncomeQuotes(dollar=fx_rate or Decimal(1))
                    if position is None:
                        position = FixedIncomePosition.open(
                            assets[asset_uuid], amount, day, quotes
                        )
                    else:
                        position.invest(amount, quotes)
                elif position is not None:
                    if day >= position.redemption_date:
                        position = None
                    else:
                        position.withdraw(amount)
                        if position.current_value.quantize(CENT, ROUND_HALF_EVEN) <= 0:
                            position = None
            day = next_business_day(day)

        if position is not None:
            positions[asset_uuid] = position

    return positions


class FixedBroker:
    """
    Gerenciador de operações e posições de renda fixa.

    Responsável por:
    - Executar compras de ativos de renda fixa (buy) com validação de saldo, vencimento e teto
    - Resgatar títulos de liquidez diária em qualquer pregão (redeem)
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

        with self._lock:
            today = self._simulation_engine.current_date
            if today >= asset.maturity_date:
                raise ConflictError(
                    f"Ativo {asset.name} já venceu em {asset.maturity_date}"
                )
            if asset.offered_until is not None and today > asset.offered_until:
                left_on = asset.offered_until + timedelta(days=1)
                raise ConflictError(f"A oferta saiu do catálogo em {left_on:%d/%m/%Y}")

            positions = self._assets[client_id]
            if asset.player_cap is not None:
                applied = (
                    positions[asset.asset_uuid].total_applied
                    if asset.asset_uuid in positions
                    else Decimal(0)
                )
                room = max(asset.player_cap - applied, Decimal(0))
                if value > room:
                    raise UnprocessableEntityError(
                        f"Seu teto nesta oferta é {format_money(asset.player_cap)} "
                        f"e você já aplicou {format_money(applied)}: "
                        f"cabem mais {format_money(room)}."
                    )
            if self._simulation_engine.get_cash(client_id) < value:
                raise InsufficentCashError(
                    f"Saldo insuficiente para investir em {asset.name}"
                )

            self._simulation_engine.add_cash(client_id, -value)

            quotes = self._simulation_engine.fixed_quotes()
            policy = self._simulation_engine.tax_policy_on(today)
            if asset.asset_uuid in positions:
                positions[asset.asset_uuid].invest(value, quotes, policy)
            else:
                positions[asset.asset_uuid] = FixedIncomePosition.open(
                    asset, value, today, quotes, policy
                )
            marked_by_dollar = positions[asset.asset_uuid].marked_by_dollar

        asset_id = repository.fixed_income.get_or_create_asset(
            self._simulation_engine.simulation_id, asset
        )
        EventManager.push_event(
            FixedIncomeEventDTO(
                simulation_id=self._simulation_engine.simulation_id,
                user_id=UserManager.get_user_id(client_id),
                event_type=FixedIncomeEventType.BUY,
                asset_id=asset_id,
                amount=value,
                fx_rate=quotes.dollar if marked_by_dollar else None,
                event_date=today,
            )
        )
        logger.debug(
            "Investido %.2f em %s (%s)", value, asset.name, asset.investment_type.value
        )

    def redeem(self, client_id: UUID, asset: FixedIncomeAssetDTO, net_wanted: Decimal):
        """
        Resgata de um título de liquidez diária o que o jogador quer receber no
        caixa (`net_wanted`, líquido de IOF e IR). O título entrega esse valor
        mais os impostos; pedir o líquido máximo resgata a posição inteira.
        """
        if not asset.daily_liquidity:
            raise ConflictError(f"{asset.name} só é resgatado no vencimento")

        net_wanted = net_wanted.quantize(CENT, ROUND_HALF_EVEN)
        if net_wanted <= 0:
            raise UnprocessableEntityError("Valor do resgate deve ser maior que zero")

        with self._lock:
            today = self._simulation_engine.current_date
            positions = self._assets[client_id]
            position = positions.get(asset.asset_uuid)
            if position is None:
                raise NotFoundError(f"Você não tem posição em {asset.name}")

            policy = self._simulation_engine.tax_policy_on(today)
            quotes = self._simulation_engine.fixed_quotes()
            maximum = position.breakdown(today, None, policy, quotes).net
            if net_wanted > maximum:
                raise UnprocessableEntityError(
                    f"Você pode resgatar até {format_money(maximum)} hoje."
                )

            breakdown = position.breakdown(today, net_wanted, policy, quotes)
            # O título perde o bruto na unidade do montante: reais, ou US$ na conta em dólar
            units = position.units_for(breakdown.gross, quotes)
            fx_rate = quotes.dollar if position.marked_by_dollar else None
            if breakdown.full:
                del positions[asset.asset_uuid]
            else:
                position.withdraw(units)
            self._simulation_engine.add_cash(client_id, breakdown.net)

        asset_id = repository.fixed_income.get_or_create_asset(
            self._simulation_engine.simulation_id, asset
        )
        EventManager.push_event(
            FixedIncomeEventDTO(
                simulation_id=self._simulation_engine.simulation_id,
                user_id=UserManager.get_user_id(client_id),
                event_type=FixedIncomeEventType.REDEEM,
                asset_id=asset_id,
                amount=_event_amount(position, units),
                tax_withheld=_withheld(breakdown),
                fx_rate=fx_rate,
                event_date=today,
            )
        )
        logger.debug(
            "Resgatado %.2f de %s (liquidez diária)", breakdown.net, asset.name
        )

    def sell_treasury(
        self, client_id: UUID, asset: FixedIncomeAssetDTO, gross: Decimal | None
    ) -> Decimal:
        """
        Vende um título do Tesouro a mercado, em qualquer pregão. `gross` é o valor
        bruto vendido (None vende tudo); o caixa recebe esse valor menos os impostos.
        O evento guarda o equivalente na curva, a fração vendida do montante, e é isso
        que a reconstrução tira do título. Devolve o líquido creditado.
        """
        if asset.investment_type is not FixedIncomeType.TESOURO_DIRETO:
            raise ConflictError(f"{asset.name} não é um título do Tesouro")
        if gross is not None:
            gross = gross.quantize(CENT, ROUND_HALF_EVEN)
            if gross <= 0:
                raise UnprocessableEntityError("Valor da venda deve ser maior que zero")

        with self._lock:
            today = self._simulation_engine.current_date
            positions = self._assets[client_id]
            position = positions.get(asset.asset_uuid)
            if position is None:
                raise NotFoundError(f"Você não tem posição em {asset.name}")

            quotes = self._simulation_engine.fixed_quotes()
            policy = self._simulation_engine.tax_policy_on(today)
            market = position.market_value(today, quotes)
            if gross is not None and gross - market >= CENT:
                raise UnprocessableEntityError(
                    f"Você pode vender até {format_money(market)} hoje."
                )
            # Sobrar menos de um centavo é vender tudo
            if gross is not None and market - gross < CENT:
                gross = None

            breakdown = position.sell_breakdown(today, gross, quotes, policy)
            curve_amount = (breakdown.gross / market * position.current_value).quantize(
                CENT, ROUND_HALF_EVEN
            )
            if breakdown.full:
                del positions[asset.asset_uuid]
            else:
                position.withdraw(curve_amount)
            self._simulation_engine.add_cash(client_id, breakdown.net)

        asset_id = repository.fixed_income.get_or_create_asset(
            self._simulation_engine.simulation_id, asset
        )
        EventManager.push_event(
            FixedIncomeEventDTO(
                simulation_id=self._simulation_engine.simulation_id,
                user_id=UserManager.get_user_id(client_id),
                event_type=FixedIncomeEventType.REDEEM,
                asset_id=asset_id,
                amount=curve_amount,
                tax_withheld=_withheld(breakdown),
                event_date=today,
            )
        )
        logger.debug("Vendido %.2f de %s (a mercado)", breakdown.net, asset.name)
        return breakdown.net

    def sell_for_cash(
        self, client_id: UUID, shortfall: Decimal, include_marked: bool
    ) -> list[CoverSale]:
        """
        Vende títulos, na ordem de `cover_order`, até o caixa receber `shortfall`
        líquido; sem o bastante, vende o que dá. Ação do sistema: não passa pela
        trava de operação do jogador.
        """
        today = self._simulation_engine.current_date
        quotes = self._simulation_engine.fixed_quotes()
        policy = self._simulation_engine.tax_policy_on(today)
        with self._lock:
            order = cover_order(
                self._assets[client_id].values(), today, include_marked, quotes
            )

        sales: list[CoverSale] = []
        remaining = shortfall
        for position in order:
            if remaining <= 0:
                break
            asset = position.asset
            full_net = redeemable_today(position, today, policy, quotes)
            if full_net is None or full_net <= 0:
                continue
            try:
                if asset.investment_type is FixedIncomeType.TESOURO_DIRETO:
                    gross = (
                        None
                        if remaining >= full_net
                        else self._gross_for_net(
                            position, remaining, full_net, today, quotes, policy
                        )
                    )
                    net = self.sell_treasury(client_id, asset, gross)
                else:
                    net = min(remaining, full_net)
                    self.redeem(client_id, asset, net)
            except (NotFoundError, UnprocessableEntityError):
                # A posição mudou entre a ordem e a venda; segue para o próximo título
                continue
            sales.append(CoverSale(asset, net))
            remaining -= net
        return sales

    @staticmethod
    def _gross_for_net(
        position: FixedIncomePosition,
        net: Decimal,
        full_net: Decimal,
        today: date,
        quotes: FixedIncomeQuotes,
        policy: TaxPolicy,
    ) -> Decimal:
        """O bruto a vender para o caixa receber `net`: a fração do mercado, ajustada ao centavo dos impostos."""
        gross = (position.market_value(today, quotes) * net / full_net).quantize(
            CENT, ROUND_HALF_EVEN
        )
        for _ in range(3):
            received = position.sell_breakdown(today, gross, quotes, policy).net
            if received >= net:
                break
            gross += net - received
        return gross

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
        quotes = self._simulation_engine.fixed_quotes()
        breakdown = position.breakdown(
            position.redemption_date,
            None,
            self._simulation_engine.tax_policy_on(position.redemption_date),
            quotes,
        )

        self._simulation_engine.add_cash(client_id, breakdown.net)
        asset_id = repository.fixed_income.get_or_create_asset(
            self._simulation_engine.simulation_id, position.asset
        )
        simulation_id = self._simulation_engine.simulation_id
        EventManager.push_event(
            FixedIncomeEventDTO(
                simulation_id=simulation_id,
                user_id=user_id,
                event_type=FixedIncomeEventType.REDEEM,
                asset_id=asset_id,
                amount=_event_amount(
                    position, position.units_for(breakdown.gross, quotes)
                ),
                tax_withheld=_withheld(breakdown),
                fx_rate=quotes.dollar if position.marked_by_dollar else None,
                event_date=current_date,
            )
        )
        logger.debug(
            "Resgate de %.2f em %s (vencimento)", breakdown.net, position.asset.name
        )
