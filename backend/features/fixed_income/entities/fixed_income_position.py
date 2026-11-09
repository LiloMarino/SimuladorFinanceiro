from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.enum import FixedIncomeType
from backend.features.fixed_income.accrual import (
    RedemptionBreakdown,
    daily_factor,
    index_daily_rate_on,
    redemption_breakdown,
    redemption_date,
    sale_breakdown,
)
from backend.features.fixed_income.quotes import NO_QUOTES, FixedIncomeQuotes
from backend.features.fixed_income.treasury import mark_factor
from backend.features.tax_policy import DEFAULT_TAX_POLICY, TaxPolicy


@dataclass
class FixedIncomePosition:
    """
    Uma posição de renda fixa. O montante (M) está na unidade do título: reais em tudo,
    menos na conta em dólar, em que é o saldo em US$. O capital aplicado (C) é sempre em
    reais, a base do IR.
    """

    asset: FixedIncomeAssetDTO
    total_applied: Decimal  # Capital aplicado (C)
    first_applied_date: date  # Data do primeiro aporte
    current_value: Decimal = field(init=False)  # Montante (M)
    # Último dia útil cujo rendimento já está em `current_value`
    last_accrual_date: date = field(init=False)

    def __post_init__(self):
        self.current_value = self.total_applied
        self.last_accrual_date = self.first_applied_date

    @classmethod
    def open(
        cls,
        asset: FixedIncomeAssetDTO,
        value: Decimal,
        day: date,
        quotes: FixedIncomeQuotes = NO_QUOTES,
        policy: TaxPolicy = DEFAULT_TAX_POLICY,
    ) -> "FixedIncomePosition":
        """A posição nascida do primeiro aporte de `value` reais em `day`."""
        position = cls(asset=asset, total_applied=Decimal(0), first_applied_date=day)
        position.invest(value, quotes, policy)
        return position

    @property
    def redemption_date(self) -> date:
        return redemption_date(self.asset.maturity_date)

    @property
    def marked_by_dollar(self) -> bool:
        return self.asset.investment_type is FixedIncomeType.DOLLAR_ACCOUNT

    def invest(
        self,
        value: Decimal,
        quotes: FixedIncomeQuotes = NO_QUOTES,
        policy: TaxPolicy = DEFAULT_TAX_POLICY,
    ):
        """
        Aporta `value` reais:
        - aumenta o capital aplicado (C) em `value`
        - aumenta o montante (M); na conta em dólar entra o que sobra do IOF do
          câmbio, convertido ao dólar do dia
        """
        self.total_applied += value
        if self.marked_by_dollar:
            self.current_value += value * (1 - policy.fx_iof_rate) / quotes.dollar
        else:
            self.current_value += value

    def accrue(self, day: date):
        """
        Aplica o rendimento do dia útil `day` sobre o montante (M).

        Cada dia rende uma única vez e nada rende depois do resgate, então o tick
        e a reconstrução por eventos podem chamar para o mesmo dia sem somar duas vezes.
        """
        if day <= self.last_accrual_date or day > self.redemption_date:
            return

        # O dia útil anterior ao tick é o que remunerou a noite até `day`
        index_rate = index_daily_rate_on(self.asset.rate_index, self.last_accrual_date)
        self.current_value *= daily_factor(self.asset, index_rate)
        self.last_accrual_date = day

    def units_for(self, reais: Decimal, quotes: FixedIncomeQuotes) -> Decimal:
        """Quanto do montante vale `reais` hoje: a própria quantia, ou o saldo em US$ na conta em dólar."""
        return reais / quotes.dollar if self.marked_by_dollar else reais

    def reais_value(self, quotes: FixedIncomeQuotes = NO_QUOTES) -> Decimal:
        """O montante em reais: o da curva, ou o saldo em US$ ao dólar de hoje."""
        return (
            self.current_value * quotes.dollar
            if self.marked_by_dollar
            else self.current_value
        )

    def withdraw(self, gross: Decimal):
        """
        Tira `gross` do título (G), na unidade do montante: o capital aplicado cai na
        mesma proporção do montante, então o rendimento por real aplicado não muda.
        """
        self.total_applied -= gross * self.total_applied / self.current_value
        self.current_value -= gross

    def breakdown(
        self,
        on: date,
        net_wanted: Decimal | None,
        policy: TaxPolicy = DEFAULT_TAX_POLICY,
        quotes: FixedIncomeQuotes = NO_QUOTES,
    ) -> RedemptionBreakdown:
        """O resgate em `on` pela política de impostos de `on`; sem `net_wanted`, o título inteiro."""
        return redemption_breakdown(
            self.reais_value(quotes),
            self.total_applied,
            self.asset.investment_type,
            (on - self.first_applied_date).days,
            net_wanted,
            policy,
        )

    def net_redemption_value(self) -> Decimal:
        """Valor creditado no vencimento, já descontados IOF e IR."""
        return self.breakdown(self.redemption_date, None).net

    def market_value(
        self, today: date, quotes: FixedIncomeQuotes = NO_QUOTES
    ) -> Decimal:
        """
        O que o título vale vendido hoje, em reais e antes dos impostos: o montante
        ajustado ao mercado. Só o Tesouro com marcação (Prefixado e IPCA+) sai da curva,
        pelo prêmio de risco do país; a conta em dólar vale o saldo ao dólar de hoje.
        """
        return self.reais_value(quotes) * mark_factor(self.asset, today, quotes.premium)

    def mark(self, today: date, quotes: FixedIncomeQuotes = NO_QUOTES) -> Decimal:
        """Marcação a mercado: quanto o preço de hoje está acima (ou abaixo) da curva."""
        return self.market_value(today, quotes) - self.reais_value(quotes)

    def sell_breakdown(
        self,
        today: date,
        gross: Decimal | None,
        quotes: FixedIncomeQuotes = NO_QUOTES,
        policy: TaxPolicy = DEFAULT_TAX_POLICY,
    ) -> RedemptionBreakdown:
        """A venda a mercado de `gross` (bruto) em `today`; sem `gross`, o título inteiro."""
        return sale_breakdown(
            self.market_value(today, quotes),
            self.total_applied,
            self.asset.investment_type,
            (today - self.first_applied_date).days,
            gross,
            policy,
        )
