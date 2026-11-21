"""O que os feeds de tela têm em comum: entregar a cada assinante do evento o dado que só o servidor monta."""

from __future__ import annotations

import logging
from collections.abc import Callable, Collection, Iterable
from typing import TYPE_CHECKING
from uuid import UUID

from backend.core.dto.base import BaseDTO
from backend.core.dto.user import UserDTO
from backend.core.runtime.user_manager import UserManager
from backend.features.realtime import notify, subscribed_clients

if TYPE_CHECKING:
    from backend.features.funds.fund_book import FundBook

logger = logging.getLogger(__name__)


def publish_each(
    event: str,
    build: Callable[[UserDTO], Iterable[BaseDTO]],
    only: Collection[UUID] | None = None,
) -> None:
    """
    Monta e entrega o dado a cada cliente que assina `event`, só a ele; sem assinante nada é
    montado. `only` restringe a quem o dado mudou. `build` devolve um payload por conta do
    jogador (nenhum, quando não há o que mostrar).
    """
    for client_id in subscribed_clients(event):
        if only is not None and client_id not in only:
            continue
        user = UserManager.get_user(client_id)
        if user is None:
            continue
        for payload in build(user):
            notify(event, payload.to_json(), to=client_id)


def guarded(step: Callable[[], None], label: str) -> None:
    """Uma falha ao publicar uma tela não derruba o dia nem as demais telas."""
    try:
        step()
    except Exception:
        logger.exception("Erro ao publicar %s", label)


def operated_accounts(
    funds: FundBook | None, user: UserDTO, *, managed_only: bool = False
) -> list[tuple[int | None, UUID]]:
    """As contas do jogador no motor, como (id da gestora, client_id): a pessoal (id nulo) e as gestoras que ele opera, ou só gere."""
    accounts: list[tuple[int | None, UUID]] = [(None, user.client_id)]
    if funds is not None:
        owned = (
            funds.managed_by(user.id) if managed_only else funds.operated_by(user.id)
        )
        accounts += [(fund.terms.id, fund.account.client_id) for fund in owned]
    return accounts
