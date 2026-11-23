from datetime import date
from decimal import Decimal

from backend.core.dto.base import BaseDTO
from backend.core.enum import PropertySize, PropertyStatus


class PropertyDTO(BaseDTO):
    """Um imóvel do Locador como o banco guarda: o preço do dia e o aluguel em vigor saem destes campos."""

    id: int
    size: PropertySize
    name: str
    # O preço na data de início da sala; o do dia é este vezes o IVG-R acumulado
    base_price: Decimal
    # O mês da oferta de que o imóvel saiu; nulo nos imóveis iniciais
    offer_month: date | None
    # O aluguel fixado na assinatura do contrato e o dia dela; o IGP-M o reajusta a cada 12 meses
    contract_rent: Decimal
    contract_start: date
    status: PropertyStatus
    # Desde quando está vago; nulo fora da vacância
    vacant_since: date | None
    # O dia em que a venda pedida conclui; nulo fora da venda
    sale_due: date | None


class PropertyDraft(BaseDTO):
    """O imóvel que ainda não tem linha: o que a semeadura e a compra gravam."""

    size: PropertySize
    name: str
    base_price: Decimal
    offer_month: date | None
    contract_rent: Decimal
    contract_start: date
