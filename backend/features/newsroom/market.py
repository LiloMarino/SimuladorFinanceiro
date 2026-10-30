"""
O pregão como o noticiário o lê: as cotações do dia, os fechamentos anteriores de cada
ativo e as séries de indicadores. As regras só leem este retrato, sem tocar no banco.
"""

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date

from backend.core.enum import AssetClass
from backend.core.repository.economic import IndicatorHistory


@dataclass(frozen=True)
class Quote:
    """O fechamento de um ativo no dia, com o setor em que ele está classificado."""

    ticker: str
    name: str
    asset_class: AssetClass
    sector: str | None
    close: float


def no_spending(day: date) -> float:
    """Sem medida de gasto aprovada, a inflação não leva nenhum ponto a mais."""
    return 0.0


@dataclass(frozen=True)
class MarketDay:
    day: date
    # O pregão anterior da partida; o dia de uma regra "contra ontem" olha para ele
    previous: date
    # Só os ativos que negociaram hoje
    quotes: Sequence[Quote]
    # Os fechamentos de cada ativo antes de hoje, do mais antigo ao mais recente
    closes: Mapping[str, Sequence[float]]
    selic: IndicatorHistory
    ipca: IndicatorHistory
    ibov: IndicatorHistory
    # O último dia com dado real; depois dele o mercado é gerado. Nulo sem dado real.
    real_until: date | None
    simulation_id: int
    # Os pontos de IPCA em 12 meses que as medidas de gasto aprovadas somam à série em cada dia
    spending_inflation: Callable[[date], float] = field(default=no_spending)
