"""
Os avisos que dependem do caixa e do dia: a cotação da boleta de renda fixa, a vida
financeira e as pendências do jogador.

O caixa mexe várias vezes numa mesma operação (a compra, a taxa, o aporte do dia): cada
movimento só marca a conta, e a publicação sai uma vez, ao fechar a operação mais externa,
com o caixa já final. O pregão marca todas as contas.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import HTTPException

from backend.core.dto.fixed_income_projection import FixedIncomeQuoteDTO
from backend.core.dto.user import UserDTO
from backend.core.exceptions.http_exceptions import NotFoundError
from backend.features.realtime.client_requests import ClientRequests
from backend.features.realtime.schemas import (
    FixedIncomeProjectionEventDTO,
    LifeStatusUpdateEventDTO,
    PendingUpdateEventDTO,
)
from backend.features.simulation.feed_support import guarded, publish_each

if TYPE_CHECKING:
    from backend.features.simulation.simulation import Simulation

# A conta que o caixa mexeu: quem a recebe no tempo real e a gestora dona (nula na pessoal)
type MovedAccount = tuple[UUID, int | None]


@dataclass
class WatchedProjection:
    """O último valor que o cliente digitou na boleta do título e a conta em que a boleta está."""

    requester: UUID
    account: int | None
    amount: Decimal


class CashFeed:
    """Os avisos do caixa de uma partida; todos os métodos rodam com o lock da simulação."""

    def __init__(self, simulation: Simulation):
        self._simulation = simulation
        self._projections = ClientRequests[WatchedProjection]("fixed_income_projection")
        # Títulos com cotação registrada: a publicação só olha para eles
        self._projected: set[str] = set()
        self._moved: set[MovedAccount] = set()
        self._day = False

    def cash_moved(self, audience: Iterable[UUID], account: int | None) -> None:
        """O caixa da conta `account` mexeu; quem a opera recebe o dado novo ao fechar a operação."""
        self._moved.update((recipient, account) for recipient in audience)

    def day_passed(self) -> None:
        """O pregão mudou a data de todas as telas que dependem dela."""
        self._day = True

    # Cotação da boleta

    def watch_projection(
        self,
        requester: UUID,
        account: int | None,
        asset_id: str,
        amount: Decimal,
    ) -> FixedIncomeQuoteDTO:
        """Cota agora, responde e deixa o valor registrado para os próximos avisos."""
        quote = self._quote(requester, account, asset_id, amount)
        self._projections.remember(
            asset_id, requester, WatchedProjection(requester, account, amount)
        )
        self._projected.add(asset_id)
        return quote

    def _quote(
        self, requester: UUID, account: int | None, asset_id: str, amount: Decimal
    ) -> FixedIncomeQuoteDTO:
        simulation = self._simulation
        asset = simulation.get_fixed_asset(asset_id)
        if asset is None:
            raise NotFoundError("Ativo de renda fixa não encontrado")
        acting = simulation.acting_client(requester, account)
        return simulation.quote_fixed_income(acting, asset, amount)

    # Publicação ao fechar a operação

    def flush(self) -> None:
        """Entrega o dado das contas que o caixa mexeu, ou de todas depois do pregão."""
        if not self._moved and not self._day:
            return
        moved, day = self._moved, self._day
        self._moved, self._day = set(), False
        guarded(
            lambda: self._publish_projections(moved, day), "a cotação da renda fixa"
        )
        guarded(lambda: self._publish_life(moved, day), "a vida financeira")
        guarded(lambda: self._publish_pending(moved, day), "as pendências")

    def _publish_projections(self, moved: set[MovedAccount], day: bool) -> None:
        for asset_id in list(self._projected):
            pending = self._projections.pending(asset_id)
            if not pending:
                self._projected.discard(asset_id)
            for client_id, watched in pending.items():
                if not day and (watched.requester, watched.account) not in moved:
                    continue
                try:
                    quote = self._quote(
                        watched.requester, watched.account, asset_id, watched.amount
                    )
                except HTTPException:
                    continue
                self._projections.send(
                    asset_id,
                    client_id,
                    FixedIncomeProjectionEventDTO(
                        amount=watched.amount, account=watched.account, quote=quote
                    ),
                )

    def _personal(self, moved: set[MovedAccount], day: bool) -> set[UUID] | None:
        """Os clientes cujo caixa pessoal mexeu; nulo depois do pregão, que vale para todos."""
        if day:
            return None
        return {client_id for client_id, account in moved if account is None}

    def _publish_life(self, moved: set[MovedAccount], day: bool) -> None:
        simulation = self._simulation

        def build(user: UserDTO) -> list[LifeStatusUpdateEventDTO]:
            status = simulation.get_life_status(user.client_id)
            return [] if status is None else [LifeStatusUpdateEventDTO(status=status)]

        publish_each("life_status_update", build, self._personal(moved, day))

    def _publish_pending(self, moved: set[MovedAccount], day: bool) -> None:
        simulation = self._simulation
        publish_each(
            "pending_update",
            lambda user: [PendingUpdateEventDTO(items=simulation.get_pending(user))],
            self._personal(moved, day),
        )
