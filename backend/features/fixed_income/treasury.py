"""
Tesouro Direto: o catálogo fixo de seis títulos, a curva de taxas e o preço a mercado.

A regra não guarda estado: o catálogo, as taxas e o histórico de qualquer mês saem de
SELIC, IPCA, do prêmio de risco do país e da data de largada da partida. A taxa de um
título é uma curva do prazo (em anos), medido no dia 1º do mês corrente; o prêmio
entra somado à taxa base.
"""

import calendar
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from uuid import NAMESPACE_URL, UUID, uuid5

from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.enum import FixedIncomeType, IndicatorSeries, RateIndexType
from backend.core.indicators import BUSINESS_DAYS_PER_YEAR, annual_index_rate
from backend.core.utils import business_days_between, last_day_of_month
from backend.features.fixed_income.accrual import (
    effective_annual_rate,
    redemption_date,
)

ISSUER = "Tesouro Nacional"
DAYS_PER_YEAR = Decimal("365.25")

# Curva de taxa por prazo `anos`, em fração ao ano (0.001 = 0,10 ponto)
SELIC_SPREAD = Decimal("0.001")
PREFIXED_DISCOUNT = Decimal("0.01")
PREFIXED_SLOPE = Decimal("0.0015")
IPCA_SLOPE = Decimal("0.001")

# Faixas do risco do país pela dívida ÷ PIB: o limite superior de cada uma
DEBT_BAND_LIMITS = (Decimal("0.5"), Decimal("0.8"), Decimal("1"))
BAND_NAMES = ("Sem prêmio", "Moderado", "Alto", "Crítico")


@dataclass(frozen=True)
class Step:
    """Um degrau do catálogo: o prazo-alvo, o vencimento de data fixa e o piso que dispara a troca."""

    rate_index: RateIndexType
    target_years: int
    maturity_month: int
    maturity_day: int
    floor_years: int


STEPS: tuple[Step, ...] = (
    Step(RateIndexType.SELIC, 3, 3, 1, 2),
    Step(RateIndexType.PREFIXADO, 3, 1, 1, 2),
    Step(RateIndexType.PREFIXADO, 7, 1, 1, 5),
    Step(RateIndexType.IPCA, 5, 5, 15, 3),
    Step(RateIndexType.IPCA, 10, 5, 15, 7),
    Step(RateIndexType.IPCA, 20, 5, 15, 15),
)

TITLE_LABELS: dict[RateIndexType, str] = {
    RateIndexType.SELIC: "Selic",
    RateIndexType.PREFIXADO: "Prefixado",
    RateIndexType.IPCA: "IPCA+",
}


def title_name(rate_index: RateIndexType, maturity: date) -> str:
    return f"Tesouro {TITLE_LABELS[rate_index]} {maturity.year}"


def years_between(start: date, maturity: date) -> Decimal:
    """O prazo em anos de `start` até `maturity`; vencido vale 0."""
    return max(Decimal((maturity - start).days) / DAYS_PER_YEAR, Decimal(0))


def month_start(day: date) -> date:
    return day.replace(day=1)


# ---------------------------------------------------------------- curva de taxas


def base_rate(
    rate_index: RateIndexType, years: Decimal, selic: Decimal, ipca: Decimal
) -> Decimal:
    """
    A taxa base do título, antes do prêmio, na forma que `interest_rate` guarda:
    spread sobre a SELIC, taxa prefixada ou spread real sobre o IPCA.
    """
    match rate_index:
        case RateIndexType.SELIC:
            return SELIC_SPREAD
        case RateIndexType.PREFIXADO:
            return selic - PREFIXED_DISCOUNT + PREFIXED_SLOPE * years
        case RateIndexType.IPCA:
            return selic - ipca + IPCA_SLOPE * years
        case _:
            raise ValueError(f"{rate_index} não existe no Tesouro")


@dataclass(frozen=True)
class MarketRates:
    """SELIC e IPCA (12 meses) que valem no dia."""

    selic: Decimal
    ipca: Decimal

    @classmethod
    def on(cls, day: date) -> "MarketRates":
        return cls(
            selic=annual_index_rate(IndicatorSeries.SELIC, day),
            ipca=annual_index_rate(IndicatorSeries.IPCA, day),
        )

    def index(self, rate_index: RateIndexType) -> Decimal:
        match rate_index:
            case RateIndexType.SELIC:
                return self.selic
            case RateIndexType.IPCA:
                return self.ipca
            case _:
                return Decimal(0)


def rate_on(
    rate_index: RateIndexType, maturity: date, day: date, premium: Decimal
) -> Decimal:
    """
    A taxa que o Tesouro paga em `day` por um título de qualquer vencimento (base mais
    prêmio). Vale o mês de `day`: prazo, SELIC e IPCA do dia 1º. Serve também aos
    títulos antigos, de vencimento sorteado.
    """
    first = month_start(day)
    rates = MarketRates.on(first)
    years = years_between(first, maturity)
    return base_rate(rate_index, years, rates.selic, rates.ipca) + premium


# ---------------------------------------------------------------- preço a mercado


def mark_factor(asset: FixedIncomeAssetDTO, today: date, premium: Decimal) -> Decimal:
    """
    Quanto o preço de mercado vale da curva: ((1 + r_compra) / (1 + r_hoje)) ^ (du / 252).

    No Prefixado r é a taxa cheia e no IPCA+ só o spread real. A Selic e tudo o que não
    é do Tesouro valem o que acumularam: fator 1.
    """
    if (
        asset.investment_type is not FixedIncomeType.TESOURO_DIRETO
        or asset.rate_index is RateIndexType.SELIC
    ):
        return Decimal(1)

    business_days_left = business_days_between(
        today, redemption_date(asset.maturity_date)
    )
    if business_days_left <= 0:
        return Decimal(1)

    today_rate = rate_on(asset.rate_index, asset.maturity_date, today, premium)
    return ((1 + asset.interest_rate) / (1 + today_rate)) ** (
        Decimal(business_days_left) / BUSINESS_DAYS_PER_YEAR
    )


# ---------------------------------------------------------------- catálogo


def _maturity_from(step: Step, on: date, minimum_years: int) -> date:
    """O menor vencimento de data fixa do degrau com prazo, a partir de `on`, de pelo menos `minimum_years`."""
    year = on.year
    while True:
        candidate = date(year, step.maturity_month, step.maturity_day)
        if years_between(on, candidate) >= minimum_years:
            return candidate
        year += 1


def maturity_on(step: Step, start: date, on: date) -> date:
    """
    O vencimento que o degrau tem em `on`. Na largada, o menor com prazo >= alvo; a cada
    fechamento de dezembro, se o prazo em 1º de janeiro seguinte cai abaixo do piso, o
    degrau passa ao próximo título com prazo >= alvo.
    """
    current = _maturity_from(step, month_start(start), step.target_years)
    for year in range(start.year, on.year):
        new_year = date(year + 1, 1, 1)
        if years_between(new_year, current) < step.floor_years:
            current = _maturity_from(step, new_year, step.target_years)
    return current


def sold_until(step: Step, maturity: date, on: date) -> date:
    """31 de dezembro do ano em que o título sai da vitrine: o primeiro fechamento que o deixa abaixo do piso."""
    year = on.year
    while years_between(date(year + 1, 1, 1), maturity) >= step.floor_years:
        year += 1
    return date(year, 12, 31)


@dataclass(frozen=True)
class TreasuryTitle:
    """Um título do catálogo num mês."""

    step: Step
    maturity: date
    name: str
    sold_until: date
    # O título que entra no lugar quando a troca é no próximo dezembro; None se ele fica mais tempo
    replacement_maturity: date | None

    @property
    def rate_index(self) -> RateIndexType:
        return self.step.rate_index

    @property
    def replacement_name(self) -> str | None:
        if self.replacement_maturity is None:
            return None
        return title_name(self.rate_index, self.replacement_maturity)


def catalog(start: date, on: date) -> list[TreasuryTitle]:
    """Os seis títulos à venda no mês de `on`, iguais em qualquer momento da partida."""
    first = month_start(on)
    titles: list[TreasuryTitle] = []
    for step in STEPS:
        maturity = maturity_on(step, start, first)
        leaves = sold_until(step, maturity, first)
        replacement = (
            _maturity_from(step, date(leaves.year + 1, 1, 1), step.target_years)
            if leaves.year == first.year
            else None
        )
        titles.append(
            TreasuryTitle(
                step=step,
                maturity=maturity,
                name=title_name(step.rate_index, maturity),
                sold_until=leaves,
                replacement_maturity=replacement,
            )
        )
    return titles


# ---------------------------------------------------------------- emissão


def issue_uuid(
    simulation_id: int, rate_index: RateIndexType, maturity: date, first: date
) -> UUID:
    """O mesmo título no mesmo mês é sempre o mesmo UUID: a retomada mostra a mesma oferta."""
    key = f"treasury/{simulation_id}/{rate_index.name}/{maturity}/{first:%Y-%m}"
    return uuid5(NAMESPACE_URL, key)


def issue(
    simulation_id: int, start: date, on: date, premium: Decimal
) -> dict[str, FixedIncomeAssetDTO]:
    """
    Os títulos do mês de `on`, cada um com a taxa travada (base mais `premium`). A oferta
    vale até o fim do mês: o mês seguinte traz a taxa revista.
    """
    first = month_start(on)
    rates = MarketRates.on(first)
    until = first.replace(day=calendar.monthrange(first.year, first.month)[1])
    issued: dict[str, FixedIncomeAssetDTO] = {}
    for title in catalog(start, first):
        years = years_between(first, title.maturity)
        base = base_rate(title.rate_index, years, rates.selic, rates.ipca)
        asset = FixedIncomeAssetDTO(
            asset_uuid=issue_uuid(
                simulation_id, title.rate_index, title.maturity, first
            ),
            name=title.name,
            issuer=ISSUER,
            investment_type=FixedIncomeType.TESOURO_DIRETO,
            rate_index=title.rate_index,
            maturity_date=title.maturity,
            interest_rate=base + premium,
            offered_until=until,
            risk_premium=premium if premium > 0 else None,
        )
        issued[str(asset.asset_uuid)] = asset
    return issued


# ---------------------------------------------------------------- histórico e termômetro


@dataclass(frozen=True)
class TitleQuote:
    """A taxa de um título do catálogo num mês: base, prêmio e o quanto rende ao ano."""

    title: TreasuryTitle
    base: Decimal
    premium: Decimal
    effective: Decimal

    @property
    def rate(self) -> Decimal:
        return self.base + self.premium


def quote(
    title: TreasuryTitle, first: date, rates: MarketRates, premium: Decimal
) -> TitleQuote:
    """A cotação de `title` no mês que começa em `first`; `effective` é o "equivale hoje"."""
    base = base_rate(
        title.rate_index, years_between(first, title.maturity), rates.selic, rates.ipca
    )
    asset = FixedIncomeAssetDTO(
        name=title.name,
        issuer=ISSUER,
        investment_type=FixedIncomeType.TESOURO_DIRETO,
        rate_index=title.rate_index,
        maturity_date=title.maturity,
        interest_rate=base + premium,
    )
    return TitleQuote(
        title=title,
        base=base,
        premium=premium,
        effective=effective_annual_rate(asset, rates.index(title.rate_index)),
    )


@dataclass(frozen=True)
class MonthPoint:
    """Um mês do histórico: as cotações do catálogo, o prêmio e a dívida ÷ PIB que valiam."""

    first: date
    quotes: list[TitleQuote]
    premium: Decimal
    # None sem a expansão do governo, que não tem dívida
    debt: Decimal | None


def history(
    start: date,
    until: date,
    premium_on: Callable[[date], Decimal],
    debt_on: Callable[[date], Decimal] | None,
) -> list[MonthPoint]:
    """Um ponto por mês, do mês da largada ao mês de `until`, recalculado da regra."""
    points: list[MonthPoint] = []
    first = month_start(start)
    while first <= until:
        premium = premium_on(first)
        rates = MarketRates.on(first)
        points.append(
            MonthPoint(
                first=first,
                quotes=[
                    quote(title, first, rates, premium)
                    for title in catalog(start, first)
                ],
                premium=premium,
                debt=None if debt_on is None else debt_on(first),
            )
        )
        first = last_day_of_month(first) + timedelta(days=1)
    return points


def band_index(debt: Decimal) -> int:
    """A faixa do risco pela dívida ÷ PIB: 0 sem prêmio (até 50%), 1 moderado, 2 alto, 3 crítico (acima de 100%)."""
    for index, limit in enumerate(DEBT_BAND_LIMITS):
        if debt <= limit:
            return index
    return len(DEBT_BAND_LIMITS)
