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


class FixedIncomeQuoteDTO(FixedIncomeProjectionDTO):
    """A projeção com o caixa do jogador e a tabela regressiva, para a boleta."""

    cash_before: Decimal
    cash_after: Decimal
    max_amount: Decimal
    income_tax_brackets: list[IncomeTaxBracketDTO]
