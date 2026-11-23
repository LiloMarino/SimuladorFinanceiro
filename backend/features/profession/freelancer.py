"""
A mecânica do Autônomo: salvar o preço por atendimento, a regra do mês e o preço da
política dos bots. Só funções do estado, do dia e da economia.
"""

from datetime import date
from decimal import Decimal
from typing import cast

from backend.core.dates import add_months
from backend.core.dto.profession import (
    FreelancerAction,
    FreelancerState,
    MechanicAction,
    MechanicState,
    SetPrice,
)
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.freelancer import (
    BOT_LOW_UNEMPLOYMENT_RAISE,
    BOT_RAISE_MONTHS,
    CENT,
    price_range,
)
from backend.core.utils import format_money
from backend.features.economy.growth import MacroMonth


def next_price_change(state: FreelancerState) -> date | None:
    """O 1º dia do mês seguinte ao do último ajuste; nulo enquanto o primeiro ajuste não aconteceu."""
    if state.price_set_on is None:
        return None
    return add_months(state.price_set_on.replace(day=1), 1)


def price_change_allowed(state: FreelancerState, day: date) -> bool:
    """O preço muda uma vez por mês do calendário; o primeiro ajuste é livre."""
    release = next_price_change(state)
    return release is None or day >= release


def apply_freelancer(
    state: MechanicState, action: MechanicAction, day: date, macro: MacroMonth
) -> FreelancerState:
    """Salva o preço, recusando o que sai da faixa da referência ou cai antes do mês seguinte ao último ajuste."""
    state, action = cast(FreelancerState, state), cast(FreelancerAction, action)
    return set_price(state, cast(SetPrice, action), day)


def set_price(state: FreelancerState, action: SetPrice, day: date) -> FreelancerState:
    """Salva o preço, de -20% a +50% da referência do dia, no máximo uma vez por mês do calendário."""
    price = action.price.quantize(CENT)
    low, high = price_range(action.reference)
    if not low <= price <= high:
        raise ConflictError(
            f"O preço vai de {format_money(low)} a {format_money(high)}: de 20% abaixo a 50% acima da referência do mercado."
        )
    if not price_change_allowed(state, day):
        release = cast(date, next_price_change(state))
        raise ConflictError(
            f"O preço muda uma vez por mês: o próximo ajuste é em {release:%d/%m/%Y}."
        )
    return state.model_copy(update={"price": price, "price_set_on": day})


def price_due(state: FreelancerState, start_date: date, day: date) -> bool:
    """A política do bot reajusta uma vez por ano, a contar do último ajuste ou do início da partida."""
    last = state.price_set_on or start_date
    return day >= add_months(last, BOT_RAISE_MONTHS)


def policy_price(
    price: Decimal, ipca_12m: Decimal, unemployment: Decimal, neutral: Decimal
) -> Decimal:
    """
    O preço do reajuste do bot: o IPCA de 12 meses repassado ao preço, mais 5% quando o
    desemprego do dia está abaixo do neutro e nada quando está acima.
    """
    raise_rate = ipca_12m + (
        BOT_LOW_UNEMPLOYMENT_RAISE if unemployment < neutral else Decimal(0)
    )
    return price * (1 + raise_rate)
