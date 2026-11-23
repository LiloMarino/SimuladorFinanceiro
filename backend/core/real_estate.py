"""
Os imóveis do Locador: o preço pelo IVG-R, o aluguel de 0,5% reajustado pelo IGP-M a cada
12 meses de contrato, a vacância sorteada por imóvel e as ofertas do mês. Funções puras:
quem guarda os imóveis e move o caixa é a `Simulation`.
"""

import random
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from backend.core.clt import cents
from backend.core.dates import add_months
from backend.core.dto.real_estate import PropertyDraft, PropertyDTO
from backend.core.enum import IndicatorSeries, PropertySize, PropertyStatus
from backend.core.indicators import (
    anniversaries,
    annual_index_rate,
    monthly_index_factor,
)
from backend.core.locked_assets import PROPERTY_COST_RATE
from backend.core.periods import MONTHS_PER_YEAR

# O aluguel inicial é esta fração do preço do dia, ao mês
RENT_RATE = Decimal("0.005")
# ITBI e corretagem, sobre o preço na compra e na venda
TRANSACTION_COST = PROPERTY_COST_RATE
# A venda conclui este tanto de meses depois do pedido
SALE_MONTHS = 1
# A chance de um imóvel vago voltar ao aluguel a cada virada de mês
RERENT_CHANCE = 0.6

# A chance de vacância por imóvel no mês: a base vale com o desemprego neutro, e cada
# ponto de queda do PIB de 12 meses soma um ponto percentual
VACANCY_BASE = Decimal("0.05")
VACANCY_GDP_POINT = Decimal("0.01")
VACANCY_MIN = Decimal("0.02")
VACANCY_MAX = Decimal("0.20")

# O preço da oferta varia até esta fração para cima e para baixo do preço do dia
OFFER_SPREAD = Decimal("0.10")

# O preço de partida de cada tamanho, em múltiplos do salário da sala
PRICE_MULTIPLES: dict[PropertySize, Decimal] = {
    PropertySize.STUDIO: Decimal(30),
    PropertySize.TWO_BEDROOM: Decimal(60),
    PropertySize.HOUSE: Decimal(100),
}

# O imóvel comprado leva o nome do tamanho
OFFER_NAMES: dict[PropertySize, str] = {
    PropertySize.STUDIO: "Kitnet",
    PropertySize.TWO_BEDROOM: "Apartamento 2 quartos",
    PropertySize.HOUSE: "Casa 3 quartos",
}

# Os imóveis de quem começa Locador: o aluguel de cada um é a sua parte (2:3:4) do
# múltiplo do salário que a profissão rende
INITIAL_PROPERTIES: tuple[tuple[PropertySize, str, int], ...] = (
    (PropertySize.STUDIO, "Apartamento 1 quarto", 2),
    (PropertySize.TWO_BEDROOM, "Apartamento 2 quartos", 3),
    (PropertySize.HOUSE, "Casa 3 quartos", 4),
)


@dataclass(frozen=True)
class Offer:
    """A oferta do mês para um tamanho: o preço do dia com a variação sorteada."""

    size: PropertySize
    price: Decimal

    @property
    def rent(self) -> Decimal:
        return rent_of(self.price)

    @property
    def cost(self) -> Decimal:
        return transaction_cost(self.price)


def rent_of(price: Decimal) -> Decimal:
    """O aluguel inicial de um imóvel que vale `price`."""
    return cents(price * RENT_RATE)


def transaction_cost(price: Decimal) -> Decimal:
    """O custo de transação (ITBI e corretagem) sobre `price`."""
    return cents(price * TRANSACTION_COST)


def price_factor(start: date, day: date) -> Decimal:
    """Quanto o preço dos imóveis subiu entre o início da partida e `day`, pelo IVG-R."""
    return monthly_index_factor(IndicatorSeries.IVG_R, start, day)


def contract_rent_on(
    contract_rent: Decimal, contract_start: date, day: date
) -> Decimal:
    """O aluguel em vigor em `day`: o do contrato, reajustado pelo IGP-M de 12 meses a cada aniversário dele."""
    rent = contract_rent
    for anniversary in anniversaries(contract_start, day):
        rent *= 1 + annual_index_rate(IndicatorSeries.IGP_M, anniversary)
    return cents(rent)


def next_readjustment(contract_start: date, day: date) -> date:
    """O próximo aniversário do contrato depois de `day`, em que o aluguel se reajusta."""
    years = len(anniversaries(contract_start, day)) + 1
    return add_months(contract_start, years * MONTHS_PER_YEAR)


def vacancy_chance(unemployment_ratio: Decimal, gdp_growth: Decimal) -> Decimal:
    """
    A chance de um imóvel ficar vago no mês: 5% com o desemprego neutro, escalada pelo
    desemprego da partida sobre o neutro, mais 1 ponto percentual por ponto de queda do
    PIB de 12 meses (PIB positivo não soma nem tira), entre 2% e 20%.
    """
    fall = max(-gdp_growth, Decimal(0))
    chance = VACANCY_BASE * unemployment_ratio + fall * VACANCY_GDP_POINT * 100
    return min(max(chance, VACANCY_MIN), VACANCY_MAX)


def becomes_vacant(
    seed: int, user_id: int, month: date, property_id: int, chance: Decimal
) -> bool:
    """O sorteio de vacância do imóvel na virada de `month`: a semente é da sala, do jogador, do mês e do imóvel, e a retomada sorteia igual."""
    key = f"{seed}:{user_id}:{month.isoformat()}:{property_id}:vacancy"
    return random.Random(key).random() < float(chance)


def is_rented_again(seed: int, user_id: int, month: date, property_id: int) -> bool:
    """O sorteio da volta ao aluguel do imóvel vago na virada de `month`."""
    key = f"{seed}:{user_id}:{month.isoformat()}:{property_id}:rerent"
    return random.Random(key).random() < RERENT_CHANCE


def offer_price(
    seed: int, month: date, size: PropertySize, price_today: Decimal
) -> Decimal:
    """O preço da oferta do mês para o tamanho: o do dia com a variação de até 10%, igual para todos os jogadores da sala."""
    key = f"{seed}:{month.isoformat()}:{size.value}:offer"
    spread = Decimal(str(random.Random(key).uniform(-1, 1))) * OFFER_SPREAD
    return cents(price_today * (1 + spread))


def offers_of(
    seed: int, month: date, room_salary: Decimal, start: date, day: date
) -> list[Offer]:
    """As 3 ofertas do mês, uma de cada tamanho, pelo preço do dia."""
    factor = price_factor(start, day)
    return [
        Offer(
            size,
            offer_price(seed, month, size, room_salary * multiple * factor),
        )
        for size, multiple in PRICE_MULTIPLES.items()
    ]


def value_of(item: PropertyDTO, start: date, day: date) -> Decimal:
    """O valor do imóvel em `day`: o preço base da partida corrido pelo IVG-R."""
    return cents(item.base_price * price_factor(start, day))


def rent_on(item: PropertyDTO, day: date) -> Decimal:
    """O aluguel que o imóvel paga em `day`: o do contrato reajustado pelo IGP-M; o vago não paga."""
    if item.status is PropertyStatus.VACANT:
        return Decimal(0)
    return contract_rent_on(item.contract_rent, item.contract_start, day)


def initial_drafts(
    room_salary: Decimal, income_multiple: Decimal, start: date, day: date
) -> list[PropertyDraft]:
    """
    Os 3 imóveis de quem começa Locador, todos alugados: o aluguel de cada um é a sua
    parte (2:3:4) de `income_multiple` salários da sala, e o preço base é o que rende
    0,5% ao mês naquele aluguel. Nascidos depois do início da partida, o contrato abre
    pelo preço do dia.
    """
    shares = sum(share for _, _, share in INITIAL_PROPERTIES)
    factor = price_factor(start, day)
    drafts: list[PropertyDraft] = []
    for size, name, share in INITIAL_PROPERTIES:
        rent = room_salary * income_multiple * share / shares
        base_price = cents(rent / RENT_RATE)
        drafts.append(
            PropertyDraft(
                size=size,
                name=name,
                base_price=base_price,
                offer_month=None,
                contract_rent=rent_of(base_price * factor),
                contract_start=day,
            )
        )
    return drafts


def bought_draft(offer: Offer, month: date, start: date, day: date) -> PropertyDraft:
    """O imóvel que a compra da oferta traz: o preço da oferta vira preço base da partida e o contrato abre hoje, a 0,5% do preço."""
    return PropertyDraft(
        size=offer.size,
        name=OFFER_NAMES[offer.size],
        base_price=cents(offer.price / price_factor(start, day)),
        offer_month=month,
        contract_rent=offer.rent,
        contract_start=day,
    )


def sale_proceeds(value: Decimal) -> Decimal:
    """O que a venda deixa no caixa: o valor do dia de conclusão menos o custo de transação."""
    return value - transaction_cost(value)
