"""
As abas das Estatísticas da partida em andamento, montadas uma vez por mês de jogo.
A tela promete números do mês fechado, então o relatório montado vale até a partida
virar o mês; o fechamento, a comparação e o backtest leem o banco a cada pedido.
"""

from collections import defaultdict
from collections.abc import Callable
from datetime import date
from decimal import Decimal
from threading import Lock
from typing import cast

from pydantic import BaseModel

from backend.core.exceptions import NoActiveSimulationError
from backend.core.runtime.simulation_manager import SimulationManager

# A nota do fim de cada mês já fechado, por apelido do jogador
type ClosedScores = defaultdict[str, dict[date, Decimal | None]]


class ReportCache:
    """
    Vive no objeto da partida: a retomada cria outro, vazio. A partida chama `clear`
    na virada do mês, quando a meta sobe e quando entra jogador, antes de avisar a
    tela, para a nova busca já montar o relatório de novo.
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._generation = 0
        self._reports: dict[str, BaseModel] = {}
        self._building: dict[str, Lock] = {}
        # O corte de um mês que acabou só depende dos snapshots até ele, que não mudam
        # mais: sobrevive ao `clear` e a virada calcula só o mês novo
        self.closed_scores: ClosedScores = defaultdict(dict)

    def report[T: BaseModel](self, tab: str, build: Callable[[], T]) -> T:
        """
        O relatório guardado da aba, ou o montado agora. Pedidos simultâneos da mesma
        aba esperam um só montar; o montado durante um `clear` vale só para quem pediu.
        """
        with self._lock:
            building = self._building.setdefault(tab, Lock())
        with building:
            with self._lock:
                cached = self._reports.get(tab)
                generation = self._generation
            if cached is not None:
                return cast(T, cached)
            report = build()
            with self._lock:
                if generation == self._generation:
                    self._reports[tab] = report
            return report

    def clear(self) -> None:
        with self._lock:
            self._generation += 1
            self._reports.clear()


def match_cache(simulation_ids: list[int]) -> ReportCache | None:
    """O cache da partida em andamento quando o pedido é só dela; None nos demais."""
    try:
        simulation = SimulationManager.get_active_simulation()
    except NoActiveSimulationError:
        return None
    if simulation.backtest is not None or simulation_ids != [simulation.settings.id]:
        return None
    return simulation.statistics
