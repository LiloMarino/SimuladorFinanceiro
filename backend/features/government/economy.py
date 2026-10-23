"""Contrafactual versionado: efeitos sobre a série, sem reescrever o histórico."""

import math
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from backend.core import repository
from backend.core.dto.government import (
    CompanyProfileDTO,
    GovernmentStateDTO,
    PolicyDTO,
    ProductExposureDTO,
)

PRODUCTS = {
    "STEEL": "Aço",
    "OIL": "Petróleo e combustíveis",
    "FOOD": "Alimentos",
    "TECH": "Tecnologia",
}
POLICIES = {
    "COMMON_TAX": "IR comum da renda variável",
    "DAY_TRADE_TAX": "IR de day trade",
    "FII_TAX": "IR dos FIIs",
    "STOCK_EXEMPTION": "Limite de isenção de ações",
    "FIXED_TAX_SHIFT": "Ajuste da tabela de renda fixa",
    "LCI_TAX": "IR de LCI e LCA",
    "SECTOR_TAX": "Ajuste do IR por setor ou segmento",
    "PRODUCT_TARIFF": "Tarifa de importação por produto",
    "PUBLIC_SPENDING": "Investimento público",
}


def state_on(simulation_id: int, day: date) -> GovernmentStateDTO | None:
    if simulation_id == 0 or simulation_id not in repository.government._enabled:
        return None
    return next(
        (
            s
            for s in reversed(repository.government.states(simulation_id))
            if s.processed_on <= day
        ),
        None,
    )


def active_policies(state: GovernmentStateDTO, on: date) -> list[PolicyDTO]:
    latest: dict[tuple[str, str], PolicyDTO] = {}
    spending: list[PolicyDTO] = []
    for p in sorted(state.policies, key=lambda p: (p.effective_on or date.max, p.id)):
        if p.status != "approved" or p.effective_on is None or p.effective_on > on:
            continue
        if p.kind == "PUBLIC_SPENDING":
            spending.append(p)
        else:
            latest[(p.kind, p.target)] = p
    return [*latest.values(), *spending]


def scenario_profile(
    ticker: str, sector: str | None, segment: str | None
) -> CompanyProfileDTO:
    """Perfis demonstrativos por setor, identificados como hipóteses em toda prévia."""
    text = f"{sector or ''} {segment or ''}".casefold()
    exposures: list[ProductExposureDTO] = []
    if any(t in text for t in ("material", "metal", "sider", "minera")):
        exposures.append(
            ProductExposureDTO(
                product="STEEL", revenue_share=0.65, imported_cost_share=0.08
            )
        )
    elif any(t in text for t in ("industr", "constru", "transporte", "veícul")):
        exposures.append(
            ProductExposureDTO(
                product="STEEL", revenue_share=0.05, imported_cost_share=0.35
            )
        )
    if any(t in text for t in ("petróleo", "combust", "gás")):
        exposures.append(
            ProductExposureDTO(
                product="OIL", revenue_share=0.70, imported_cost_share=0.15
            )
        )
    elif any(t in text for t in ("transporte", "logística", "aéreo")):
        exposures.append(
            ProductExposureDTO(product="OIL", revenue_share=0, imported_cost_share=0.30)
        )
    if any(t in text for t in ("alimento", "agro", "bebida")):
        exposures.append(
            ProductExposureDTO(
                product="FOOD", revenue_share=0.65, imported_cost_share=0.12
            )
        )
    if any(t in text for t in ("tecnologia", "comput", "eletrôn")):
        exposures.append(
            ProductExposureDTO(
                product="TECH", revenue_share=0.25, imported_cost_share=0.50
            )
        )
    return CompanyProfileDTO(
        ticker=ticker, sector=sector, segment=segment, exposures=exposures
    )


@dataclass(frozen=True)
class MacroEffect:
    inflation: float = 0
    selic: float = 0


def macro_effect(state: GovernmentStateDTO | None, on: date) -> MacroEffect:
    if state is None:
        return MacroEffect()
    inflation = 0.0
    for p in active_policies(state, on):
        if p.kind == "PUBLIC_SPENDING" and p.effective_on:
            age = (on - p.effective_on).days - 30
            if age >= 0:
                inflation += (
                    float(p.value)
                    / 100_000_000
                    * state.rules.spending_inflation
                    * 0.5 ** (age / 365)
                )
    decisions = [d for d in state.selic_decisions if d.on <= on]
    if state.rules.manual_selic and decisions:
        # A reação inflacionária tem 90 dias de atraso; taxa baixa aquece e alta esfria.
        for d in reversed(decisions):
            if d.on + timedelta(days=90) <= on:
                inflation += (d.baseline - d.rate) * state.rules.monetary_inflation
                break
        delta = decisions[-1].rate - decisions[-1].baseline
    else:
        delta = 1.5 * max(-0.10, min(0.50, inflation))
    return MacroEffect(inflation=max(-0.10, min(0.50, inflation)), selic=delta)


def company_effect(
    state: GovernmentStateDTO | None, ticker: str, on: date
) -> tuple[float, float, float]:
    if state is None:
        return 1, 0, 0
    company = next((c for c in state.rules.companies if c.ticker == ticker), None)
    product = 0.0
    if company:
        for policy in active_policies(state, on):
            if policy.kind == "PRODUCT_TARIFF":
                for exposure in company.exposures:
                    if exposure.product == policy.target:
                        tariff = float(policy.value)
                        revenue = (
                            exposure.revenue_share
                            * exposure.domestic_competition
                            * tariff
                        )
                        cost = (
                            exposure.imported_cost_share
                            * tariff
                            * (1 - exposure.pass_through)
                        )
                        # 20% da variação do lucro operacional entra na avaliação da ação.
                        product += 0.20 * (revenue - cost) / company.margin
            elif policy.kind == "PUBLIC_SPENDING" and policy.effective_on:
                age = max(0, (on - policy.effective_on).days)
                product += (
                    0.005 * float(policy.value) / 100_000_000 * 0.5 ** (age / 365)
                )
    monetary = -2.9 * macro_effect(state, on).selic * (company.beta if company else 1)
    return max(0.10, min(3, 1 + product + monetary)), product, monetary


def tax_value(
    state: GovernmentStateDTO | None,
    on: date,
    kind: str,
    default: Decimal,
    target: str = "",
) -> Decimal:
    if state:
        for p in active_policies(state, on):
            if p.kind == kind and p.target == target:
                return p.value
    return default


def campaign_gain(spent: Decimal, scale: Decimal) -> float:
    return math.sqrt(float(max(Decimal(0), spent) / scale)) * 1.4
