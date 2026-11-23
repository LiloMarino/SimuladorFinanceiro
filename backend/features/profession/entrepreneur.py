"""
A mecânica do Empreendedor: salvar a fração reinvestida, vender parte da empresa, o
pagamento do mês e a política dos bots. Só funções do estado, do dia e da economia.
"""

from datetime import date
from decimal import Decimal
from typing import cast

from backend.core.dto.profession import (
    EntrepreneurAction,
    EntrepreneurState,
    MechanicAction,
    MechanicState,
    SellCapital,
    SetReinvestShare,
)
from backend.core.entrepreneur import (
    BOT_RECESSION_QUARTERS,
    BOT_REINVEST_SHARE,
    CAPITAL_HISTORY_MONTHS,
    REINVEST_STEP,
    after_payment,
    negative_quarters,
    sale_part,
    sale_proceeds,
    sale_share_valid,
)
from backend.core.exceptions.http_exceptions import ConflictError
from backend.features.economy.growth import MacroMonth


def apply_entrepreneur(
    state: MechanicState, action: MechanicAction, day: date, macro: MacroMonth
) -> EntrepreneurState:
    """Salva a fração reinvestida ou vende parte do capital, recusando o que o estado ou as opções não permitem."""
    state = cast(EntrepreneurState, state)
    action = cast(EntrepreneurAction, action)
    if isinstance(action, SellCapital):
        return sell_capital(state, action)
    return set_reinvest_share(state, cast(SetReinvestShare, action))


def set_reinvest_share(
    state: EntrepreneurState, action: SetReinvestShare
) -> EntrepreneurState:
    """Salva a fração do lucro reinvestida, de 0% a 100% em passos de 1%; vale a partir do próximo pagamento."""
    share = action.share
    if not 0 <= share <= 1 or share % REINVEST_STEP != 0:
        raise ConflictError("A fração reinvestida vai de 0% a 100%, em passos de 1%.")
    return state.model_copy(update={"reinvest_share": share})


def sell_capital(state: EntrepreneurState, action: SellCapital) -> EntrepreneurState:
    """Tira do capital a fração vendida; o que entra no caixa é `sale_payout`."""
    if not sale_share_valid(action.share):
        raise ConflictError("Venda 10%, 25%, 50% ou 100% do capital da empresa.")
    if state.capital <= 0:
        raise ConflictError("A empresa ainda não tem capital para vender.")
    part = sale_part(state.capital, action.share)
    return state.model_copy(update={"capital": state.capital - part})


def sale_payout(state: EntrepreneurState, share: Decimal) -> Decimal:
    """O que entra no caixa com a venda de `share` do capital do estado, com o desconto da venda."""
    return sale_proceeds(sale_part(state.capital, share))


def pay_month(
    state: EntrepreneurState, growth: Decimal, profit: Decimal
) -> tuple[EntrepreneurState, Decimal, Decimal]:
    """
    O pagamento do mês: o estado com o capital novo, a parte do lucro que sai do caixa
    para o capital e o rendimento positivo que entra no caixa (zero com rendimento
    negativo). O estado guarda o capital que havia antes do pagamento, até os últimos
    pagamentos que o bloco compara.
    """
    capital, reinvested, income = after_payment(
        state.capital, growth, profit, state.reinvest_share
    )
    history = [*state.capital_history, state.capital][-CAPITAL_HISTORY_MONTHS:]
    paid = state.model_copy(update={"capital": capital, "capital_history": history})
    return paid, reinvested, max(income, Decimal(0))


def capital_months_ago(state: EntrepreneurState) -> Decimal | None:
    """O capital de 3 meses atrás, quando o estado já guarda os 3 pagamentos; nulo antes disso."""
    if len(state.capital_history) < CAPITAL_HISTORY_MONTHS:
        return None
    return state.capital_history[0]


def policy_reinvest_share(growth: Decimal, neutral: Decimal) -> Decimal:
    """A fração do bot: reinveste 30% com o PIB de 12 meses acima do neutro e nada abaixo."""
    return BOT_REINVEST_SHARE if growth > neutral else Decimal(0)


def policy_sale_due(state: EntrepreneurState, quarters: list[Decimal]) -> bool:
    """O bot vende na recessão de dois trimestres negativos seguidos, uma vez por recessão, e só com capital."""
    return (
        state.capital > 0
        and not state.recession_sold
        and negative_quarters(quarters) >= BOT_RECESSION_QUARTERS
    )


def policy_recession_flag(
    state: EntrepreneurState, quarters: list[Decimal], sold: bool
) -> EntrepreneurState:
    """O estado com a marca da recessão: ligada pela venda e desligada quando o último trimestre não é negativo."""
    flag = sold or (state.recession_sold and negative_quarters(quarters) > 0)
    return (
        state
        if flag == state.recession_sold
        else state.model_copy(update={"recession_sold": flag})
    )
