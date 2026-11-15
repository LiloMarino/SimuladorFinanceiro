from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from backend.core.dto.base import BaseDTO
from backend.core.dto.government import MeasurePreviewDTO
from backend.core.enum import SovereignFlowKind


class SovereignFundDTO(BaseDTO):
    """O registro do fundo na partida: a carteira e a conta que opera nela."""

    portfolio_id: int
    client_id: UUID


class SovereignFlowDTO(BaseDTO):
    """Um movimento entre o fundo e o Tesouro."""

    day: date
    kind: SovereignFlowKind
    amount: Decimal
    # A medida do aporte; nulo na venda e no dividendo
    measure_id: int | None = None


class SovereignPositionDTO(BaseDTO):
    """Um ativo na carteira do fundo, com a fatia que ele tem da empresa ou da gestora."""

    ticker: str
    name: str
    # Cota de gestora ou ação importada
    is_fund: bool
    size: Decimal
    avg_price: Decimal
    current_price: Decimal
    current_value: Decimal
    return_value: Decimal
    # A fração (0.12 = 12%) do que existe em circulação que o fundo guarda; nula sem o número de papéis
    stake: Decimal | None
    # Quantos papéis o fundo ainda pode comprar até o teto; nulo sem o número de papéis
    room: Decimal | None


class SovereignFundPanelDTO(BaseDTO):
    """O Fundo Soberano como a sala vê: caixa, carteira e o que já foi e voltou do Tesouro."""

    # Quem lê é o presidente em exercício, a quem a conta do fundo se abre
    is_president: bool
    cash: Decimal
    # O que o Tesouro aportou e o que voltou a ele (vendas e dividendos), em reais
    contributed: Decimal
    returned: Decimal
    # O teto de fatia por empresa e por gestora, em fração (0.2 = 20%)
    ceiling: Decimal
    # O valor das posições a preço de mercado
    invested: Decimal
    positions: list[SovereignPositionDTO]


class SovereignContributionRequest(BaseDTO):
    """O aporte que o presidente simula, em reais."""

    value: Decimal


class SovereignContributionPreviewDTO(BaseDTO):
    """O que o aporte faria: a medida (voto, vigência e dívida) e o caixa do fundo antes e depois."""

    measure: MeasurePreviewDTO
    cash_before: Decimal
    cash_after: Decimal
