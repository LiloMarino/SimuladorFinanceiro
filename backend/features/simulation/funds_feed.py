"""
Os avisos das gestoras: as contas do jogador, a lista da sala, as ofertas públicas e a
página de cada gestora chegam a quem tem a tela aberta, já montados para ele.

Uma operação de gestora muda vários desses dados (a cota, o caixa, a oferta, as taxas) e
o pregão muda todos: cada mudança só marca, e a publicação sai uma vez, ao fechar a
operação mais externa, com o estado final.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.features.realtime import subscribed_clients
from backend.features.realtime.schemas import (
    FundAccountsUpdateEventDTO,
    FundRoomUpdateEventDTO,
)
from backend.features.simulation.feed_support import guarded, publish_each

if TYPE_CHECKING:
    from backend.features.simulation.simulation import Simulation

FUND_DETAIL_EVENT = "fund_update"


class FundsFeed:
    """Os avisos das gestoras de uma partida; todos os métodos rodam com o lock da simulação."""

    def __init__(self, simulation: Simulation):
        self._simulation = simulation
        self._changed = False

    def mark(self) -> None:
        """Algo nas gestoras mudou (PL, cotas, cotistas, oferta, taxas ou congelamento)."""
        self._changed = True

    def flush(self) -> None:
        """Entrega o estado atual a quem assina; sem mudança marcada não sai nada."""
        simulation = self._simulation
        if not self._changed:
            return
        self._changed = False
        funds = simulation._funds
        if funds is None:
            return
        guarded(
            lambda: publish_each(
                "fund_accounts_update",
                lambda user: [
                    FundAccountsUpdateEventDTO(
                        accounts=simulation.get_fund_accounts(user)
                    )
                ],
            ),
            "as contas das gestoras",
        )
        guarded(
            lambda: publish_each(
                "funds_list_update",
                lambda user: [FundRoomUpdateEventDTO(funds=simulation.get_funds(user))],
            ),
            "a lista das gestoras",
        )
        guarded(
            lambda: publish_each(
                "fund_offers_update",
                lambda user: [simulation.get_fund_offers(user)],
            ),
            "as ofertas das gestoras",
        )
        for fund in funds.funds():
            fund_id = fund.terms.id
            event = f"{FUND_DETAIL_EVENT}:{fund_id}"
            if subscribed_clients(event):
                guarded(
                    lambda event=event, fund_id=fund_id: publish_each(
                        event, lambda user: [simulation.get_fund(user, fund_id)]
                    ),
                    "a página da gestora",
                )
