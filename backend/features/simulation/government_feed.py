"""
Os painéis do país ao vivo: cada painel que as telas do governo e da eleição leem por HTTP
tem o seu evento, e o servidor entrega o painel pronto a quem o assina.

- Iguais para todos (economia, orçamento, linha do tempo da eleição): montados uma vez e
  enviados a todos os assinantes.
- Por jogador (eleição, mapa, campanha e o histórico dela, promessas, balanços, governo, resumo do governo, base): montados para
  cada assinante e entregues só a ele, porque mudam com quem olha.
- O payload é o mesmo DTO que a rota devolve; sem assinante nada é montado.
- O painel igual ao último enviado ao mesmo destinatário não sai de novo.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import HTTPException

from backend.core.dto.base import BaseDTO
from backend.core.dto.user import UserDTO
from backend.core.runtime.user_manager import UserManager
from backend.features.realtime import notify, subscribed_clients
from backend.features.simulation.feed_support import guarded
from backend.types import JSONValue

if TYPE_CHECKING:
    from backend.features.simulation.simulation import Simulation

type Panel = BaseDTO | Sequence[BaseDTO]


def _json(panel: Panel) -> JSONValue:
    if isinstance(panel, BaseDTO):
        return panel.to_json()
    return [item.to_json() for item in panel]


class GovernmentFeed:
    """Os painéis do país de uma partida; todos os métodos rodam com o lock da simulação."""

    def __init__(self, simulation: Simulation):
        self._simulation = simulation
        # O último painel enviado por evento e destinatário (nulo quando o envio é a todos)
        self._sent: dict[tuple[str, UUID | None], JSONValue] = {}

    def publish(self) -> None:
        """Entrega o painel novo de cada tela a quem a assina."""
        simulation = self._simulation
        guarded(
            lambda: self._shared("economy_update", simulation.get_economy_panel),
            "o painel da economia",
        )
        if simulation._government is None:
            return
        guarded(
            lambda: self._shared("budget_update", simulation.get_budget),
            "o orçamento",
        )
        guarded(
            lambda: self._shared(
                "map_timeline_update", lambda: simulation.get_map_timeline(None)
            ),
            "a linha do tempo da eleição",
        )
        with simulation._publishing():
            for event, build in (
                ("election_update", simulation.get_election),
                ("map_update", simulation.get_map),
                ("campaign_update", simulation.get_campaign),
                ("campaign_history_update", simulation.get_campaign_history),
                ("promises_update", simulation.get_promises),
                ("balances_update", simulation.get_balances),
                ("government_panel_update", simulation.get_governance),
                ("government_status_update", simulation.get_government_status),
                ("base_update", simulation.get_base),
            ):
                guarded(
                    lambda event=event, build=build: self._each(event, build),
                    f"o painel {event}",
                )

    def _forget(self, event: str, listeners: set[UUID]) -> None:
        """Só quem ainda assina o evento tem o último envio guardado."""
        for key in [k for k in self._sent if k[0] == event]:
            if key[1] is None:
                if not listeners:
                    del self._sent[key]
            elif key[1] not in listeners:
                del self._sent[key]

    def _shared(self, event: str, build: Callable[[], Panel]) -> None:
        listeners = subscribed_clients(event)
        self._forget(event, listeners)
        if not listeners:
            return
        payload = _json(build())
        if self._sent.get((event, None)) == payload:
            return
        self._sent[(event, None)] = payload
        notify(event, payload)

    def _each(self, event: str, build: Callable[[UserDTO], Panel]) -> None:
        listeners = subscribed_clients(event)
        self._forget(event, listeners)
        if not listeners:
            return
        for player in UserManager.list_active_players():
            if player.client_id not in listeners:
                continue
            try:
                payload = _json(build(player))
            except HTTPException:
                # O painel recusa quem não tem o que ver (as promessas, de quem fundou o partido)
                continue
            key = (event, player.client_id)
            if self._sent.get(key) == payload:
                continue
            self._sent[key] = payload
            notify(event, payload, to=player.client_id)
