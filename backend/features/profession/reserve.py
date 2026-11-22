"""O que a política do bot vê do bolso dele, além do estado e da economia."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Reserve:
    """O caixa que um débito automático alcança e o que o imprevisto de saúde custa hoje, antes de qualquer multiplicador da profissão."""

    cash: Decimal
    health_cost: Decimal
