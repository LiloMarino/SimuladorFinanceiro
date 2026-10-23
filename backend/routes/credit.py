from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from backend.core.dependencies import ActiveSimulation, ClientID
from backend.core.dto.credit import (
    ContractLoanRequestDTO,
    CreditOverviewDTO,
    LoanQuoteDTO,
    PrepayLoanRequestDTO,
    PrepaymentPreviewDTO,
)

credit_router = APIRouter(prefix="/api/credit", tags=["Credit"])


@credit_router.get(
    "",
    response_model=CreditOverviewDTO,
    summary="Obter o crédito",
    description="Retorna a dívida, a nota de risco, a oferta de empréstimo, os empréstimos, as próximas parcelas, o histórico de 12 meses e as sugestões para subir a nota.",
)
def get_credit(simulation: ActiveSimulation, client_id: ClientID):
    return simulation.get_credit(client_id)


@credit_router.get(
    "/quote",
    response_model=LoanQuoteDTO,
    summary="Simular um empréstimo",
    description="Calcula parcela, juro no prazo, cronograma completo, alavancagem antes e depois, a nota projetada e quanto passa do limite.",
)
def quote_loan(
    simulation: ActiveSimulation,
    client_id: ClientID,
    amount: Annotated[Decimal, Query(gt=0)],
    term_months: Annotated[int, Query()],
):
    return simulation.quote_loan(client_id, amount, term_months)


@credit_router.post(
    "/loans",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Contratar um empréstimo",
    description="Assina o empréstimo com o juro da nota de hoje, travado até o fim, e credita o valor no caixa.",
)
def contract_loan(
    simulation: ActiveSimulation,
    client_id: ClientID,
    payload: ContractLoanRequestDTO,
):
    simulation.contract_loan(client_id, payload.amount, payload.term_months)


@credit_router.get(
    "/loans/{loan_id}/prepayment",
    response_model=PrepaymentPreviewDTO,
    summary="Prévia de pagar antes",
    description="Mostra as duas formas de amortizar (diminuir o prazo ou a parcela) com o juro economizado de cada uma, e o que custa quitar tudo hoje.",
)
def preview_prepayment(
    simulation: ActiveSimulation,
    client_id: ClientID,
    loan_id: UUID,
    amount: Annotated[Decimal, Query(ge=0)] = Decimal(0),
):
    return simulation.preview_prepayment(client_id, loan_id, amount)


@credit_router.post(
    "/loans/{loan_id}/prepayment",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Amortizar um empréstimo",
    description="Paga uma parte do saldo devedor agora e diminui o prazo ou a parcela.",
)
def prepay_loan(
    simulation: ActiveSimulation,
    client_id: ClientID,
    loan_id: UUID,
    payload: PrepayLoanRequestDTO,
):
    simulation.prepay_loan(client_id, loan_id, payload.amount, payload.mode)


@credit_router.post(
    "/loans/{loan_id}/payoff",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Quitar um empréstimo",
    description="Paga o saldo devedor do dia, sem os juros que ainda não correram.",
)
def payoff_loan(simulation: ActiveSimulation, client_id: ClientID, loan_id: UUID):
    simulation.payoff_loan(client_id, loan_id)


@credit_router.post(
    "/loans/{loan_id}/overdue",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Pagar a parcela em atraso",
    description="Paga as parcelas em atraso do empréstimo com a multa de 2% e a mora até hoje.",
)
def pay_overdue(simulation: ActiveSimulation, client_id: ClientID, loan_id: UUID):
    simulation.pay_overdue(client_id, loan_id)
