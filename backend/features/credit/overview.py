"""
Monta o que as rotas do crédito devolvem: a tela, a simulação do empréstimo e a
prévia da amortização. Só lê o `CreditBook`; quem altera estado são as operações dele.
"""

from collections import Counter
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from backend.core.dto.credit import (
    CreditOfferDTO,
    CreditOverviewDTO,
    InstallmentRowDTO,
    LadderTierDTO,
    LoanDTO,
    LoanQuoteDTO,
    MonthPaymentsDTO,
    OverdueDTO,
    PrepaymentOptionDTO,
    PrepaymentPreviewDTO,
    RatingDTO,
    RatingLeverageDTO,
    RatingPaymentsDTO,
    RatingVolatilityDTO,
    SuggestionDTO,
    SuggestionKind,
    UpcomingInstallmentDTO,
)
from backend.core.enum import CreditEventType, CreditGrade, PrepaymentMode
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    UnprocessableEntityError,
)
from backend.features.credit.credit_book import ClientCredit, CreditBook, Loan
from backend.features.credit.loan import LoanState
from backend.features.credit.price import (
    ZERO,
    add_months,
    monthly_rate,
    total_interest,
)
from backend.features.credit.rating import (
    RatingScore,
    count_recent_late,
    leverage,
    leverage_points,
    payment_points,
    payoff_to_next_grade,
    volatility_points,
    volatility_to_next_grade,
)
from backend.features.credit.rules import (
    LADDER,
    LEVERAGE_MAX_POINTS,
    MAX_TERM_MONTHS,
    MIN_TERM_MONTHS,
    PAYMENT_MAX_POINTS,
    VOLATILITY_MAX_POINTS,
    next_tier,
)
from backend.features.statistics.risk import daily_returns

HISTORY_MONTHS = 12
UPCOMING_COUNT = 3
# Menos que isso de histórico e a rentabilidade de 12 meses não existe
MIN_RETURN_SPAN_DAYS = 360


def _month_end(day: date) -> date:
    return add_months(day.replace(day=1), 1) - timedelta(days=1)


def _loan_dto(loan: Loan, day: date) -> LoanDTO:
    state = loan.state
    return LoanDTO(
        id=loan.loan_id,
        number=loan.number,
        principal=loan.principal,
        term_months=loan.term_months,
        annual_rate=loan.annual_rate,
        grade=loan.grade,
        contract_date=loan.contract_date,
        installment=state.installment,
        paid_installments=loan.paid_installments,
        total_installments=loan.total_installments,
        balance=loan.balance_on(day),
        overdue_charges=loan.charges_on(day),
        next_due=None if state.is_closed else state.next_due,
        overdue=[
            OverdueDTO(
                installment_number=o.number,
                due_date=o.due_date,
                days_late=max((day - o.due_date).days, 0),
                installment=o.amount,
                fee=o.charges(day).fee,
                interest=o.charges(day).interest,
                total=o.charges(day).total,
            )
            for o in loan.overdue
        ],
    )


def _upcoming(loans: list[Loan]) -> list[UpcomingInstallmentDTO]:
    rows = [
        UpcomingInstallmentDTO(
            due_date=row.due_date,
            loan_number=loan.number,
            installment_number=row.number,
            total_installments=loan.total_installments,
            amount=row.payment,
        )
        for loan in loans
        for row in loan.state.schedule()[:UPCOMING_COUNT]
    ]
    return sorted(rows, key=lambda r: (r.due_date, r.loan_number))[:UPCOMING_COUNT]


def _history(client: ClientCredit, day: date) -> list[MonthPaymentsDTO]:
    """Os últimos 12 meses, uma célula por mês com as parcelas em dia, pagas com atraso e em aberto."""
    resolved = {
        (e.loan_id, e.installment_number)
        for e in client.events
        if e.event_type is CreditEventType.OVERDUE_PAID
    }
    months = [
        add_months(day.replace(day=1), -i) for i in range(HISTORY_MONTHS - 1, -1, -1)
    ]
    on_time: Counter[date] = Counter()
    paid_late: Counter[date] = Counter()
    late: Counter[date] = Counter()
    for event in client.events:
        month = event.event_date.replace(day=1)
        if event.event_type is CreditEventType.INSTALLMENT_PAID:
            on_time[month] += 1
        elif event.event_type is CreditEventType.INSTALLMENT_LATE:
            if (event.loan_id, event.installment_number) in resolved:
                paid_late[month] += 1
            else:
                late[month] += 1
    return [
        MonthPaymentsDTO(
            month=month,
            on_time=on_time[month],
            paid_late=paid_late[month],
            late=late[month],
        )
        for month in months
    ]


def _interest_saved(loans: list[Loan], amount: Decimal, day: date) -> Decimal:
    """Juro poupado ao quitar `amount` do empréstimo de juro mais alto para o de mais baixo."""
    saved = ZERO
    left = amount
    for loan in sorted(loans, key=lambda x: x.annual_rate, reverse=True):
        if left <= 0:
            break
        balance = loan.state.balance_on(day)
        remaining = sum((row.payment for row in loan.state.schedule()), ZERO)
        if left >= balance:
            saved += remaining - balance
            left -= balance
            continue
        prepaid = loan.state.prepay(left, day, PrepaymentMode.SHORTEN_TERM)
        saved += loan.state.interest_saved(prepaid, left)
        left = ZERO
    return saved


def _suggestions(
    book: CreditBook, client_id: UUID, day: date, debt: Decimal, networth: Decimal
) -> list[SuggestionDTO]:
    score = book.score(client_id, day)
    grade = score.grade
    tier = next_tier(grade)
    loans = book.loans(client_id)
    suggestions: list[SuggestionDTO] = []
    if tier is not None:
        amount = payoff_to_next_grade(score, debt, networth)
        if amount is not None and amount > 0:
            suggestions.append(
                SuggestionDTO(
                    kind=(
                        SuggestionKind.RECOVER
                        if grade is CreditGrade.D
                        else SuggestionKind.PAYOFF
                    ),
                    target_grade=tier.grade,
                    amount=amount,
                    interest_saved=_interest_saved(loans, amount, day),
                    leverage_after=leverage(debt - amount, networth),
                )
            )
        ceiling = volatility_to_next_grade(score)
        closed = book.client(client_id).rating
        if (
            ceiling is not None
            and closed is not None
            and closed.volatility is not None
            and closed.volatility > ceiling
        ):
            suggestions.append(
                SuggestionDTO(
                    kind=SuggestionKind.VOLATILITY,
                    target_grade=tier.grade,
                    volatility=ceiling,
                )
            )
    suggestions.append(SuggestionDTO(kind=SuggestionKind.ON_TIME, target_grade=None))
    return suggestions


def _portfolio_return(book: CreditBook, client_id: UUID, day: date) -> Decimal | None:
    history = book.history(client_id)
    if not history or (day - history[0].snapshot_date).days < MIN_RETURN_SPAN_DAYS:
        return None
    start = day - timedelta(days=365)
    growth = Decimal(1)
    for snapshot_day, daily in daily_returns(history):
        if snapshot_day > start:
            growth *= 1 + daily
    return growth - 1


def _rating(book: CreditBook, client_id: UUID, day: date) -> RatingDTO:
    client = book.client(client_id)
    score = book.score(client_id, day)
    closed = client.rating
    previous = client.previous
    late = count_recent_late(client.late_dates(), day)
    return RatingDTO(
        grade=score.grade,
        points=score.points,
        previous_grade=previous.grade if previous else None,
        previous_points=previous.points if previous else None,
        next_review=_month_end(day),
        leverage=RatingLeverageDTO(
            points=score.leverage_points,
            max_points=LEVERAGE_MAX_POINTS,
            value=closed.leverage if closed else ZERO,
        ),
        volatility=RatingVolatilityDTO(
            points=score.volatility_points,
            max_points=VOLATILITY_MAX_POINTS,
            value=closed.volatility if closed else None,
        ),
        payments=RatingPaymentsDTO(
            points=score.payment_points,
            max_points=PAYMENT_MAX_POINTS,
            late_installments=late,
        ),
        ladder=[
            LadderTierDTO(
                grade=t.grade,
                min_points=t.min_points,
                spread=t.spread,
                debt_limit=t.debt_limit,
            )
            for t in LADDER
        ],
    )


def build_overview(book: CreditBook, client_id: UUID, day: date) -> CreditOverviewDTO:
    client = book.client(client_id)
    loans = book.loans(client_id)
    debt = book.debt(client_id, day)
    assets = book.assets_value(client_id)
    networth = assets - debt
    offer = book.offer(client_id, day)
    cash = book.cash(client_id)

    # As próximas parcelas do mês mais próximo em que alguma vence
    next_dues = [
        (loan.state.next_due, loan.state.due_amount())
        for loan in loans
        if not loan.state.is_closed
    ]
    first_month = min((d for d, _ in next_dues), default=None)
    in_month = [
        (d, a)
        for d, a in next_dues
        if first_month and (d.year, d.month) == (first_month.year, first_month.month)
    ]
    month_total = sum((a for _, a in in_month), ZERO)

    return CreditOverviewDTO(
        debt=debt,
        open_loans=len(loans),
        closed_loans=client.closed_loans,
        networth=networth,
        assets=assets,
        cash=cash,
        leverage=leverage(debt, networth) if networth > 0 else None,
        next_installments_month=first_month.replace(day=1) if first_month else None,
        next_installments_total=month_total,
        next_installments_first=min((d for d, _ in in_month), default=None),
        next_installments_last=max((d for d, _ in in_month), default=None),
        cash_covers_next=cash >= month_total,
        rating=_rating(book, client_id, day),
        offer=CreditOfferDTO(
            available=offer.annual_rate is not None,
            selic=offer.selic,
            spread=offer.tier.spread,
            annual_rate=offer.annual_rate,
            best_fixed_income_rate=offer.best_fixed_income_rate,
            max_amount=offer.max_amount,
            debt_limit=offer.tier.debt_limit,
            debt_limit_amount=offer.debt_limit_amount,
        ),
        loans=[_loan_dto(loan, day) for loan in loans],
        upcoming=_upcoming(loans),
        history=_history(client, day),
        suggestions=_suggestions(book, client_id, day, debt, networth),
        portfolio_return_12m=_portfolio_return(book, client_id, day),
    )


def build_quote(
    book: CreditBook,
    client_id: UUID,
    day: date,
    amount: Decimal,
    term_months: int,
) -> LoanQuoteDTO:
    if not MIN_TERM_MONTHS <= term_months <= MAX_TERM_MONTHS:
        raise UnprocessableEntityError(
            f"O prazo vai de {MIN_TERM_MONTHS} a {MAX_TERM_MONTHS} meses."
        )
    if amount <= 0:
        raise UnprocessableEntityError("O valor do empréstimo deve ser maior que zero.")
    offer = book.offer(client_id, day)
    if offer.annual_rate is None:
        raise ConflictError(
            "Com a nota D não há crédito novo. Veja como voltar a ter crédito."
        )

    state = LoanState.sign(day, amount, offer.annual_rate, term_months)
    rows = state.schedule()
    interest = total_interest(rows, amount)
    debt = book.debt(client_id, day)
    networth = book.assets_value(client_id) - debt
    after = leverage(debt + amount, networth)

    # A nota do fim do mês: a alavancagem com o empréstimo, a volatilidade de hoje
    live = book.closing(client_id, add_months(day.replace(day=1), 1))
    late = count_recent_late(book.client(client_id).late_dates(), day)
    projected = RatingScore(
        leverage_points=leverage_points(after),
        volatility_points=volatility_points(live.volatility, live.sample_size),
        payment_points=payment_points(late),
    )
    return LoanQuoteDTO(
        amount=amount,
        term_months=term_months,
        annual_rate=offer.annual_rate,
        monthly_rate=monthly_rate(offer.annual_rate),
        installment=state.installment,
        total_interest=interest,
        total_paid=amount + interest,
        due_day=day.day,
        schedule=[
            InstallmentRowDTO(
                number=r.number,
                due_date=r.due_date,
                interest=r.interest,
                principal=r.principal,
                payment=r.payment,
                balance=r.balance,
            )
            for r in rows
        ],
        leverage_before=leverage(debt, networth),
        leverage_after=after,
        projected_grade=projected.grade,
        projected_points=projected.points,
        current_debt=debt,
        excess=max(amount - offer.max_amount, ZERO),
        cash_after=book.cash(client_id) + amount,
    )


def build_prepayment_preview(
    book: CreditBook, client_id: UUID, loan_id: UUID, day: date, amount: Decimal
) -> PrepaymentPreviewDTO:
    loan = book.loan(client_id, loan_id)
    state = loan.state
    balance = state.balance_on(day)
    options: dict[PrepaymentMode, PrepaymentOptionDTO | None] = {}
    for mode in PrepaymentMode:
        if state.is_closed or not 0 < amount < balance:
            options[mode] = None
            continue
        prepaid = state.prepay(amount, day, mode)
        options[mode] = PrepaymentOptionDTO(
            mode=mode,
            installments_remaining=prepaid.remaining,
            installment=prepaid.installment,
            interest_saved=state.interest_saved(prepaid, amount),
        )
    remaining = sum((row.payment for row in state.schedule()), ZERO)
    return PrepaymentPreviewDTO(
        balance=balance,
        cash=book.cash(client_id),
        shorten_term=options[PrepaymentMode.SHORTEN_TERM],
        reduce_installment=options[PrepaymentMode.REDUCE_INSTALLMENT],
        payoff_installments=state.remaining,
        payoff_remaining_payments=remaining,
        payoff_interest_saved=max(remaining - balance, ZERO),
        payoff_amount=loan.payoff_on(day),
    )
