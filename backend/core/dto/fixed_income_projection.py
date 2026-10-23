from datetime import date
from decimal import Decimal

from backend.core.dto.base import BaseDTO


class FixedIncomeProjectionDTO(BaseDTO):
    """
    Projeção de um investimento levado até o vencimento.

    Percentuais são frações sobre o valor aplicado (0.12 = 12%) e não dependem
    de `amount`, então valem mesmo com `amount` zero.
    """

    amount: Decimal
    index_rate: Decimal
    effective_annual_rate: Decimal
    business_days: int
    redemption_date: date
    gross_amount: Decimal
    gross_return: Decimal
    gross_return_pct: Decimal
    income_tax_rate: Decimal
    income_tax: Decimal
    income_tax_pct: Decimal
    net_amount: Decimal
    net_return: Decimal
    net_return_pct: Decimal


class IncomeTaxBracketDTO(BaseDTO):
    # Até `max_days` dias corridos de aplicação; None é a faixa final, sem teto
    max_days: int | None
    rate: Decimal


class FixedIncomeQuoteDTO(BaseDTO):
    """
    A projeção com o caixa do jogador e a tabela regressiva, para a boleta.

    A taxa equivalente e o que o dinheiro vira no vencimento (bruto, IR e líquido)
    são None quando a partida esconde essas ajudas.
    """

    amount: Decimal
    index_rate: Decimal
    business_days: int
    redemption_date: date
    income_tax_rate: Decimal
    effective_annual_rate: Decimal | None
    gross_amount: Decimal | None
    gross_return: Decimal | None
    gross_return_pct: Decimal | None
    income_tax: Decimal | None
    income_tax_pct: Decimal | None
    net_amount: Decimal | None
    net_return: Decimal | None
    net_return_pct: Decimal | None
    cash_before: Decimal
    cash_after: Decimal
    # O que cabe na compra: o caixa, limitado pelo que resta do teto por jogador
    max_amount: Decimal
    # Capital já aplicado no título com teto; None quando o título não tem teto
    cap_used: Decimal | None
    income_tax_brackets: list[IncomeTaxBracketDTO]


class NextTaxDropDTO(BaseDTO):
    on: date
    rate: Decimal


class FixedIncomeRedemptionQuoteDTO(BaseDTO):
    """
    O resgate de uma posição de liquidez diária hoje, por `amount` líquido no caixa.

    Os campos de valor são None quando `amount` é zero ou passa de `max_amount`,
    o líquido de resgatar a posição inteira.
    """

    amount: Decimal
    max_amount: Decimal
    position_value: Decimal
    total_applied: Decimal
    first_applied_date: date
    days_held: int
    gross_amount: Decimal | None
    yield_amount: Decimal | None
    iof_rate: Decimal
    iof: Decimal | None
    income_tax_rate: Decimal
    income_tax: Decimal | None
    net_amount: Decimal | None
    cash_before: Decimal
    cash_after: Decimal | None
    remaining: Decimal | None
    full: bool
    next_tax_drop: NextTaxDropDTO | None
    iof_free_date: date | None
