"""
Versões das séries de preço e de indicador.

A versão 0 é a série comum, real e gerada. Uma partida salva que jogou dias
gerados guarda a cópia deles na versão de número igual ao id dela antes de o
gerado ser trocado, e lê a própria cópia onde ela existe e a comum no resto.
"""

from sqlalchemy import ColumnElement, and_, exists, or_
from sqlalchemy.orm import aliased

from backend.core.exceptions import NoActiveSimulationError
from backend.core.models.models import EconomicIndicatorHistory, StockPriceHistory
from backend.core.runtime.simulation_manager import SimulationManager

COMMON_VERSION = 0

type SeriesModel = type[StockPriceHistory] | type[EconomicIndicatorHistory]


def reading_version(simulation_id: int | None = None) -> int:
    """A versão da partida pedida, senão a da partida ativa, senão a comum."""
    if simulation_id is not None:
        return simulation_id
    try:
        return SimulationManager.get_active_simulation_id()
    except NoActiveSimulationError:
        return COMMON_VERSION


def _key(model: SeriesModel) -> tuple[str, str]:
    if model is StockPriceHistory:
        return "stock_id", "price_date"
    return "series", "ref_date"


def seen_by(model: SeriesModel, version: int) -> ColumnElement[bool]:
    """Filtro das linhas que a versão vê: a cópia dela, e a comum onde não há cópia."""
    common = model.version == COMMON_VERSION
    if version == COMMON_VERSION:
        return common
    copy = aliased(model)
    same_day = [
        getattr(copy, column) == getattr(model, column) for column in _key(model)
    ]
    return or_(
        model.version == version,
        and_(common, ~exists().where(*same_day, copy.version == version)),
    )
