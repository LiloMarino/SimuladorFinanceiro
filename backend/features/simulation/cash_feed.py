"""
Os avisos que dependem do caixa, do crédito e do dia: a cotação da boleta de renda fixa, a
vida financeira, as pendências e o panorama do crédito do jogador.

O caixa e o crédito mexem várias vezes numa mesma operação (a compra, a taxa, o aporte do
dia, a parcela): cada mudança só marca a conta, e a publicação sai uma vez, ao fechar a
operação mais externa, com o estado já final. O pregão marca todas as contas.

O caixa de uma conta de gestora mexe nas pendências de quem a opera; a vida financeira é
só da conta pessoal. O dinheiro que o governo e a eleição mexem na conta pessoal (contribuição
e doação à campanha, legado do presidente) leva também a carteira nova ao dono dela. O crédito é de quem vê a conta: o dono da pessoal e o gestor principal
da gestora.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import HTTPException

from backend.core.dto.base import BaseDTO
from backend.core.dto.fixed_income_projection import FixedIncomeQuoteDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import CashflowEventType
from backend.core.exceptions.http_exceptions import NotFoundError
from backend.features.credit.overview import build_overview
from backend.features.realtime.client_requests import ClientRequests
from backend.features.realtime.schemas import (
    CreditUpdateEventDTO,
    FixedIncomeProjectionEventDTO,
    LifeStatusUpdateEventDTO,
    PendingUpdateEventDTO,
    PortfolioUpdateEventDTO,
)
from backend.features.simulation.feed_support import (
    guarded,
    operated_accounts,
    publish_each,
)

if TYPE_CHECKING:
    from backend.features.simulation.simulation import Simulation

# Os lançamentos do governo e da eleição que mexem na carteira de quem os paga ou recebe
POLITICAL_CASH = frozenset(
    {
        CashflowEventType.CAMPAIGN_CONTRIBUTION,
        CashflowEventType.CAMPAIGN_DONATION,
        CashflowEventType.PRESIDENT_LEGACY,
    }
)

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
        # Os clientes cuja carteira pessoal o governo mexeu
        self._portfolio: set[UUID] = set()
        # As contas de crédito (client_id) que mudaram e os clientes cuja lista de pendências mudou
        self._credit: set[UUID] = set()
        self._pending: set[UUID] = set()
        self._day = False

    def credit_changed(self, client_id: UUID) -> None:
        """O crédito da conta `client_id` mudou; o panorama novo sai ao fechar a operação em curso."""
        self._credit.add(client_id)

    def pending_changed(self, recipients: Iterable[UUID]) -> None:
        """A lista de pendências de `recipients` mudou por algo que não é o caixa."""
        self._pending.update(recipients)

    def cash_moved(
        self,
        audience: Iterable[UUID],
        account: int | None,
        event_type: CashflowEventType | None = None,
    ) -> None:
        """O caixa da conta `account` mexeu; quem a opera recebe o dado novo ao fechar a operação."""
        recipients = tuple(audience)
        self._moved.update((recipient, account) for recipient in recipients)
        if account is None and event_type in POLITICAL_CASH:
            self._portfolio.update(recipients)

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
        acting = simulation.acting_client(requester, account)
        asset = simulation.get_fixed_asset(acting, asset_id)
        if asset is None:
            raise NotFoundError("Ativo de renda fixa não encontrado")
        return simulation.quote_fixed_income(acting, asset, amount)

    # Publicação ao fechar a operação

    def flush(self) -> None:
        """Entrega o dado das contas que o caixa mexeu, ou de todas depois do pregão."""
        if not (self._moved or self._day or self._credit or self._pending):
            return
        moved, day = self._moved, self._day
        credit, pending, portfolio = self._credit, self._pending, self._portfolio
        self._moved, self._day = set(), False
        self._credit, self._pending, self._portfolio = set(), set(), set()
        guarded(
            lambda: self._publish_projections(moved, day), "a cotação da renda fixa"
        )
        guarded(lambda: self._publish_life(moved, day), "a vida financeira")
        guarded(lambda: self._publish_pending(moved, day, pending), "as pendências")
        guarded(lambda: self._publish_credit(credit, day), "o crédito")
        # O pregão já leva a carteira a todos os jogadores
        if not day:
            guarded(lambda: self._publish_portfolio(portfolio), "a carteira")

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

    def _publish_pending(
        self, moved: set[MovedAccount], day: bool, pending: set[UUID]
    ) -> None:
        simulation = self._simulation
        # O caixa de qualquer conta, a da gestora também, mexe nas pendências de quem a opera
        recipients = None if day else {client_id for client_id, _ in moved} | pending
        publish_each(
            "pending_update",
            lambda user: [PendingUpdateEventDTO(items=simulation.get_pending(user))],
            recipients,
        )

    def _publish_portfolio(self, portfolio: set[UUID]) -> None:
        """A carteira pessoal dos jogadores que o governo mexeu."""
        simulation = self._simulation
        publish_each(
            "portfolio_update",
            lambda user: [
                PortfolioUpdateEventDTO(
                    portfolio=simulation.get_portfolio(user.client_id), account=None
                )
            ],
            portfolio,
        )

    def _publish_credit(self, credit: set[UUID], day: bool) -> None:
        """O panorama das contas de crédito que mudaram e, depois do pregão, o das que têm parcela em atraso (multa e mora crescem por dia)."""
        simulation = self._simulation

        def build(user: UserDTO) -> list[BaseDTO]:
            events: list[BaseDTO] = []
            for account, client_id in operated_accounts(
                simulation._funds, user, managed_only=True
            ):
                marked = client_id in credit
                if not (marked or day):
                    continue
                overview = build_overview(
                    simulation._engine.credit_book, client_id, simulation._current_date
                )
                if marked or any(loan.overdue for loan in overview.loans):
                    events.append(
                        CreditUpdateEventDTO(overview=overview, account=account)
                    )
            return events

        publish_each("credit_update", build)
