"""O Tesouro como a tela mostra: catálogo, histórico, termômetro do risco, posições e cotação de venda."""

import math
from collections.abc import Iterable
from datetime import date, timedelta
from decimal import Decimal

from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.dto.treasury import (
    TreasuryCatalogDTO,
    TreasuryHistoryPointDTO,
    TreasuryHistoryQuoteDTO,
    TreasuryPositionDTO,
    TreasurySaleQuoteDTO,
    TreasuryThermometerDTO,
    TreasuryTitleDTO,
)
from backend.core.enum import FixedIncomeType
from backend.core.utils import last_day_of_month
from backend.features.fixed_income import treasury
from backend.features.fixed_income.accrual import (
    effective_annual_rate,
    income_tax_rate,
    index_rate_on,
    iof_rate,
    project,
    redemption_breakdown,
    redemption_date,
)
from backend.features.fixed_income.entities.fixed_income_position import (
    FixedIncomePosition,
)
from backend.features.government.budget import BudgetCourse
from backend.features.government.budget import premium as debt_premium
from backend.features.tax_policy import TaxPolicy

MONTHS_PER_YEAR = 12
ONE_POINT_OF_DEBT = Decimal("0.01")


def _shown(
    asset: FixedIncomeAssetDTO, on: date, show_equivalent: bool
) -> Decimal | None:
    """O "equivale hoje" do título; a partida pode escondê-lo."""
    if not show_equivalent:
        return None
    return effective_annual_rate(asset, index_rate_on(asset.rate_index, on))


def _months_between(start: date, end: date) -> int:
    return max((end.year - start.year) * MONTHS_PER_YEAR + end.month - start.month, 0)


def build_catalog(
    start: date,
    today: date,
    issued: Iterable[FixedIncomeAssetDTO],
    thermometer: TreasuryThermometerDTO | None,
    show_equivalent: bool,
) -> TreasuryCatalogDTO:
    """Os seis títulos à venda no mês, com a taxa travada que `issued` guarda aberta em base e prêmio."""
    by_name = {
        asset.name: asset
        for asset in issued
        if asset.investment_type is FixedIncomeType.TESOURO_DIRETO
    }
    titles: list[TreasuryTitleDTO] = []
    for title in treasury.catalog(start, today):
        asset = by_name[title.name]
        premium = asset.risk_premium or Decimal(0)
        titles.append(
            TreasuryTitleDTO(
                asset_uuid=asset.asset_uuid,
                name=asset.name,
                rate_index=asset.rate_index,
                maturity_date=asset.maturity_date,
                months_to_maturity=_months_between(today, asset.maturity_date),
                base_rate=asset.interest_rate - premium,
                premium=premium,
                rate=asset.interest_rate,
                effective_annual_rate=_shown(asset, today, show_equivalent),
                sold_until=title.sold_until,
                replacement_name=title.replacement_name,
            )
        )
    return TreasuryCatalogDTO(
        next_review=last_day_of_month(today) + timedelta(days=1),
        titles=titles,
        thermometer=thermometer,
    )


def build_thermometer(budget: BudgetCourse, today: date) -> TreasuryThermometerDTO:
    """
    O prêmio de risco do país e a faixa em que a dívida ÷ PIB o coloca. O ritmo da
    dívida é a variação dos últimos 12 meses fechados, dividida por 12.
    """
    closed = budget.months_until(today)
    latest = budget.latest(today)
    debt = latest.debt
    band = treasury.band_index(debt)

    change: Decimal | None = None
    if len(closed) >= MONTHS_PER_YEAR:
        year_ago = last_day_of_month(
            date(latest.month_end.year - 1, latest.month_end.month, 1)
        )
        change = debt - budget.latest(year_ago).debt

    last_band = len(treasury.DEBT_BAND_LIMITS)
    next_limit = treasury.DEBT_BAND_LIMITS[band] if band < last_band else None
    to_next = None if next_limit is None else next_limit - debt
    months_to_next = None
    if to_next is not None and change is not None and change > 0:
        months_to_next = math.ceil(to_next / (change / MONTHS_PER_YEAR))

    return TreasuryThermometerDTO(
        premium=latest.premium,
        premium_per_debt_point=debt_premium(debt + ONE_POINT_OF_DEBT)
        - debt_premium(debt),
        band=treasury.BAND_NAMES[band],
        band_index=band,
        debt=debt,
        debt_change_12m=change,
        next_band=treasury.BAND_NAMES[band + 1] if band < last_band else None,
        next_band_limit=next_limit,
        debt_to_next_band=to_next,
        months_to_next_band=months_to_next,
    )


def build_history(
    points: list[treasury.MonthPoint], show_equivalent: bool
) -> list[TreasuryHistoryPointDTO]:
    """A série mensal do gráfico: um ponto por mês, com SELIC e IPCA do dia 1º."""
    history: list[TreasuryHistoryPointDTO] = []
    for point in points:
        rates = treasury.MarketRates.on(point.first)
        history.append(
            TreasuryHistoryPointDTO(
                month=point.first,
                selic=rates.selic,
                ipca=rates.ipca,
                premium=point.premium,
                debt=point.debt,
                band_index=None
                if point.debt is None
                else treasury.band_index(point.debt),
                quotes=[
                    TreasuryHistoryQuoteDTO(
                        name=q.title.name,
                        rate_index=q.title.rate_index,
                        maturity_date=q.title.maturity,
                        base_rate=q.base,
                        premium=q.premium,
                        effective_annual_rate=q.effective if show_equivalent else None,
                    )
                    for q in point.quotes
                ],
            )
        )
    return history


def build_position(
    position: FixedIncomePosition, today: date, premium: Decimal
) -> TreasuryPositionDTO:
    market_value = position.market_value(today, premium)
    asset = position.asset
    return TreasuryPositionDTO(
        asset=asset,
        first_applied_date=position.first_applied_date,
        bought_rate=asset.interest_rate,
        today_rate=treasury.rate_on(
            asset.rate_index, asset.maturity_date, today, premium
        ),
        total_applied=position.total_applied,
        yield_amount=position.current_value - position.total_applied,
        mark=market_value - position.current_value,
        market_value=market_value,
    )


def build_sale_quote(
    position: FixedIncomePosition,
    amount: Decimal,
    cash: Decimal,
    today: date,
    premium: Decimal,
    policy: TaxPolicy,
) -> TreasurySaleQuoteDTO:
    """A venda de `amount` bruto hoje, lado a lado com esperar a mesma parte até o vencimento."""
    asset = position.asset
    market_value = position.market_value(today, premium)
    days_held = (today - position.first_applied_date).days
    maturity = redemption_date(asset.maturity_date)

    sale = (
        position.sell_breakdown(today, amount, premium, policy)
        if 0 < amount <= market_value
        else None
    )
    values: dict[str, Decimal | None] = dict.fromkeys(
        (
            "applied_amount",
            "yield_amount",
            "mark",
            "maturity_gross_amount",
            "maturity_income_tax",
            "maturity_net_amount",
        )
    )
    if sale is not None:
        # A parte vendida carrega a mesma fração do aplicado e do montante da curva
        share = sale.gross / market_value
        applied = position.total_applied * share
        curve = position.current_value * share
        at_maturity = project(asset, curve, today, policy).gross_amount
        waiting = redemption_breakdown(
            at_maturity,
            applied,
            asset.investment_type,
            (maturity - position.first_applied_date).days,
            None,
            policy,
        )
        values = {
            "applied_amount": applied,
            "yield_amount": curve - applied,
            "mark": sale.gross - curve,
            "maturity_gross_amount": at_maturity,
            "maturity_income_tax": waiting.income_tax,
            "maturity_net_amount": waiting.net,
        }

    return TreasurySaleQuoteDTO(
        amount=amount,
        max_amount=market_value,
        first_applied_date=position.first_applied_date,
        bought_rate=asset.interest_rate,
        today_rate=treasury.rate_on(
            asset.rate_index, asset.maturity_date, today, premium
        ),
        days_held=days_held,
        iof_rate=iof_rate(days_held),
        iof=sale and sale.iof,
        income_tax_rate=income_tax_rate(asset.investment_type, days_held, policy),
        income_tax=sale and sale.income_tax,
        net_amount=sale and sale.net,
        cash_before=cash,
        cash_after=sale and cash + sale.net,
        remaining=sale and sale.remaining,
        full=sale is not None and sale.full,
        maturity_date=maturity,
        **values,
    )
