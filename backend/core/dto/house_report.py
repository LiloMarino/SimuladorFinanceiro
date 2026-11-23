from datetime import date
from decimal import Decimal

from backend.core.dto.base import BaseDTO
from backend.core.enum import HouseResult, OrderAction


class HouseRecommendationDTO(BaseDTO):
    """Uma recomendação do relatório da casa: o lado, o preço do dia, o alvo, o prazo e, depois do desfecho, o resultado."""

    id: int
    # O dia 1 do mês do relatório e o dia em que ele saiu
    report_month: date
    issued_on: date
    ticker: str
    side: OrderAction
    price: Decimal
    target: Decimal
    deadline: date
    # Nulo enquanto a recomendação está em aberto
    result: HouseResult | None
    # O preço que o placar mostra: o que o alvo alcançou, ou o fechamento do prazo
    result_price: Decimal | None
    resolved_on: date | None


class HousePickDTO(BaseDTO):
    """A ação de uma recomendação do relatório vigente e o lado dela; é o que o selo da Renda variável mostra."""

    ticker: str
    side: OrderAction
