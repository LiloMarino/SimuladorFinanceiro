"""
Os imóveis do Locador no dia: o bloco da página e a política do bot. Só funções do dia,
dos imóveis e das ofertas que a `Simulation` entrega.
"""

from collections.abc import Sequence
from datetime import date
from decimal import Decimal

from backend.core.dates import add_months
from backend.core.dto.profession_page import (
    LandlordMechanicDTO,
    LandlordPropertyDTO,
    PropertyOfferDTO,
)
from backend.core.dto.real_estate import PropertyDTO
from backend.core.enum import MechanicStatus, PropertySize, PropertyStatus
from backend.core.periods import MONTHS_PER_YEAR
from backend.core.real_estate import (
    RENT_RATE,
    SALE_MONTHS,
    TRANSACTION_COST,
    Offer,
    next_readjustment,
    rent_of,
    rent_on,
    value_of,
)
from backend.features.profession.reserve import Reserve

# O Locador-bot compra quando o aluguel inicial rende mais que o CDI menos esta folga, e vende quando o aluguel de 12 meses do imóvel rende menos que o CDI menos esta distância
BUY_MARGIN = Decimal("0.02")
SELL_MARGIN = Decimal("0.05")


def next_offers_on(day: date) -> date:
    """O dia em que saem as ofertas do mês seguinte: o dia 1."""
    return add_months(day.replace(day=1), 1)


def bought_sizes(items: Sequence[PropertyDTO], month: date) -> set[PropertySize]:
    """Os tamanhos de que o jogador já comprou a oferta do mês."""
    return {item.size for item in items if item.offer_month == month}


def annual_yield(rent: Decimal, value: Decimal) -> Decimal | None:
    """O aluguel mensal `rent` em 12 meses sobre o valor `value`; nulo sem valor."""
    if value <= 0:
        return None
    return rent * MONTHS_PER_YEAR / value


def _months_vacant(since: date, day: date) -> int:
    months = (day.year - since.year) * MONTHS_PER_YEAR + day.month - since.month
    return max(months, 1)


def property_row(item: PropertyDTO, start: date, day: date) -> LandlordPropertyDTO:
    value = value_of(item, start, day)
    vacant = item.status is PropertyStatus.VACANT
    return LandlordPropertyDTO(
        id=item.id,
        name=item.name,
        size=item.size,
        value=value,
        status=item.status,
        rent=None if vacant else rent_on(item, day),
        next_readjustment=None
        if vacant
        else next_readjustment(item.contract_start, day),
        vacant_months=(
            _months_vacant(item.vacant_since, day)
            if vacant and item.vacant_since is not None
            else None
        ),
        rerent=rent_of(value) if vacant else None,
        sale_due=item.sale_due,
    )


def landlord_block(
    items: Sequence[PropertyDTO],
    offers: Sequence[Offer],
    start: date,
    day: date,
    cdi: Decimal,
    vacancy_chance: Decimal,
) -> LandlordMechanicDTO:
    """
    O bloco do Locador: os imóveis com valor, aluguel e situação, o rendimento do aluguel
    contra o CDI, a chance de vacância e as 3 ofertas do mês, cada uma marcada quando o
    jogador já a comprou.
    """
    rows = [property_row(item, start, day) for item in items]
    month = day.replace(day=1)
    bought = bought_sizes(items, month)
    income = sum((row.rent or Decimal(0) for row in rows), Decimal(0))
    full_income = sum(
        (
            row.rent if row.rent is not None else row.rerent or Decimal(0)
            for row in rows
        ),
        Decimal(0),
    )
    total_value = sum((row.value for row in rows), Decimal(0))
    return LandlordMechanicDTO(
        status=MechanicStatus.ACTIVE if rows else MechanicStatus.AVAILABLE,
        income=income,
        rented=sum(1 for row in rows if row.status is not PropertyStatus.VACANT),
        total=len(rows),
        annual_yield=annual_yield(income, total_value),
        full_yield=annual_yield(full_income, total_value),
        cdi=cdi,
        vacancy_chance=vacancy_chance,
        properties=rows,
        total_value=total_value,
        offers_month=month,
        next_offers_on=next_offers_on(day),
        offers=[
            PropertyOfferDTO(
                size=offer.size,
                price=offer.price,
                rent=offer.rent,
                cost=offer.cost,
                bought=offer.size in bought,
            )
            for offer in offers
        ],
        rent_rate=RENT_RATE,
        cost_rate=TRANSACTION_COST,
        sale_months=SALE_MONTHS,
    )


def policy_purchase(
    offers: Sequence[Offer],
    bought: set[PropertySize],
    cdi: Decimal,
    cash: Decimal,
    reserve: Reserve,
) -> Offer | None:
    """
    A oferta que o Locador-bot compra no mês: com o aluguel inicial (6% ao ano) acima do
    CDI menos a folga, a maior que o caixa paga com o preço, o custo de compra e a reserva
    de saúde ainda de pé; nula quando nada compensa ou cabe.
    """
    if cdi - BUY_MARGIN >= RENT_RATE * MONTHS_PER_YEAR:
        return None
    affordable = [
        offer
        for offer in offers
        if offer.size not in bought
        and cash - offer.price - offer.cost >= reserve.health_cost
    ]
    return max(affordable, key=lambda offer: offer.price, default=None)


def policy_sales(
    items: Sequence[PropertyDTO], start: date, day: date, cdi: Decimal
) -> list[int]:
    """Os imóveis que o Locador-bot põe à venda: o aluguel de 12 meses sobre o valor de hoje abaixo do CDI menos a distância; o vago e o já à venda ficam de fora."""
    sales: list[int] = []
    for item in items:
        if item.status is not PropertyStatus.RENTED:
            continue
        rate = annual_yield(rent_on(item, day), value_of(item, start, day))
        if rate is not None and rate < cdi - SELL_MARGIN:
            sales.append(item.id)
    return sales
