from datetime import date

from backend.core.dto.base import BaseDTO


class DailyEquityFlowDTO(BaseDTO):
    """Compras menos vendas dos jogadores num ativo, num dia."""

    ticker: str
    flow_date: date
    quantity: int
