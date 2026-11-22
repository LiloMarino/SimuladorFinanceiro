"""
Os avisos do pregão das telas de renda fixa, Tesouro e governo: a cada dia o
servidor entrega o dado novo a quem tem a tela aberta, em vez de mandar a tela buscar de novo.

- Iguais para todos (título de renda fixa, catálogo e série do Tesouro): montados uma vez
  e enviados a todos os assinantes.
- Por jogador (Fundo Soberano, estatais, títulos do Tesouro): montados para cada
  assinante e entregues só a ele; nas contas de gestora, uma entrega por conta, marcada com
  o id dela.
- O que não muda no dia não sai: o catálogo do Tesouro segue a revisão mensal e os
  vencimentos.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING
from uuid import UUID

from backend.features.realtime import notify, subscribed_clients
from backend.features.realtime.schemas import (
    TreasuryHistoryUpdateEventDTO,
    TreasuryPositionsUpdateEventDTO,
)
from backend.features.simulation.feed_support import (
    guarded,
    operated_accounts,
    publish_each,
)

if TYPE_CHECKING:
    from backend.features.simulation.simulation import Simulation

FIXED_INCOME_OFFER_EVENT = "fixed_income_offer_update"
CORPORATE_EVENTS_EVENT = "corporate_events_update"


class DayFeed:
    """Os avisos por pregão de uma partida; todos os métodos rodam com o lock da simulação."""

    def __init__(self, simulation: Simulation):
        self._simulation = simulation
        # O último catálogo do Tesouro enviado: só um catálogo diferente sai de novo
        self._catalog_sent: dict | None = None

    def publish(self, *, month_changed: bool) -> None:
        """A cada pregão, entrega o dado novo de cada tela a quem a assina."""
        guarded(self._publish_fixed_income, "os títulos de renda fixa")
        guarded(self._publish_sovereign_fund, "o Fundo Soberano")
        guarded(self._publish_state_companies, "as estatais")
        guarded(self._publish_treasury_catalog, "o catálogo do Tesouro")
        guarded(
            lambda: self._publish_treasury_history(month_changed),
            "a série do Tesouro",
        )
        guarded(self._publish_treasury_positions, "os títulos do Tesouro")

    def publish_corporate_events(self, client_id: UUID, tickers: Iterable[str]) -> None:
        """Um provento ou desdobramento novo entra no histórico do ativo de quem o tem aberto."""
        for ticker in dict.fromkeys(tickers):
            guarded(
                lambda ticker=ticker: self._publish_corporate_events(client_id, ticker),
                "o histórico de proventos",
            )

    def _publish_corporate_events(self, client_id: UUID, ticker: str) -> None:
        event = f"{CORPORATE_EVENTS_EVENT}:{ticker}"
        if client_id not in subscribed_clients(event):
            return
        events = self._simulation.get_asset_corporate_events(client_id, ticker)
        if events is not None:
            notify(event, events.to_json(), to=client_id)

    def _publish_fixed_income(self) -> None:
        for asset in self._simulation.get_fixed_assets():
            event = f"{FIXED_INCOME_OFFER_EVENT}:{asset.asset_uuid}"
            if not subscribed_clients(event):
                continue
            notify(event, self._simulation.offer_of(asset).to_json())
        # O CDB da casa chega só ao dono
        for owner, house_offer in self._simulation.get_house_offers():
            event = f"{FIXED_INCOME_OFFER_EVENT}:{house_offer.asset_uuid}"
            if owner in subscribed_clients(event):
                notify(event, house_offer.to_json(), to=owner)

    def _publish_sovereign_fund(self) -> None:
        if self._simulation._government is None:
            return
        publish_each(
            "sovereign_fund_update",
            lambda user: [self._simulation.get_sovereign_fund(user)],
        )

    def _publish_state_companies(self) -> None:
        if self._simulation._government is None:
            return
        publish_each(
            "state_companies_update",
            lambda user: [self._simulation.get_state_companies(user)],
        )

    def _publish_treasury_catalog(self) -> None:
        if not subscribed_clients("treasury_catalog_update"):
            return
        catalog = self._simulation.get_treasury().to_json()
        if catalog != self._catalog_sent:
            self._catalog_sent = catalog
            notify("treasury_catalog_update", catalog)

    def _publish_treasury_history(self, month_changed: bool) -> None:
        if not month_changed or not subscribed_clients("treasury_history_update"):
            return
        history = self._simulation.get_treasury_history()
        if history:
            notify(
                "treasury_history_update",
                TreasuryHistoryUpdateEventDTO(point=history[-1]).to_json(),
            )

    def _publish_treasury_positions(self) -> None:
        simulation = self._simulation
        publish_each(
            "treasury_positions_update",
            lambda user: [
                TreasuryPositionsUpdateEventDTO(
                    positions=simulation.get_treasury_positions(client_id),
                    account=account,
                )
                for account, client_id in operated_accounts(simulation._funds, user)
            ],
        )
