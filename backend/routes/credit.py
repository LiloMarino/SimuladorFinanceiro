from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from backend.core.dto.credit import (
    ContractLoanRequestDTO,
    CreditOverviewDTO,
    LoanQuoteDTO,
    PayrollLoanDTO,
    PayrollQuoteDTO,
    PrepayLoanRequestDTO,
    PrepaymentPreviewDTO,
)
from backend.routes.dependencies import ActingClient, ActiveSimulation, CurrentUser

credit_router = APIRouter(prefix="/api/credit", tags=["Credit"])


@credit_router.get(
    "",
    response_model=CreditOverviewDTO,
    summary="Obter o crédito",
    description="Retorna a dívida, a nota de risco, a oferta de empréstimo, os empréstimos, as próximas parcelas, o histórico de 12 meses e as sugestões para subir a nota.",
)
def get_credit(simulation: ActiveSimulation, user: CurrentUser, acting: ActingClient):
    return simulation.get_credit(user, acting)


@credit_router.get(
    "/quote",
    response_model=LoanQuoteDTO,
    summary="Simular um empréstimo",
    description="Calcula parcela, juro no prazo, cronograma completo, alavancagem antes e depois, a nota projetada e quanto passa do limite.",
)
def quote_loan(
    simulation: ActiveSimulation,
    user: CurrentUser,
    acting: ActingClient,
    amount: Annotated[Decimal, Query(gt=0)],
    term_months: Annotated[int, Query()],
):
    return simulation.quote_loan(user, acting, amount, term_months)


@credit_router.post(
    "/loans",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Contratar um empréstimo",
    description="Assina o empréstimo com o juro da nota de hoje, travado até o fim, e credita o valor no caixa.",
)
def contract_loan(
    simulation: ActiveSimulation,
    user: CurrentUser,
    acting: ActingClient,
    payload: ContractLoanRequestDTO,
):
    simulation.contract_loan(user, acting, payload.amount, payload.term_months)


@credit_router.get(
    "/payroll/quote",
    response_model=PayrollQuoteDTO,
    summary="Simular um consignado",
    description="Só para o Servidor, na conta pessoal. Calcula parcela, juro no prazo, a margem consignável (35% do salário líquido do mês) livre e o maior valor que ela sustenta no prazo.",
)
def quote_payroll(
    simulation: ActiveSimulation,
    user: CurrentUser,
    acting: ActingClient,
    amount: Annotated[Decimal, Query(gt=0)],
    term_months: Annotated[int, Query()],
):
    return simulation.quote_payroll(user, acting, amount, term_months)


@credit_router.post(
    "/payroll",
    response_model=PayrollLoanDTO,
    summary="Contratar um consignado",
    description="Assina o consignado com a SELIC do dia mais 2 pontos ao ano, travados até o fim, e credita o valor no caixa. A parcela sai do salário na virada do mês, a partir da primeira virada que vem 30 dias ou mais depois do contrato. Quitar e amortizar usam as rotas dos empréstimos, com o id devolvido.",
)
def contract_payroll(
    simulation: ActiveSimulation,
    user: CurrentUser,
    acting: ActingClient,
    payload: ContractLoanRequestDTO,
):
    return simulation.contract_payroll(
        user, acting, payload.amount, payload.term_months
    )


@credit_router.get(
    "/loans/{loan_id}/prepayment",
    response_model=PrepaymentPreviewDTO,
    summary="Prévia de pagar antes",
    description="Mostra as duas formas de amortizar (diminuir o prazo ou a parcela) com o juro economizado de cada uma, e o que custa quitar tudo hoje.",
)
def preview_prepayment(
    simulation: ActiveSimulation,
    user: CurrentUser,
    acting: ActingClient,
    loan_id: UUID,
    amount: Annotated[Decimal, Query(ge=0)] = Decimal(0),
):
    return simulation.preview_prepayment(user, acting, loan_id, amount)


@credit_router.post(
    "/loans/{loan_id}/prepayment",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Amortizar um empréstimo",
    description="Paga uma parte do saldo devedor agora e diminui o prazo ou a parcela.",
)
def prepay_loan(
    simulation: ActiveSimulation,
    user: CurrentUser,
    acting: ActingClient,
    loan_id: UUID,
    payload: PrepayLoanRequestDTO,
):
    simulation.prepay_loan(user, acting, loan_id, payload.amount, payload.mode)


@credit_router.post(
    "/loans/{loan_id}/payoff",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Quitar um empréstimo",
    description="Paga o saldo devedor do dia, sem os juros que ainda não correram.",
)
def payoff_loan(
    simulation: ActiveSimulation, user: CurrentUser, acting: ActingClient, loan_id: UUID
):
    simulation.payoff_loan(user, acting, loan_id)


@credit_router.post(
    "/loans/{loan_id}/overdue",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Pagar a parcela em atraso",
    description="Paga as parcelas em atraso do empréstimo com a multa de 2% e a mora até hoje.",
)
def pay_overdue(
    simulation: ActiveSimulation, user: CurrentUser, acting: ActingClient, loan_id: UUID
):
    simulation.pay_overdue(user, acting, loan_id)
