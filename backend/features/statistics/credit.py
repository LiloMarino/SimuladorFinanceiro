"""O crédito de um jogador visto de fora da partida: dívida, nota, atraso e custo do juro."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from backend.core.dto.events.credit import CreditEventDTO
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.enum import CreditEventType, CreditGrade
from backend.core.utils import required
from backend.features.credit.credit_book import ClientCredit, Loan, close_rating
from backend.features.credit.price import ZERO
from backend.features.credit.rating import (
    RatingScore,
    count_recent_late,
    payment_points,
)


@dataclass(frozen=True)
class CreditStanding:
    debt: Decimal
    # Dívida sobre o patrimônio líquido; nulo sem patrimônio para a dívida caber
    leverage: Decimal | None
    grade: CreditGrade
    # Tem parcela em atraso (o "Negativado" do ranking)
    delinquent: bool
    # Quem já contratou: só ele tem custo de dívida para mostrar
    has_borrowed: bool
    interest_paid: Decimal
    paid_installments: int
    late_installments: int
    # Juro anual médio dos empréstimos, pesado pelo saldo devedor de hoje (ou pelo valor contratado, sem dívida aberta)
    cost_of_debt: Decimal | None


def credit_standing(
    events: list[CreditEventDTO], history: list[PatrimonialHistoryDTO]
) -> CreditStanding:
    """Estado do crédito no último dia da série, reconstruído dos eventos."""
    last = history[-1]
    client = ClientCredit()
    interest_paid = ZERO
    # Parte de principal de cada parcela atrasada, que sai do saldo quando ela é paga
    late_principal: dict[tuple[UUID, int], Decimal] = {}
    for event in events:
        loan = client.loans.get(event.loan_id)
        if loan is not None:
            interest_paid += _interest_of(event, loan, late_principal)
        client.apply(event)

    day = last.snapshot_date
    closed = close_rating(history, day)
    late = count_recent_late(client.late_dates(), day)
    score = RatingScore(
        leverage_points=closed.leverage_points,
        volatility_points=closed.volatility_points,
        payment_points=payment_points(late),
    )
    debt = sum((loan.debt_on(day) for loan in client.loans.values()), ZERO)
    leverage = (
        ZERO
        if debt <= 0
        else debt / last.total_networth
        if last.total_networth > 0
        else None
    )
    return CreditStanding(
        debt=debt,
        leverage=leverage,
        grade=score.grade,
        delinquent=any(loan.overdue for loan in client.loans.values()),
        has_borrowed=client.contracts > 0,
        interest_paid=interest_paid,
        paid_installments=sum(
            1
            for e in events
            if e.event_type
            in (CreditEventType.INSTALLMENT_PAID, CreditEventType.OVERDUE_PAID)
        ),
        late_installments=len(client.late_dates()),
        cost_of_debt=_cost_of_debt(events, client, day),
    )


def _interest_of(
    event: CreditEventDTO, loan: Loan, late_principal: dict[tuple[UUID, int], Decimal]
) -> Decimal:
    """
    Juro (e multa) que o pagamento carrega: o valor pago menos o principal que ele
    tira do saldo. A parcela atrasada guarda o principal dela para quando for paga.
    """
    state = loan.state
    match event.event_type:
        case CreditEventType.INSTALLMENT_PAID:
            return event.amount - (state.cycle_balance - state.advance().cycle_balance)
        case CreditEventType.PREPAYMENT:
            after = state.prepay(
                event.amount, event.event_date, required(event.prepayment_mode)
            )
            return event.amount - (state.cycle_balance - after.cycle_balance)
        case CreditEventType.INSTALLMENT_LATE:
            late_principal[(loan.loan_id, state.next_number)] = (
                state.cycle_balance - state.advance().cycle_balance
            )
        case CreditEventType.OVERDUE_PAID:
            key = (loan.loan_id, event.installment_number or 0)
            return event.amount - late_principal.get(key, ZERO)
        case CreditEventType.PAYOFF:
            principal = state.cycle_balance + sum(
                (
                    late_principal.get((loan.loan_id, o.number), ZERO)
                    for o in loan.overdue
                ),
                ZERO,
            )
            return event.amount - principal
    return ZERO


def _cost_of_debt(
    events: list[CreditEventDTO], client: ClientCredit, day: date
) -> Decimal | None:
    open_loans = list(client.loans.values())
    if open_loans:
        weighted = [(loan.annual_rate, loan.debt_on(day)) for loan in open_loans]
    else:
        weighted = [
            (e.annual_rate, e.amount)
            for e in events
            if e.event_type is CreditEventType.CONTRACT and e.annual_rate is not None
        ]
    total = sum((weight for _, weight in weighted), ZERO)
    if total <= 0:
        return None
    return sum((rate * weight for rate, weight in weighted), ZERO) / total
