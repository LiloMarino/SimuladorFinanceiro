from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from backend.core import repository
from backend.core.dto.events.credit import CreditEventDTO
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.enum import (
    CreditEventType,
    CreditGrade,
    IndicatorSeries,
    PrepaymentMode,
)
from backend.core.exceptions import InsufficentCashError
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.indicators import annual_index_rate
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.user_manager import UserManager
from backend.core.utils import next_business_day
from backend.core.utils.lazy_dict import LazyDict
from backend.features.credit.loan import LoanState
from backend.features.credit.price import (
    ZERO,
    OverdueCharges,
    money,
    overdue_charges,
)
from backend.features.credit.rating import (
    RatingScore,
    count_recent_late,
    leverage,
    leverage_points,
    payment_points,
    volatility_points,
)
from backend.features.credit.rules import (
    FIXED_INCOME_MARGIN,
    MAX_TERM_MONTHS,
    MIN_TERM_MONTHS,
    WARNING_DAYS,
    GradeTier,
    tier_of,
)
from backend.features.fixed_income.accrual import offer as fixed_income_offer
from backend.features.realtime import notify
from backend.features.realtime.schemas import (
    CreditInstallmentLateEventDTO,
    CreditInstallmentPaidEventDTO,
    CreditInstallmentWarningEventDTO,
    CreditLoanPaidOffEventDTO,
    CreditMonthlySummaryEventDTO,
    CreditRatingChangedEventDTO,
)
from backend.features.statistics.risk import (
    ROLLING_WINDOW,
    annual_volatility,
    daily_returns,
)

if TYPE_CHECKING:
    from backend.features.simulation.simulation_engine import SimulationEngine

logger = logging.getLogger(__name__)

# Avisos de cada parcela só nas velocidades em que dá para ler; acima vira resumo do mês
PER_INSTALLMENT_NOTICE_MAX_SPEED = 2
MONTHLY_SUMMARY_MIN_SPEED = 4


@dataclass
class Overdue:
    number: int
    due_date: date
    amount: Decimal

    def charges(self, today: date) -> OverdueCharges:
        return overdue_charges(self.amount, self.due_date, today)


@dataclass
class Loan:
    loan_id: UUID
    # "Empréstimo N": a ordem em que o jogador contratou
    number: int
    principal: Decimal
    term_months: int
    grade: CreditGrade
    state: LoanState
    overdue: list[Overdue] = field(default_factory=list)

    @property
    def contract_date(self) -> date:
        return self.state.contract_date

    @property
    def annual_rate(self) -> Decimal:
        return self.state.annual_rate

    @property
    def total_installments(self) -> int:
        return self.state.cycles_done + self.state.remaining

    @property
    def paid_installments(self) -> int:
        return self.state.cycles_done - len(self.overdue)

    @property
    def is_settled(self) -> bool:
        return self.state.is_closed and not self.overdue

    def balance_on(self, day: date) -> Decimal:
        """Saldo do dia: o ciclo corrente mais as parcelas em atraso (sem multa nem mora)."""
        return self.state.balance_on(day) + sum((o.amount for o in self.overdue), ZERO)

    def charges_on(self, day: date) -> Decimal:
        """Multa e mora das parcelas em atraso."""
        total = ZERO
        for overdue in self.overdue:
            charges = overdue.charges(day)
            total += charges.fee + charges.interest
        return total

    def debt_on(self, day: date) -> Decimal:
        return self.balance_on(day) + self.charges_on(day)

    def payoff_on(self, day: date) -> Decimal:
        """O que zera o empréstimo hoje: o saldo do dia e o atraso com multa e mora."""
        return money(self.debt_on(day))


@dataclass
class ClosedRating:
    """A alavancagem e a volatilidade do último fechamento mensal."""

    leverage: Decimal
    volatility: Decimal | None
    sample_size: int
    leverage_points: Decimal
    volatility_points: Decimal


@dataclass
class ClientCredit:
    loans: dict[UUID, Loan] = field(default_factory=dict)
    # Todos os eventos do jogador, na ordem em que aconteceram
    events: list[CreditEventDTO] = field(default_factory=list)
    contracts: int = 0
    rating: ClosedRating | None = None
    # A nota que o jogador viu por último, para avisar só quando a nota muda
    seen: RatingScore | None = None
    # A nota e os pontos de antes da última mudança
    previous: RatingScore | None = None
    warned: set[tuple[UUID, int]] = field(default_factory=set)

    @property
    def closed_loans(self) -> int:
        return self.contracts - len(self.loans)

    def late_dates(self) -> list[date]:
        return [
            e.event_date
            for e in self.events
            if e.event_type is CreditEventType.INSTALLMENT_LATE
        ]

    def apply(self, event: CreditEventDTO) -> None:
        """
        Aplica um evento ao estado: cada parcela (paga ou atrasada) avança o ciclo,
        a amortização abate o saldo do dia do evento e a quitação encerra o empréstimo.
        """
        self.events.append(event)
        loan = self.loans.get(event.loan_id)
        match event.event_type:
            case CreditEventType.CONTRACT:
                assert event.annual_rate is not None and event.term_months is not None
                assert event.grade is not None
                self.contracts += 1
                self.loans[event.loan_id] = Loan(
                    loan_id=event.loan_id,
                    number=self.contracts,
                    principal=event.amount,
                    term_months=event.term_months,
                    grade=event.grade,
                    state=LoanState.sign(
                        event.event_date,
                        event.amount,
                        event.annual_rate,
                        event.term_months,
                    ),
                )
            case CreditEventType.INSTALLMENT_PAID if loan:
                loan.state = loan.state.advance()
            case CreditEventType.INSTALLMENT_LATE if loan:
                number = loan.state.next_number
                due = loan.state.next_due
                loan.overdue.append(Overdue(number, due, event.amount))
                loan.state = loan.state.advance()
            case CreditEventType.OVERDUE_PAID if loan:
                loan.overdue = [
                    o for o in loan.overdue if o.number != event.installment_number
                ]
            case CreditEventType.PREPAYMENT if loan:
                assert event.prepayment_mode is not None
                loan.state = loan.state.prepay(
                    event.amount, event.event_date, event.prepayment_mode
                )
            case CreditEventType.PAYOFF if loan:
                loan.state = loan.state.close()
                loan.overdue = []
        if loan and loan.is_settled:
            del self.loans[loan.loan_id]


@dataclass(frozen=True)
class Offer:
    selic: Decimal
    tier: GradeTier
    score: RatingScore
    annual_rate: Decimal | None
    best_fixed_income_rate: Decimal | None
    max_amount: Decimal
    debt_limit_amount: Decimal


def close_rating(history: list[PatrimonialHistoryDTO], day: date) -> ClosedRating:
    """O fechamento do mês: alavancagem do último snapshot e volatilidade dos últimos pregões."""
    month_start = day.replace(day=1)
    closed = [p for p in history if p.snapshot_date < month_start]
    if not closed:
        return ClosedRating(
            ZERO, None, 0, leverage_points(ZERO), volatility_points(None, 0)
        )
    last = closed[-1]
    value = leverage(last.total_debt, last.total_networth)
    returns = [r for _, r in daily_returns(closed)][-ROLLING_WINDOW:]
    volatility = annual_volatility(returns)
    return ClosedRating(
        leverage=value,
        volatility=volatility,
        sample_size=len(returns),
        leverage_points=leverage_points(value),
        volatility_points=volatility_points(volatility, len(returns)),
    )


def replay(events: list[CreditEventDTO]) -> ClientCredit:
    """
    Reconstrói os empréstimos a partir dos eventos, na ordem em que aconteceram.
    """
    client = ClientCredit()
    for event in events:
        client.apply(event)
    return client


class CreditBook:
    """
    Empréstimos dos jogadores: contratação, parcelas no vencimento, amortização,
    quitação, atraso e a nota de risco.

    O estado vive em memória, reconstruído dos eventos de crédito na primeira
    consulta (como a renda fixa). Toda operação roda sob o lock do motor e grava
    o evento de crédito junto do movimento de caixa.
    """

    def __init__(
        self,
        engine: SimulationEngine,
        lock: threading.RLock,
        history: Callable[[UUID], list[PatrimonialHistoryDTO]] | None = None,
    ):
        self._engine = engine
        self._lock = lock
        self._history = history or (
            lambda client_id: repository.portfolio.get_patrimonial_history(
                UserManager.get_user_id(client_id)
            )
        )
        self._clients: LazyDict[UUID, ClientCredit] = LazyDict(self._load)

    def _load(self, client_id: UUID) -> ClientCredit:
        events = repository.credit.get_events(
            self._engine.simulation_id, UserManager.get_user_id(client_id)
        )
        client = replay(events)
        client.rating = self.closing(client_id, self._engine.current_date)
        client.seen = self._score(client, self._engine.current_date)
        return client

    def client(self, client_id: UUID) -> ClientCredit:
        with self._lock:
            return self._clients[client_id]

    def forget(self, client_id: UUID) -> None:
        self._clients.pop(client_id, None)

    # ------------------------------------------------------------------ leitura

    def debt(self, client_id: UUID, day: date) -> Decimal:
        """Saldo devedor do jogador no dia, com multa e mora."""
        client = self.client(client_id)
        return sum((loan.debt_on(day) for loan in client.loans.values()), ZERO)

    def loans(self, client_id: UUID) -> list[Loan]:
        return sorted(self.client(client_id).loans.values(), key=lambda x: x.number)

    def loan(self, client_id: UUID, loan_id: UUID) -> Loan:
        loan = self.client(client_id).loans.get(loan_id)
        if loan is None:
            raise NotFoundError("Esse empréstimo não existe ou já foi quitado.")
        return loan

    def score(self, client_id: UUID, day: date) -> RatingScore:
        return self._score(self.client(client_id), day)

    def _score(self, client: ClientCredit, day: date) -> RatingScore:
        closed = client.rating
        late = count_recent_late(client.late_dates(), day)
        return RatingScore(
            leverage_points=closed.leverage_points if closed else leverage_points(ZERO),
            volatility_points=(
                closed.volatility_points if closed else volatility_points(None, 0)
            ),
            payment_points=payment_points(late),
        )

    def history(self, client_id: UUID) -> list[PatrimonialHistoryDTO]:
        return self._history(client_id)

    def assets_value(self, client_id: UUID) -> Decimal:
        return self._engine.assets_value(client_id)

    def cash(self, client_id: UUID) -> Decimal:
        return self._engine.get_cash(client_id)

    def best_fixed_income_rate(self, day: date) -> Decimal | None:
        """Maior taxa anual efetiva entre os títulos de renda fixa à venda hoje."""
        rates = [
            rate
            for asset in self._engine.fixed_income_market.get_available_assets()
            if (rate := fixed_income_offer(asset, day).effective_annual_rate)
            is not None
        ]
        return max(rates, default=None)

    def offer(self, client_id: UUID, day: date) -> Offer:
        """
        Juro e limite que a nota de hoje dá: o juro é o maior entre SELIC + spread
        e a renda fixa mais cara do dia mais a margem; o limite é a fração do
        patrimônio líquido que a dívida pode chegar a ser.
        """
        score = self.score(client_id, day)
        tier = tier_of(score.grade)
        selic = annual_index_rate(IndicatorSeries.SELIC, day)
        best = self.best_fixed_income_rate(day)
        debt = self.debt(client_id, day)
        networth = self._engine.assets_value(client_id) - debt
        limit_amount = max(tier.debt_limit * networth, ZERO)
        if tier.spread is None:
            return Offer(selic, tier, score, None, best, ZERO, limit_amount)
        rate = selic + tier.spread
        if best is not None:
            rate = max(rate, best + FIXED_INCOME_MARGIN)
        return Offer(
            selic, tier, score, rate, best, max(limit_amount - debt, ZERO), limit_amount
        )

    def alert(self, client_id: UUID, day: date) -> bool:
        """Parcela em atraso, ou parcela dentro do aviso sem caixa para cobri-la."""
        client = self.client(client_id)
        if any(loan.overdue for loan in client.loans.values()):
            return True
        return self._shortfall(client_id, client, day) > 0

    def _due_soon(self, client: ClientCredit, day: date) -> list[tuple[Loan, Decimal]]:
        limit = day + timedelta(days=WARNING_DAYS)
        return [
            (loan, loan.state.due_amount())
            for loan in client.loans.values()
            if not loan.state.is_closed and loan.state.next_due <= limit
        ]

    def _shortfall(self, client_id: UUID, client: ClientCredit, day: date) -> Decimal:
        due = sum((amount for _, amount in self._due_soon(client, day)), ZERO)
        return max(due - self._engine.get_cash(client_id), ZERO)

    # ------------------------------------------------------------------ nota

    def closing(self, client_id: UUID, day: date) -> ClosedRating:
        return close_rating(self._history(client_id), day)

    def close_month(self, client_ids: list[UUID], day: date) -> None:
        """Na virada do mês a alavancagem e a volatilidade do mês que fechou valem para a nota."""
        for client_id in client_ids:
            with self._lock:
                client = self._clients[client_id]
                client.rating = self.closing(client_id, day)
                client.previous = None
                self._announce_grade(client_id, client, day)

    def _announce_grade(self, client_id: UUID, client: ClientCredit, day: date) -> None:
        score = self._score(client, day)
        seen, client.seen = client.seen, score
        if seen is None or seen.grade is score.grade:
            return
        client.previous = seen
        if not client.events:
            return
        tier = tier_of(score.grade)
        notify(
            "credit_rating_changed",
            CreditRatingChangedEventDTO(
                before=seen.grade,
                after=score.grade,
                points=score.points,
                spread=tier.spread,
                debt_limit=tier.debt_limit,
            ).to_json(),
            to=client_id,
        )

    # ------------------------------------------------------------------ vencimentos

    def process_due(self, client_ids: list[UUID], day: date, speed: int) -> None:
        """
        Debita a parcela que vence no dia (o primeiro pregão em ou depois da data).
        Sem caixa, a parcela vira atraso: nada é vendido e o cheque especial não a cobre.
        """
        for client_id in client_ids:
            with self._lock:
                client = self._clients[client_id]
                for loan in list(client.loans.values()):
                    self._settle_due(client_id, client, loan, day, speed)
                self._warn(client_id, client, day)
                self._announce_grade(client_id, client, day)

    def _settle_due(
        self,
        client_id: UUID,
        client: ClientCredit,
        loan: Loan,
        day: date,
        speed: int,
    ) -> None:
        while not loan.state.is_closed and day >= loan.state.next_due:
            amount = loan.state.due_amount()
            number = loan.state.next_number
            if self._engine.get_cash(client_id) >= amount:
                self._engine.pay_loan(client_id, amount)
                self._record(
                    client,
                    client_id,
                    loan,
                    CreditEventType.INSTALLMENT_PAID,
                    amount,
                    number,
                )
                total = loan.total_installments
                loan.state = loan.state.advance()
                if speed <= PER_INSTALLMENT_NOTICE_MAX_SPEED:
                    notify(
                        "credit_installment_paid",
                        CreditInstallmentPaidEventDTO(
                            loan_number=loan.number,
                            installment_number=number,
                            total_installments=total,
                            amount=amount,
                        ).to_json(),
                        to=client_id,
                    )
            else:
                due = loan.state.next_due
                self._record(
                    client,
                    client_id,
                    loan,
                    CreditEventType.INSTALLMENT_LATE,
                    amount,
                    number,
                )
                loan.overdue.append(Overdue(number, due, amount))
                loan.state = loan.state.advance()
                notify(
                    "credit_installment_late",
                    CreditInstallmentLateEventDTO(
                        loan_id=loan.loan_id,
                        loan_number=loan.number,
                        installment_number=number,
                        due_date=due,
                        amount=amount,
                    ).to_json(),
                    to=client_id,
                )
        if loan.is_settled:
            del client.loans[loan.loan_id]
            notify(
                "credit_loan_paid_off",
                CreditLoanPaidOffEventDTO(
                    loan_number=loan.number,
                    amount=loan.principal,
                    interest_saved=ZERO,
                ).to_json(),
                to=client_id,
            )

    def _warn(self, client_id: UUID, client: ClientCredit, day: date) -> None:
        """Avisa uma vez por parcela que entrou na janela de 7 dias sem caixa para cobri-la."""
        shortfall = self._shortfall(client_id, client, day)
        if shortfall <= 0:
            return
        for loan, amount in self._due_soon(client, day):
            key = (loan.loan_id, loan.state.next_number)
            if key in client.warned:
                continue
            client.warned.add(key)
            notify(
                "credit_installment_warning",
                CreditInstallmentWarningEventDTO(
                    loan_number=loan.number,
                    due_date=loan.state.next_due,
                    amount=amount,
                    shortfall=shortfall,
                ).to_json(),
                to=client_id,
            )

    def monthly_summary(self, client_ids: list[UUID], day: date, speed: int) -> None:
        """No último pregão do mês, em velocidade alta, um aviso só no lugar de uma parcela por vez."""
        if speed < MONTHLY_SUMMARY_MIN_SPEED:
            return
        if next_business_day(day).month == day.month:
            return
        for client_id in client_ids:
            paid = [
                e
                for e in self.client(client_id).events
                if e.event_type is CreditEventType.INSTALLMENT_PAID
                and (e.event_date.year, e.event_date.month) == (day.year, day.month)
            ]
            if not paid:
                continue
            notify(
                "credit_monthly_summary",
                CreditMonthlySummaryEventDTO(
                    month=day.replace(day=1),
                    installments=len(paid),
                    amount=sum((e.amount for e in paid), ZERO),
                ).to_json(),
                to=client_id,
            )

    # ------------------------------------------------------------------ operações

    def contract(self, client_id: UUID, amount: Decimal, term_months: int) -> Loan:
        if not MIN_TERM_MONTHS <= term_months <= MAX_TERM_MONTHS:
            raise UnprocessableEntityError(
                f"O prazo vai de {MIN_TERM_MONTHS} a {MAX_TERM_MONTHS} meses."
            )
        if amount <= 0:
            raise UnprocessableEntityError(
                "O valor do empréstimo deve ser maior que zero."
            )
        amount = money(amount)
        with self._lock:
            day = self._engine.current_date
            offer = self.offer(client_id, day)
            if offer.annual_rate is None:
                raise ConflictError(
                    "Com a nota D não há crédito novo. Veja como voltar a ter crédito."
                )
            if amount > offer.max_amount:
                raise ConflictError("O valor passa do seu limite de dívida.")
            client = self._clients[client_id]
            client.contracts += 1
            loan = Loan(
                loan_id=uuid4(),
                number=client.contracts,
                principal=amount,
                term_months=term_months,
                grade=offer.tier.grade,
                state=LoanState.sign(day, amount, offer.annual_rate, term_months),
            )
            client.loans[loan.loan_id] = loan
            self._engine.receive_loan(client_id, amount)
            self._record(
                client,
                client_id,
                loan,
                CreditEventType.CONTRACT,
                amount,
                annual_rate=offer.annual_rate,
                term_months=term_months,
                grade=offer.tier.grade,
            )
            return loan

    def prepay(
        self, client_id: UUID, loan_id: UUID, amount: Decimal, mode: PrepaymentMode
    ) -> Loan:
        amount = money(amount)
        with self._lock:
            loan = self.loan(client_id, loan_id)
            day = self._engine.current_date
            if amount <= 0:
                raise UnprocessableEntityError(
                    "O valor da amortização deve ser maior que zero."
                )
            if loan.state.is_closed or amount >= loan.state.balance_on(day):
                raise ConflictError("Esse valor quita o empréstimo: use a quitação.")
            self._require_cash(client_id, amount)
            loan.state = loan.state.prepay(amount, day, mode)
            self._engine.pay_loan(client_id, amount)
            self._record(
                self._clients[client_id],
                client_id,
                loan,
                CreditEventType.PREPAYMENT,
                amount,
                prepayment_mode=mode,
            )
            return loan

    def payoff(self, client_id: UUID, loan_id: UUID) -> Decimal:
        with self._lock:
            loan = self.loan(client_id, loan_id)
            day = self._engine.current_date
            amount = loan.payoff_on(day)
            self._require_cash(client_id, amount)
            remaining = sum((row.payment for row in loan.state.schedule()), ZERO)
            saved = max(remaining - loan.state.balance_on(day), ZERO)
            client = self._clients[client_id]
            self._engine.pay_loan(client_id, amount)
            self._record(client, client_id, loan, CreditEventType.PAYOFF, amount)
            del client.loans[loan_id]
            notify(
                "credit_loan_paid_off",
                CreditLoanPaidOffEventDTO(
                    loan_number=loan.number, amount=amount, interest_saved=saved
                ).to_json(),
                to=client_id,
            )
            self._announce_grade(client_id, client, day)
            return amount

    def pay_overdue(self, client_id: UUID, loan_id: UUID) -> Decimal:
        with self._lock:
            loan = self.loan(client_id, loan_id)
            if not loan.overdue:
                raise ConflictError("Esse empréstimo não tem parcela em atraso.")
            day = self._engine.current_date
            charges = [(o, o.charges(day)) for o in loan.overdue]
            total = sum((c.total for _, c in charges), ZERO)
            self._require_cash(client_id, total)
            client = self._clients[client_id]
            self._engine.pay_loan(client_id, total)
            for overdue, c in charges:
                self._record(
                    client,
                    client_id,
                    loan,
                    CreditEventType.OVERDUE_PAID,
                    c.total,
                    overdue.number,
                )
            loan.overdue = []
            if loan.is_settled:
                del client.loans[loan.loan_id]
            return total

    def _require_cash(self, client_id: UUID, amount: Decimal) -> None:
        if self._engine.get_cash(client_id) < amount:
            raise InsufficentCashError("Saldo insuficiente para pagar esse valor.")

    def _record(
        self,
        client: ClientCredit,
        client_id: UUID,
        loan: Loan,
        event_type: CreditEventType,
        amount: Decimal,
        installment_number: int | None = None,
        *,
        annual_rate: Decimal | None = None,
        term_months: int | None = None,
        grade: CreditGrade | None = None,
        prepayment_mode: PrepaymentMode | None = None,
    ) -> None:
        event = CreditEventDTO(
            simulation_id=self._engine.simulation_id,
            user_id=UserManager.get_user_id(client_id),
            event_date=self._engine.current_date,
            loan_id=loan.loan_id,
            event_type=event_type,
            amount=amount,
            installment_number=installment_number,
            annual_rate=annual_rate,
            term_months=term_months,
            grade=grade,
            prepayment_mode=prepayment_mode,
        )
        client.events.append(event)
        EventManager.push_event(event)
