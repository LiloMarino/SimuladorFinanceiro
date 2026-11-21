"""
Os avisos das prévias de operação da gestora (emissão, subscrição, oferta dirigida,
incorporação e recompra): o servidor entrega a prévia recalculada, ou o motivo da recusa, a
quem ainda tem o diálogo aberto.

Cada prévia deriva do pedido do cliente (assinatura com parâmetro): a rota HTTP responde na
hora e registra o último pedido dele na gestora; ao fechar a operação em curso, o servidor
recalcula para quem ainda assina e entrega só àquele cliente, sem reenviar a prévia igual.
Recalcula quando muda o que a prévia lê: a gestora (cota, oferta, taxas, cotistas), o caixa
pessoal de quem pediu (subscrição e oferta dirigida), o caixa da gestora (oferta dirigida e
recompra) e o dia.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any
from uuid import UUID

from fastapi import HTTPException

from backend.core.dto.base import BaseDTO
from backend.core.dto.fund import (
    FundBuybackPreviewDTO,
    FundDirectedIssuancePreviewDTO,
    FundIssuancePreviewDTO,
    FundIssuanceSubscriptionPreviewDTO,
    FundMergePreviewDTO,
)
from backend.core.dto.user import UserDTO
from backend.core.runtime.user_manager import UserManager
from backend.features.realtime.client_requests import ClientRequests
from backend.features.realtime.schemas import (
    FundBuybackPreviewEventDTO,
    FundDirectedPreviewEventDTO,
    FundIssuancePreviewEventDTO,
    FundMergePreviewEventDTO,
    FundSubscriptionPreviewEventDTO,
)
from backend.features.simulation.feed_support import (
    guarded,
    refusal_mark,
    refusal_reason,
)

if TYPE_CHECKING:
    from backend.features.simulation.simulation import Simulation

# O caixa que mexeu: quem o recebe no tempo real e a gestora dona (nula na conta pessoal)
type MovedAccount = tuple[UUID, int | None]


@dataclass(frozen=True)
class FundPreviewKind[T: BaseDTO]:
    """Uma prévia da gestora: o evento, a conta que ela faz, o que ela lê e o aviso que a entrega."""

    # Prefixo do evento `{prefix}:{fund_id}`
    prefix: str
    # Os parâmetros do pedido (quantidade, preço, gestora incorporada) viram o resultado da prévia
    compute: Callable[[Simulation, UserDTO, int, tuple], T]
    # Monta o aviso com os parâmetros do pedido e a prévia ou o motivo da recusa
    event: Callable[[tuple, T | None, str | None], BaseDTO]
    # A prévia lê o caixa pessoal de quem pediu
    reads_personal_cash: bool = False
    # A prévia lê o caixa da gestora
    reads_fund_cash: bool = False


ISSUANCE = FundPreviewKind[FundIssuancePreviewDTO](
    "fund_issuance_preview",
    lambda sim, user, fund_id, p: sim.preview_fund_issuance(user, fund_id, p[0]),
    lambda p, preview, refused: FundIssuancePreviewEventDTO(
        quotas=p[0], preview=preview, refused=refused
    ),
)

SUBSCRIPTION = FundPreviewKind[FundIssuanceSubscriptionPreviewDTO](
    "fund_subscription_preview",
    lambda sim, user, fund_id, p: sim.preview_fund_subscription(user, fund_id, p[0]),
    lambda p, preview, refused: FundSubscriptionPreviewEventDTO(
        quotas=p[0], preview=preview, refused=refused
    ),
    reads_personal_cash=True,
)

DIRECTED = FundPreviewKind[FundDirectedIssuancePreviewDTO](
    "fund_directed_preview",
    lambda sim, user, fund_id, p: sim.preview_fund_directed(user, fund_id, p[0]),
    lambda p, preview, refused: FundDirectedPreviewEventDTO(
        quotas=p[0], preview=preview, refused=refused
    ),
    reads_personal_cash=True,
    reads_fund_cash=True,
)

MERGE = FundPreviewKind[FundMergePreviewDTO](
    "fund_merge_preview",
    lambda sim, user, fund_id, p: sim.preview_fund_merge(user, fund_id, p[0]),
    lambda p, preview, refused: FundMergePreviewEventDTO(
        daughter_fund_id=p[0], preview=preview, refused=refused
    ),
)

BUYBACK = FundPreviewKind[FundBuybackPreviewDTO](
    "fund_buyback_preview",
    lambda sim, user, fund_id, p: sim.preview_fund_buyback(user, fund_id, p[0], p[1]),
    lambda p, preview, refused: FundBuybackPreviewEventDTO(
        quantity=p[0], max_price=p[1], preview=preview, refused=refused
    ),
    reads_fund_cash=True,
)

KINDS: tuple[FundPreviewKind[Any], ...] = (
    ISSUANCE,
    SUBSCRIPTION,
    DIRECTED,
    MERGE,
    BUYBACK,
)


@dataclass
class WatchedFundPreview:
    """O último pedido do cliente na gestora e o que o último envio mostrou (a prévia ou a recusa)."""

    params: tuple
    seen: Any = None


class FundPreviewFeed:
    """As prévias da gestora de uma partida; todos os métodos rodam com o lock da simulação."""

    def __init__(self, simulation: Simulation):
        self._simulation = simulation
        self._requests = {
            kind.prefix: ClientRequests[WatchedFundPreview](kind.prefix)
            for kind in KINDS
        }
        # Gestoras com prévia registrada por tipo: a publicação só olha para elas
        self._watched: set[tuple[FundPreviewKind[Any], int]] = set()
        self._funds_changed = False
        self._day = False
        self._moved: set[MovedAccount] = set()

    # Marcas do que a prévia lê

    def funds_changed(self) -> None:
        """Algo nas gestoras mudou (cota, oferta, taxas, cotistas ou congelamento)."""
        self._funds_changed = True

    def cash_moved(self, audience: Iterable[UUID], account: int | None) -> None:
        """O caixa da conta `account` mexeu."""
        self._moved.update((recipient, account) for recipient in audience)

    def day_passed(self) -> None:
        """O pregão mudou a data e os preços de todas as prévias."""
        self._day = True

    # Pedido do cliente

    def watch[T: BaseDTO](
        self,
        kind: FundPreviewKind[T],
        user: UserDTO,
        fund_id: int,
        params: tuple,
    ) -> T:
        """Calcula a prévia, responde e deixa o pedido registrado para os próximos avisos."""
        # Partida sem expansão recusa antes de registrar qualquer pedido
        self._simulation._ensure_funds()
        watched = WatchedFundPreview(params)
        try:
            preview = kind.compute(self._simulation, user, fund_id, params)
        except HTTPException as exc:
            # Só a recusa de regra registra o pedido: o aviso traz o motivo e a prévia que voltar a caber
            reason = refusal_reason(exc)
            if reason is not None:
                watched.seen = refusal_mark(reason)
                self._register(kind, fund_id, user, watched)
            raise
        watched.seen = preview
        self._register(kind, fund_id, user, watched)
        return preview

    def _register(
        self,
        kind: FundPreviewKind[Any],
        fund_id: int,
        user: UserDTO,
        watched: WatchedFundPreview,
    ) -> None:
        self._requests[kind.prefix].remember(str(fund_id), user.client_id, watched)
        self._watched.add((kind, fund_id))

    # Publicação ao fechar a operação

    def flush(self) -> None:
        """Entrega a prévia nova a quem a tem aberta; sem mudança marcada não sai nada."""
        if not (self._funds_changed or self._day or self._moved):
            return
        everyone = self._funds_changed or self._day
        moved = self._moved
        self._funds_changed, self._day, self._moved = False, False, set()
        for kind, fund_id in list(self._watched):
            requests = self._requests[kind.prefix]
            pending = requests.pending(str(fund_id))
            if not pending:
                self._watched.discard((kind, fund_id))
                continue
            for client_id, watched in pending.items():
                if everyone or _reads_moved(kind, client_id, fund_id, moved):
                    guarded(
                        lambda kind=kind, fund_id=fund_id, client_id=client_id, watched=watched: (
                            self._send(kind, fund_id, client_id, watched)
                        ),
                        "a prévia da gestora",
                    )

    def _send(
        self,
        kind: FundPreviewKind[Any],
        fund_id: int,
        client_id: UUID,
        watched: WatchedFundPreview,
    ) -> None:
        user = UserManager.get_user(client_id)
        if user is None:
            return
        preview: BaseDTO | None = None
        refused: str | None = None
        try:
            preview = kind.compute(self._simulation, user, fund_id, watched.params)
            seen: Any = preview
        except HTTPException as exc:
            refused = refusal_reason(exc)
            if refused is None:
                raise
            seen = refusal_mark(refused)
        if seen == watched.seen:
            return
        watched.seen = seen
        self._requests[kind.prefix].send(
            str(fund_id), client_id, kind.event(watched.params, preview, refused)
        )


def _reads_moved(
    kind: FundPreviewKind[Any], client_id: UUID, fund_id: int, moved: set[MovedAccount]
) -> bool:
    """O caixa que mexeu é um dos que a prévia lê."""
    if kind.reads_personal_cash and (client_id, None) in moved:
        return True
    return kind.reads_fund_cash and any(account == fund_id for _, account in moved)
