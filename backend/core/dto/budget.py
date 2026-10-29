from datetime import date
from decimal import Decimal

from backend.core.dto.base import BaseDTO


class BudgetTaxDTO(BaseDTO):
    """Um imposto do jogo: a alíquota de hoje e a padrão, o que arrecada e a diferença contra a padrão."""

    key: str
    name: str
    # Nula quando o imposto é isento
    rate: Decimal | None
    default_rate: Decimal | None
    # Em fração do PIB por ano
    revenue: Decimal
    difference: Decimal
    # Na renda fixa, a alíquota do prazo mais curto e a do mais longo, hoje e na política padrão
    top_rate: Decimal | None
    floor_rate: Decimal | None
    default_top_rate: Decimal | None
    default_floor_rate: Decimal | None


class BudgetMonthDTO(BaseDTO):
    """
    O orçamento no fim de um mês, em fração do PIB por ano (0.0183 = 1,83%). Antes do
    primeiro fechamento, `closed` é falso e juros e resultado ainda não existem.
    """

    month_end: date
    revenue: Decimal
    spending: Decimal
    primary: Decimal
    interest: Decimal
    result: Decimal
    # Dívida em fração do PIB e o prêmio de risco que ela cobra nos títulos novos
    debt: Decimal
    premium: Decimal
    # PIB em 12 meses, em reais
    gdp: Decimal
    closed: bool


class BudgetAmountsDTO(BaseDTO):
    """O mês do último fechamento em reais: o que entrou, o que saiu e o resultado."""

    revenue: Decimal
    spending: Decimal
    primary: Decimal
    interest: Decimal
    # Negativo é déficit
    result: Decimal
    debt: Decimal


class PremiumPointDTO(BaseDTO):
    """Um ponto da curva do prêmio de risco: a dívida em fração do PIB e o prêmio que ela cobra."""

    debt: Decimal
    premium: Decimal


class BudgetDTO(BaseDTO):
    today: date
    # O último fechamento de mês, ou o ponto de partida antes do primeiro
    month: BudgetMonthDTO
    amounts: BudgetAmountsDTO
    taxes: list[BudgetTaxDTO]
    # O resto da arrecadação do país, fixo, e a receita total com os impostos de hoje
    fixed_revenue: Decimal
    total_revenue: Decimal
    # A receita total contra a da política padrão
    total_difference: Decimal
    # Os fechamentos já feitos e a projeção até o fim do mandato, se nada mais mudar
    history: list[BudgetMonthDTO]
    projection: list[BudgetMonthDTO]
    projection_end: date
    premium_curve: list[PremiumPointDTO]
    # Dívida em fração do PIB abaixo da qual o prêmio é zero
    premium_floor: Decimal


class BudgetEffectDTO(BaseDTO):
    """
    O que uma medida faz com a conta do governo, estimado: o imposto atingido, a
    receita dele e o resultado e a dívida no fim do mandato, antes e depois.
    """

    # Variação da receita total, em fração do PIB por ano e em reais por ano
    revenue_change: Decimal
    revenue_change_amount: Decimal
    # Variação do gasto (positivo gasta mais), em fração do PIB por ano e em reais por ano
    spending_change: Decimal
    spending_change_amount: Decimal
    # O gasto total do governo hoje e no fim da projeção com a medida, em fração do PIB por ano
    spending_before: Decimal
    spending_after: Decimal
    tax_name: str
    # Nulas quando o imposto é isento
    rate_before: Decimal | None
    rate_after: Decimal | None
    # Receita do imposto atingido, em fração do PIB por ano
    tax_revenue_before: Decimal
    tax_revenue_after: Decimal
    # Resultado do governo por ano, em fração do PIB
    result_before: Decimal
    result_after: Decimal
    # Dívida em fração do PIB no fim da projeção, se nada mais mudar
    debt_end: date
    debt_before: Decimal
    debt_after: Decimal


class QueueBudgetDTO(BaseDTO):
    """A fila inteira do Congresso, se passar: o que muda no resultado do governo."""

    # Variação do resultado (receita menos gasto), em fração do PIB por ano
    total: Decimal
    result_now: Decimal
    result_if_passes: Decimal


class InitialAccountOptionDTO(BaseDTO):
    """O que a partida herda numa das duas contas iniciais."""

    # Dívida em fração do PIB e resultado primário por ano (negativo é déficit)
    debt: Decimal
    primary: Decimal
    # O primário em reais por ano
    primary_amount: Decimal
    # O prêmio de risco que essa dívida já cobra no primeiro dia
    premium: Decimal


class InitialAccountDTO(BaseDTO):
    """A conta inicial do governo para um início de partida, nas duas opções da sala."""

    # O ano do início da partida: a dívida é a do fim do ano anterior e o primário, o deste ano
    year: int
    playable: InitialAccountOptionDTO
    realistic: InitialAccountOptionDTO
