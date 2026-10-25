"""
Cálculo de renda fixa: a única fórmula de rendimento do simulador.

O jogo ao vivo (um `accrue` por tick), a reconstrução a partir dos eventos
(retomada) e a projeção mostrada na compra aplicam a mesma sequência de
multiplicações `valor *= daily_factor(...)`, um dia útil por vez e na mesma
ordem, em `Decimal`. Ao vivo e reconstrução leem a taxa real de cada dia e
chegam ao mesmo valor ao centavo; a projeção congela o último valor conhecido
na compra, e coincide com eles quando o indexador não muda.

A taxa do dia útil `d` remunera a noite de `d` até o próximo dia útil: o tick
rende com a taxa do dia útil anterior a ele.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_EVEN, Decimal
from functools import lru_cache

from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO, FixedIncomeOfferDTO
from backend.core.dto.fixed_income_projection import (
    FixedIncomeProjectionDTO,
    IncomeTaxBracketDTO,
)
from backend.core.enum import FixedIncomeType, IndicatorSeries, RateIndexType
from backend.core.indicators import (
    BUSINESS_DAYS_PER_YEAR,
    annual_index_rate,
    daily_rate,
    index_daily_rate,
    last_known_value,
)
from backend.core.utils import is_business_day, next_business_day
from backend.features.tax_policy import DEFAULT_TAX_POLICY, TaxPolicy

CENT = Decimal("0.01")

# IOF regressivo sobre o rendimento: alíquota do 1º ao 29º dia corrido; do 30º em diante é zero
IOF_TABLE: tuple[Decimal, ...] = tuple(
    Decimal(pct) / 100
    for pct in (
        96, 93, 90, 86, 83, 80, 76, 73, 70, 66, 63, 60, 56, 53, 50,
        46, 43, 40, 36, 33, 30, 26, 23, 20, 16, 13, 10, 6, 3,
    )
)  # fmt: skip
IOF_FREE_DAYS = len(IOF_TABLE) + 1


INDEX_SERIES: dict[RateIndexType, IndicatorSeries] = {
    RateIndexType.CDI: IndicatorSeries.CDI,
    RateIndexType.IPCA: IndicatorSeries.IPCA,
    RateIndexType.SELIC: IndicatorSeries.SELIC,
}


def index_rate_on(rate_index: RateIndexType, on: date) -> Decimal:
    """Taxa anual do indexador conhecida em `on`. Prefixado não tem indexador: vale 0."""
    if rate_index is RateIndexType.PREFIXADO:
        return Decimal(0)
    return annual_index_rate(INDEX_SERIES[rate_index], on)


def effective_annual_rate(asset: FixedIncomeAssetDTO, index_rate: Decimal) -> Decimal:
    """
    Taxa anual que o título rende, combinando o indexador com a taxa do título.

    - Prefixado: a própria taxa (0.12 = 12% a.a.).
    - CDI: percentual do CDI (interest_rate 1.05 = 105% do CDI).
    - IPCA/SELIC: spread composto sobre o índice, como no mercado:
      (1 + índice) * (1 + spread) - 1.
    """
    match asset.rate_index:
        case RateIndexType.PREFIXADO:
            return asset.interest_rate
        case RateIndexType.CDI:
            return index_rate * asset.interest_rate
        case RateIndexType.IPCA | RateIndexType.SELIC:
            return (1 + index_rate) * (1 + asset.interest_rate) - 1


@lru_cache(maxsize=1024)
def annual_to_daily_factor(annual_rate: Decimal) -> Decimal:
    """Fator de um dia útil: (1 + taxa anual) ^ (1/252)."""
    return (1 + annual_rate) ** (Decimal(1) / BUSINESS_DAYS_PER_YEAR)


def daily_factor(asset: FixedIncomeAssetDTO, index_rate: Decimal | None) -> Decimal:
    """
    Fator de um dia útil do título, com `index_rate` a fração que o indexador
    rendeu no dia. None é dia sem pregão no indexador: nada rende.

    - Prefixado: (1 + taxa) ^ (1/252).
    - CDI: 1 + CDI do dia x percentual do CDI.
    - IPCA/SELIC: (1 + índice do dia) x (1 + spread) ^ (1/252).
    """
    if index_rate is None:
        return Decimal(1)

    match asset.rate_index:
        case RateIndexType.PREFIXADO:
            return annual_to_daily_factor(asset.interest_rate)
        case RateIndexType.CDI:
            return 1 + index_rate * asset.interest_rate
        case RateIndexType.IPCA | RateIndexType.SELIC:
            return (1 + index_rate) * annual_to_daily_factor(asset.interest_rate)


def index_daily_rate_on(rate_index: RateIndexType, day: date) -> Decimal | None:
    """Fração que o indexador rendeu no dia útil `day`. Prefixado: 0."""
    if rate_index is RateIndexType.PREFIXADO:
        return Decimal(0)
    return index_daily_rate(INDEX_SERIES[rate_index], day)


def redemption_date(maturity: date) -> date:
    """Dia do resgate: o primeiro dia útil a partir do vencimento (o tick que o vê)."""
    return maturity if is_business_day(maturity) else next_business_day(maturity)


def income_tax_rate(
    investment_type: FixedIncomeType,
    days_held: int,
    policy: TaxPolicy = DEFAULT_TAX_POLICY,
) -> Decimal:
    """Alíquota de IR pelos dias corridos de aplicação; LCI e LCA têm alíquota própria."""
    if investment_type in (FixedIncomeType.LCI, FixedIncomeType.LCA):
        return policy.lci_lca_rate

    for max_days, rate in policy.fixed_income_brackets:
        if days_held <= max_days:
            return rate
    return policy.fixed_income_floor


def iof_rate(days_held: int) -> Decimal:
    """Alíquota do IOF pelos dias corridos de aplicação; o dia da compra paga como o 1º."""
    if days_held >= IOF_FREE_DAYS:
        return Decimal(0)
    return IOF_TABLE[max(days_held, 1) - 1]


@dataclass(frozen=True)
class RedemptionBreakdown:
    """Um resgate decomposto: o que sai do título, os impostos e o que chega ao caixa."""

    gross: Decimal  # G: o que sai do título
    yield_amount: Decimal  # Rendimento contido em G
    iof: Decimal
    income_tax: Decimal
    net: Decimal  # O que o caixa recebe
    remaining: Decimal  # O que fica no título

    @property
    def full(self) -> bool:
        return self.remaining <= 0


def redemption_breakdown(
    current_value: Decimal,
    total_applied: Decimal,
    investment_type: FixedIncomeType,
    days_held: int,
    net_wanted: Decimal | None,
    policy: TaxPolicy = DEFAULT_TAX_POLICY,
) -> RedemptionBreakdown:
    """
    Resgate de um título de montante M e capital C.

    O rendimento da parte resgatada G é G·(M-C)/M. O IOF incide sobre ele e o IR,
    sobre o que sobra do rendimento depois do IOF; os dois saem do bruto, e o caixa
    recebe o líquido. `net_wanted` é o líquido que o jogador quer receber (G sai do
    inverso da fórmula); sem ele, ou com um valor que pede o título inteiro, resgata tudo.
    """
    iof = iof_rate(days_held)
    ir = income_tax_rate(investment_type, days_held, policy)
    profit_share = (
        max(current_value - total_applied, Decimal(0)) / current_value
        if current_value > 0
        else Decimal(0)
    )

    def taxed(gross: Decimal) -> tuple[Decimal, Decimal, Decimal]:
        yield_amount = gross * profit_share
        iof_amount = (yield_amount * iof).quantize(CENT, ROUND_HALF_EVEN)
        ir_amount = ((yield_amount - iof_amount) * ir).quantize(CENT, ROUND_HALF_EVEN)
        return yield_amount, iof_amount, ir_amount

    yield_amount, iof_amount, ir_amount = taxed(current_value)
    full_net = (current_value - iof_amount - ir_amount).quantize(CENT, ROUND_HALF_EVEN)
    full = RedemptionBreakdown(
        gross=current_value,
        yield_amount=yield_amount,
        iof=iof_amount,
        income_tax=ir_amount,
        net=full_net,
        remaining=Decimal(0),
    )
    if net_wanted is None or net_wanted >= full_net:
        return full

    tax_share = profit_share * (iof + ir - ir * iof)
    gross = net_wanted / (1 - tax_share)
    yield_amount, iof_amount, ir_amount = taxed(gross)
    # O caixa recebe o líquido pedido ao centavo; o título entrega ele mais os impostos
    gross = net_wanted + iof_amount + ir_amount
    return RedemptionBreakdown(
        gross=gross,
        yield_amount=gross * profit_share,
        iof=iof_amount,
        income_tax=ir_amount,
        net=net_wanted,
        remaining=current_value - gross,
    )


@dataclass(frozen=True)
class TaxDrop:
    """Dia em que o IR passa para a próxima faixa, e a alíquota dessa faixa."""

    on: date
    rate: Decimal


def next_tax_drop(
    investment_type: FixedIncomeType,
    first_applied: date,
    today: date,
    policy: TaxPolicy = DEFAULT_TAX_POLICY,
) -> TaxDrop | None:
    """A próxima queda do IR; None quando já está na alíquota final ou o título é isento."""
    if investment_type in (FixedIncomeType.LCI, FixedIncomeType.LCA):
        return None

    days_held = (today - first_applied).days
    brackets = policy.fixed_income_brackets
    rates = [rate for _, rate in brackets] + [policy.fixed_income_floor]
    for (max_days, _), next_rate in zip(brackets, rates[1:], strict=True):
        if days_held <= max_days:
            return TaxDrop(
                on=first_applied + timedelta(days=max_days + 1), rate=next_rate
            )
    return None


def iof_free_date(first_applied: date, today: date) -> date | None:
    """Primeiro dia sem IOF; None quando o prazo de 30 dias já passou."""
    free_on = first_applied + timedelta(days=IOF_FREE_DAYS)
    return free_on if today < free_on else None


def project(
    asset: FixedIncomeAssetDTO,
    amount: Decimal,
    on: date,
    policy: TaxPolicy = DEFAULT_TAX_POLICY,
) -> FixedIncomeProjectionDTO:
    """
    Projeta `amount` aplicado em `on` até o resgate, com o indexador congelado no
    último valor conhecido em `on`. O primeiro dia que rende é o tick seguinte à
    compra, e o último é o dia do resgate — igual ao jogo ao vivo.
    """
    index_rate = index_rate_on(asset.rate_index, on)
    annual_rate = effective_annual_rate(asset, index_rate)
    redeem_on = redemption_date(asset.maturity_date)

    series = INDEX_SERIES.get(asset.rate_index)
    frozen = None if series is None else last_known_value(series, on)

    def frozen_rate(day: date) -> Decimal | None:
        if series is None:
            return Decimal(0)
        return None if frozen is None else daily_rate(series, frozen, day)

    # `gross_amount` cresce a partir de `amount`; `growth`, a partir de 1 (percentuais)
    gross_amount = amount
    growth = Decimal(1)
    business_days = 0
    previous, day = on, next_business_day(on)
    while day <= redeem_on:
        factor = daily_factor(asset, frozen_rate(previous))
        gross_amount *= factor
        growth *= factor
        business_days += 1
        previous, day = day, next_business_day(day)

    days_held = (redeem_on - on).days
    tax_rate = income_tax_rate(asset.investment_type, days_held, policy)
    gross_return = gross_amount - amount
    # Os impostos do resgate são IR e, em título que vence antes de 30 dias, o IOF
    net_amount = redemption_breakdown(
        gross_amount, amount, asset.investment_type, days_held, None, policy
    ).net
    gross_return_pct = growth - 1
    taxes = gross_amount - net_amount
    taxes_pct = taxes / amount if amount > 0 else gross_return_pct * tax_rate

    return FixedIncomeProjectionDTO(
        amount=amount,
        index_rate=index_rate,
        effective_annual_rate=annual_rate,
        business_days=business_days,
        redemption_date=redeem_on,
        gross_amount=gross_amount,
        gross_return=gross_return,
        gross_return_pct=gross_return_pct,
        income_tax_rate=tax_rate,
        income_tax=taxes,
        income_tax_pct=taxes_pct,
        net_amount=net_amount,
        net_return=net_amount - amount,
        net_return_pct=gross_return_pct - taxes_pct,
    )


def offer(
    asset: FixedIncomeAssetDTO, on: date, policy: TaxPolicy = DEFAULT_TAX_POLICY
) -> FixedIncomeOfferDTO:
    """O título com a taxa equivalente de `on` e a alíquota de IR se levado ao vencimento."""
    index_rate = index_rate_on(asset.rate_index, on)
    return FixedIncomeOfferDTO(
        **asset.model_dump(),
        index_rate=index_rate,
        effective_annual_rate=effective_annual_rate(asset, index_rate),
        tax_exempt=asset.investment_type in (FixedIncomeType.LCI, FixedIncomeType.LCA)
        and policy.lci_lca_rate == 0,
        income_tax_rate_at_maturity=income_tax_rate(
            asset.investment_type,
            (redemption_date(asset.maturity_date) - on).days,
            policy,
        ),
    )


def income_tax_brackets(
    policy: TaxPolicy = DEFAULT_TAX_POLICY,
) -> list[IncomeTaxBracketDTO]:
    """A tabela regressiva inteira, da primeira faixa à alíquota final."""
    return [
        *(
            IncomeTaxBracketDTO(max_days=days, rate=rate)
            for days, rate in policy.fixed_income_brackets
        ),
        IncomeTaxBracketDTO(max_days=None, rate=policy.fixed_income_floor),
    ]
