from datetime import date
from decimal import Decimal

from backend.core.dto.base import BaseDTO


class EconomyPointDTO(BaseDTO):
    """A economia num dia da partida; as taxas são frações (0.1425 = 14,25% ao ano)."""

    date: date
    selic: Decimal
    # Inflação acumulada em 12 meses
    ipca: Decimal
    # SELIC menos IPCA: quanto o dinheiro rende de verdade
    real_rate: Decimal
    # Meta de inflação do ano
    target: Decimal
    # Folga da meta: a inflação dentro de meta ± tolerância cumpre o regime de metas
    tolerance: Decimal
    # Crescimento do PIB em 12 meses e desemprego, no último fechamento de mês
    growth: Decimal
    unemployment: Decimal
    # Dívida bruta em fração do PIB e prêmio de risco que ela cobra; nulos sem a expansão Governo
    debt: Decimal | None
    premium: Decimal | None


class CopomChangeDTO(BaseDTO):
    """Dia em que a SELIC mudou de nível."""

    date: date
    # A mudança em fração (0.005 = sobe 0,5 ponto)
    change: Decimal
    # A SELIC depois da mudança
    selic: Decimal


class GrowthPartsDTO(BaseDTO):
    """
    O que puxa o alvo do crescimento hoje, em fração ao ano: tendência + juro real +
    bolsa dão o alvo, e o crescimento anda um quarto do caminho até ele a cada mês.
    """

    trend: Decimal
    # Juro real do dia e quanto ele soma (negativo quando acima do neutro)
    real_rate: Decimal
    real_rate_part: Decimal
    neutral_real_rate: Decimal
    # Alta do Ibovespa em 12 meses (nula sem série de bolsa) e quanto ela soma
    stocks: Decimal | None
    stocks_part: Decimal
    # Para onde o crescimento caminha e onde ele está hoje
    target: Decimal
    growth: Decimal


class DebtSummaryDTO(BaseDTO):
    """A dívida do governo no último fechamento de mês."""

    month_end: date
    # Em fração do PIB
    debt: Decimal
    premium: Decimal
    # Em reais: a dívida, o PIB em 12 meses e o resultado do mês (negativo é déficit); o
    # resultado é nulo antes do primeiro fechamento
    debt_amount: Decimal
    gdp: Decimal
    month_result: Decimal | None


class EconomyPanelDTO(BaseDTO):
    points: list[EconomyPointDTO]
    copom_changes: list[CopomChangeDTO]
    growth_parts: GrowthPartsDTO
    # Só nas partidas com a expansão Governo & Política
    debt: DebtSummaryDTO | None
