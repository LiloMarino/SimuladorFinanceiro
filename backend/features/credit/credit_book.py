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
from backend.core.dto.base import BaseDTO
from backend.core.dto.events.credit import CreditEventDTO
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.pending import PendingDTO
from backend.core.enum import (
    CashflowEventType,
    CreditEventType,
    CreditGrade,
    FixedIncomeType,
    IndicatorSeries,
    PendingType,
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
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.core.utils import format_money, next_business_day, required
from backend.core.utils.lazy_dict import LazyDict
from backend.features.credit.loan import LoanState
from backend.features.credit.price import (
    RATE_STEP,
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
    PAYROLL_MARGIN,
    PAYROLL_SPREAD,
    WARNING_DAYS,
    GradeTier,
    payroll_first_collection,
    tier_of,
)
from backend.features.fixed_income.accrual import offer as fixed_income_offer
from backend.features.notifications import registry
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
from backend.types import Event

if TYPE_CHECKING:
    from backend.features.simulation.simulation_engine import SimulationEngine

logger = logging.getLogger(__name__)

# O histórico patrimonial do jogador; com `last`, só os `last` snapshots antes de `before`
HistoryReader = Callable[[UUID, date | None, int | None], list[PatrimonialHistoryDTO]]

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
class LoanContract:
    """O que todo contrato de empréstimo tem: o valor, o prazo e o estado da tabela Price."""

    loan_id: UUID
    principal: Decimal
    term_months: int
    state: LoanState

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
        return self.state.cycles_done

    @property
    def is_settled(self) -> bool:
        return self.state.is_closed

    def balance_on(self, day: date) -> Decimal:
        """Saldo devedor do dia: o que quitaria o contrato agora."""
        return self.state.balance_on(day)

    def charges_on(self, day: date) -> Decimal:
        """Multa e mora das parcelas em atraso; o contrato sem atraso não tem."""
        return ZERO

    def debt_on(self, day: date) -> Decimal:
        return self.balance_on(day) + self.charges_on(day)

    def payoff_on(self, day: date) -> Decimal:
        """O que zera o contrato hoje: o saldo do dia e o atraso com multa e mora."""
        return money(self.debt_on(day))


@dataclass
class Loan(LoanContract):
    """O empréstimo comum: tem a nota do dia da contratação e a parcela vence, e atrasa, no vencimento."""

    # "Empréstimo N": a ordem em que o jogador contratou
    number: int
    grade: CreditGrade
    overdue: list[Overdue] = field(default_factory=list)

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


@dataclass
class PayrollLoan(LoanContract):
    """O consignado do Servidor: sem nota, a parcela sai do salário na virada do mês e nunca atrasa."""

    def due_for_collection(self, day: date) -> bool:
        """A primeira parcela cai na virada que fecha a carência; dali em diante, uma por virada de mês."""
        if self.state.is_closed:
            return False
        if self.state.cycles_done > 0:
            return True
        return day >= payroll_first_collection(self.contract_date)


@dataclass
class ClosedRating:
    """A alavancagem e a volatilidade do último fechamento mensal."""

    leverage: Decimal | None
    volatility: Decimal | None
    sample_size: int
    leverage_points: Decimal
    volatility_points: Decimal


@dataclass
class ClientCredit:
    loans: dict[UUID, Loan] = field(default_factory=dict)
    # Os consignados ativos: ficam fora de `loans`, que reúne o que vence e atrasa
    payroll: dict[UUID, PayrollLoan] = field(default_factory=dict)
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

    def open_contracts(self) -> list[LoanContract]:
        """Todos os contratos em aberto: os empréstimos comuns e os consignados."""
        return [*self.loans.values(), *self.payroll.values()]

    def contract_of(self, loan_id: UUID) -> LoanContract | None:
        return self.loans.get(loan_id) or self.payroll.get(loan_id)

    def late_dates(self) -> list[date]:
        return [
            e.event_date
            for e in self.events
            if e.event_type is CreditEventType.INSTALLMENT_LATE
        ]

    def open_due_dates(self) -> list[date]:
        """Os vencimentos das parcelas atrasadas que seguem sem pagar."""
        return [o.due_date for loan in self.loans.values() for o in loan.overdue]

    def recent_late(self, day: date) -> int:
        return count_recent_late(self.late_dates(), self.open_due_dates(), day)

    def apply(self, event: CreditEventDTO) -> None:
        """
        Aplica um evento ao estado: cada parcela (paga ou atrasada) avança o ciclo,
        a amortização abate o saldo do dia do evento e a quitação encerra o empréstimo.
        """
        self.events.append(event)
        loan = self.loans.get(event.loan_id)
        payroll = self.payroll.get(event.loan_id)
        match event.event_type:
            case CreditEventType.CONTRACT:
                annual_rate = required(event.annual_rate)
                term_months = required(event.term_months)
                grade = required(event.grade)
                self.contracts += 1
                self.loans[event.loan_id] = Loan(
                    loan_id=event.loan_id,
                    number=self.contracts,
                    principal=event.amount,
                    term_months=term_months,
                    grade=grade,
                    state=LoanState.sign(
                        event.event_date,
                        event.amount,
                        annual_rate,
                        term_months,
                    ),
                )
            case CreditEventType.PAYROLL_CONTRACT:
                term_months = required(event.term_months)
                self.payroll[event.loan_id] = PayrollLoan(
                    loan_id=event.loan_id,
                    principal=event.amount,
                    term_months=term_months,
                    state=LoanState.sign(
                        event.event_date,
                        event.amount,
                        required(event.annual_rate),
                        term_months,
                    ),
                )
            case CreditEventType.INSTALLMENT_PAID if loan:
                loan.state = loan.state.advance()
            case CreditEventType.PAYROLL_INSTALLMENT if payroll:
                payroll.state = payroll.state.advance()
            case CreditEventType.INSTALLMENT_LATE if loan:
                number = loan.state.next_number
                due = loan.state.next_due
                loan.overdue.append(Overdue(number, due, event.amount))
                loan.state = loan.state.advance()
            case CreditEventType.OVERDUE_PAID if loan:
                loan.overdue = [
                    o for o in loan.overdue if o.number != event.installment_number
                ]
            case CreditEventType.PREPAYMENT if contract := loan or payroll:
                contract.state = contract.state.prepay(
                    event.amount, event.event_date, required(event.prepayment_mode)
                )
            case CreditEventType.PAYOFF if contract := loan or payroll:
                contract.state = contract.state.close()
                if loan:
                    loan.overdue = []
        if loan and loan.is_settled:
            del self.loans[loan.loan_id]
        if payroll and payroll.is_settled:
            del self.payroll[payroll.loan_id]


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
        history: HistoryReader | None = None,
    ):
        self._engine = engine
        self._lock = lock
        self._history = history or self._stored_history
        self._clients: LazyDict[UUID, ClientCredit] = LazyDict(self._load)
        # Chamado com a conta cujo crédito mudou: o dono do livro leva o panorama novo à tela
        self.on_changed: Callable[[UUID], None] | None = None

    def _stored_history(
        self, client_id: UUID, before: date | None, last: int | None
    ) -> list[PatrimonialHistoryDTO]:
        """O histórico gravado da conta: os snapshots do jogador ou os fechamentos da gestora."""
        portfolio_id = UserManager.get_portfolio_id(client_id)
        if SimulationManager.find_fund_portfolio(client_id) is not None:
            return repository.fund.credit_history(portfolio_id, before, last)
        return repository.portfolio.get_patrimonial_history(portfolio_id, before, last)

    def _changed(self, client_id: UUID) -> None:
        if self.on_changed is not None:
            self.on_changed(client_id)

    def _notify(self, event: Event, payload: BaseDTO, client_id: UUID) -> None:
        """O aviso vai a quem vê a conta: o dono da conta pessoal ou o gestor principal da gestora."""
        self._changed(client_id)
        audience, account = self._engine.audience(client_id)
        json = payload.model_copy(update={"account": account}).to_json()
        for recipient in audience[:1]:
            notify(event, json, to=recipient)

    def _load(self, client_id: UUID) -> ClientCredit:
        events = repository.credit.get_events(
            self._engine.simulation_id, UserManager.get_portfolio_id(client_id)
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

    def transfer_loans(self, source: UUID, target: UUID) -> list[Loan]:
        """Os empréstimos em aberto de `source` passam a `target`, com o histórico de cada um.

        Os eventos de cada empréstimo mudam de carteira no banco e saem do estado de `source`;
        `target` relê os seus eventos na ordem do banco: a dívida segue como estava, sem evento
        novo de contratação nem de quitação.
        """
        with self._lock:
            from_client = self.client(source)
            to_client = self.client(target)
            moved_ids = list(from_client.loans)
            if not moved_ids:
                return []
            # Os eventos ainda no buffer precisam estar gravados para mudar de carteira
            EventManager.flush()
            source_portfolio = UserManager.get_portfolio_id(source)
            target_portfolio = UserManager.get_portfolio_id(target)
            repository.credit.move_loans(
                self._engine.simulation_id,
                source_portfolio,
                target_portfolio,
                moved_ids,
            )
            moving = set(moved_ids)
            from_client.events = [
                e for e in from_client.events if e.loan_id not in moving
            ]
            for loan_id in moved_ids:
                del from_client.loans[loan_id]
            # O estado de `target` sai da releitura dos eventos na ordem do banco: o número de cada
            # empréstimo é o mesmo que a carteira mostra depois de carregada de novo
            reloaded = replay(
                repository.credit.get_events(
                    self._engine.simulation_id, target_portfolio
                )
            )
            reloaded.rating = to_client.rating
            reloaded.seen = to_client.seen
            reloaded.previous = to_client.previous
            reloaded.warned = to_client.warned
            self._clients[target] = reloaded
            self._changed(source)
            self._changed(target)
            return [
                reloaded.loans[loan_id]
                for loan_id in moved_ids
                if loan_id in reloaded.loans
            ]

    # ------------------------------------------------------------------ leitura

    def loan_debt(self, client_id: UUID, day: date) -> Decimal:
        """Saldo devedor dos empréstimos e do consignado da conta no dia, com multa e mora."""
        client = self.client(client_id)
        return sum((loan.debt_on(day) for loan in client.open_contracts()), ZERO)

    def fee_payable(self, client_id: UUID) -> Decimal:
        """A taxa a pagar da gestora: dívida da conta dela, fora dos empréstimos; zero nas demais contas."""
        return self._engine.fund_fee_payable.get(client_id, ZERO)

    def debt(self, client_id: UUID, day: date) -> Decimal:
        """A dívida total da conta no dia: os empréstimos mais a taxa a pagar da gestora."""
        return self.loan_debt(client_id, day) + self.fee_payable(client_id)

    def loans(self, client_id: UUID) -> list[Loan]:
        return sorted(self.client(client_id).loans.values(), key=lambda x: x.number)

    def loan(self, client_id: UUID, loan_id: UUID) -> Loan:
        loan = self.client(client_id).loans.get(loan_id)
        if loan is None:
            raise NotFoundError("Esse empréstimo não existe ou já foi quitado.")
        return loan

    def loan_contract(self, client_id: UUID, loan_id: UUID) -> LoanContract:
        """O contrato em aberto, empréstimo comum ou consignado; amortizar e quitar servem aos dois."""
        contract = self.client(client_id).contract_of(loan_id)
        if contract is None:
            raise NotFoundError("Esse empréstimo não existe ou já foi quitado.")
        return contract

    def payroll_loans(self, client_id: UUID) -> list[PayrollLoan]:
        return sorted(
            self.client(client_id).payroll.values(), key=lambda x: x.contract_date
        )

    def payroll_rate(self, day: date) -> Decimal:
        """O juro do consignado: a SELIC do dia mais o spread fixo, sem nota nem piso da renda fixa."""
        rate = annual_index_rate(IndicatorSeries.SELIC, day) + PAYROLL_SPREAD
        # O juro tem a precisão que o evento grava: a retomada refaz o mesmo contrato
        return rate.quantize(RATE_STEP)

    def payroll_used(self, client_id: UUID) -> Decimal:
        """A parte da margem consignável que as parcelas dos consignados ativos ocupam."""
        return sum(
            (
                loan.state.installment
                for loan in self.client(client_id).payroll.values()
            ),
            ZERO,
        )

    def payroll_margin(self, client_id: UUID, net_salary: Decimal) -> Decimal:
        """A margem consignável livre: a fração do salário líquido que as parcelas dos consignados ativos ainda deixam."""
        return max(net_salary * PAYROLL_MARGIN - self.payroll_used(client_id), ZERO)

    def score(self, client_id: UUID, day: date) -> RatingScore:
        return self._score(self.client(client_id), day)

    def _score(self, client: ClientCredit, day: date) -> RatingScore:
        closed = client.rating
        late = client.recent_late(day)
        return RatingScore(
            leverage_points=closed.leverage_points if closed else leverage_points(ZERO),
            volatility_points=(
                closed.volatility_points if closed else volatility_points(None, 0)
            ),
            payment_points=payment_points(late),
        )

    def history(self, client_id: UUID) -> list[PatrimonialHistoryDTO]:
        return self._history(client_id, None, None)

    def assets_value(self, client_id: UUID) -> Decimal:
        return self._engine.assets_value(client_id)

    def networth(self, client_id: UUID, debt: Decimal) -> Decimal:
        """O patrimônio líquido da conta, pela definição única do patrimônio."""
        return self._engine.networth(client_id, debt)

    def cash(self, client_id: UUID) -> Decimal:
        return self._engine.get_cash(client_id)

    def best_fixed_income_rate(self, day: date) -> Decimal | None:
        """Maior taxa anual efetiva entre os títulos de renda fixa à venda hoje."""
        rates = [
            rate
            for asset in self._engine.fixed_income_market.get_available_assets()
            if asset.investment_type is not FixedIncomeType.DOLLAR_ACCOUNT
            and (rate := fixed_income_offer(asset, day).effective_annual_rate)
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
        networth = self.networth(client_id, debt)
        limit_amount = max(tier.debt_limit * networth, ZERO)
        if tier.spread is None:
            return Offer(selic, tier, score, None, best, ZERO, limit_amount)
        rate = selic + tier.spread + self._engine.premium_gap_on(day)
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

    def pending(
        self, client_id: UUID, day: date, fund: tuple[int, str] | None = None
    ) -> list[PendingDTO]:
        """Uma pendência por empréstimo com parcela em atraso e uma se o caixa não cobre o que vence em breve.

        Na conta de uma gestora, `fund` traz o id e o ticker dela: a pendência nomeia a gestora e aponta para ela.
        """
        client = self.client(client_id)
        owner = f"{fund[1]} · " if fund else ""
        fund_id = fund[0] if fund else None
        items = [
            registry.pending(
                PendingType.OVERDUE_INSTALLMENT,
                f"{owner}Empréstimo {loan.number} · "
                f"{format_money(sum((o.amount for o in loan.overdue), ZERO))}"
                " · multa de 2% e mora correndo",
                ref=str(loan.loan_id),
                loan_id=loan.loan_id,
                fund_id=fund_id,
            )
            for loan in sorted(client.loans.values(), key=lambda loan: loan.number)
            if loan.overdue
        ]
        shortfall = self._shortfall(client_id, client, day)
        if shortfall > 0:
            next_due = min(
                loan.state.next_due for loan, _ in self._due_soon(client, day)
            )
            items.append(
                registry.pending(
                    PendingType.CASH_SHORT,
                    f"{owner}Faltam {format_money(shortfall)} até {next_due:%d/%m}",
                    ref=str(fund_id) if fund_id is not None else "",
                    fund_id=fund_id,
                )
            )
        return items

    def _due_soon(self, client: ClientCredit, day: date) -> list[tuple[Loan, Decimal]]:
        limit = day + timedelta(days=WARNING_DAYS)
        return [
            (loan, loan.state.due_amount())
            for loan in client.loans.values()
            if not loan.state.is_closed and loan.state.next_due <= limit
        ]

    def _shortfall(self, client_id: UUID, client: ClientCredit, day: date) -> Decimal:
        # A falta é de parcela que vence em breve: sem parcela, o caixa negativo não falta a nada
        due_soon = self._due_soon(client, day)
        if not due_soon:
            return ZERO
        due = sum((amount for _, amount in due_soon), ZERO)
        return max(due - self._engine.get_cash(client_id), ZERO)

    # ------------------------------------------------------------------ nota

    def closing(self, client_id: UUID, day: date) -> ClosedRating:
        # A nota usa o último snapshot e os retornos da janela, todos de antes do mês
        window = self._history(client_id, day.replace(day=1), ROLLING_WINDOW + 1)
        return close_rating(window, day)

    def close_month(self, client_ids: list[UUID], day: date) -> None:
        """Na virada do mês a alavancagem e a volatilidade do mês que fechou valem para a nota."""
        for client_id in client_ids:
            with self._lock:
                client = self._clients[client_id]
                client.rating = self.closing(client_id, day)
                client.previous = None
                self._changed(client_id)
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
        self._notify(
            "credit_rating_changed",
            CreditRatingChangedEventDTO(
                before=seen.grade,
                after=score.grade,
                points=score.points,
                spread=tier.spread,
                debt_limit=tier.debt_limit,
            ),
            client_id,
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
            self._engine.cover_before_debit(
                client_id, amount, CashflowEventType.LOAN_PAYMENT
            )
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
                    self._notify(
                        "credit_installment_paid",
                        CreditInstallmentPaidEventDTO(
                            loan_number=loan.number,
                            installment_number=number,
                            total_installments=total,
                            amount=amount,
                        ),
                        client_id,
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
                self._notify(
                    "credit_installment_late",
                    CreditInstallmentLateEventDTO(
                        loan_id=loan.loan_id,
                        loan_number=loan.number,
                        installment_number=number,
                        due_date=due,
                        amount=amount,
                    ),
                    client_id,
                )
        if loan.is_settled:
            del client.loans[loan.loan_id]
            self._notify(
                "credit_loan_paid_off",
                CreditLoanPaidOffEventDTO(
                    loan_number=loan.number,
                    amount=loan.principal,
                    interest_saved=ZERO,
                ),
                client_id,
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
            self._notify(
                "credit_installment_warning",
                CreditInstallmentWarningEventDTO(
                    loan_number=loan.number,
                    due_date=loan.state.next_due,
                    amount=amount,
                    shortfall=shortfall,
                ),
                client_id,
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
            self._notify(
                "credit_monthly_summary",
                CreditMonthlySummaryEventDTO(
                    month=day.replace(day=1),
                    installments=len(paid),
                    amount=sum((e.amount for e in paid), ZERO),
                ),
                client_id,
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

    def contract_payroll(
        self, client_id: UUID, amount: Decimal, term_months: int, net_salary: Decimal
    ) -> PayrollLoan:
        """Contrata o consignado: a parcela precisa caber na margem livre sobre `net_salary`, o salário líquido do mês."""
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
            rate = self.payroll_rate(day)
            state = LoanState.sign(day, amount, rate, term_months)
            if state.installment > self.payroll_margin(client_id, net_salary):
                raise ConflictError("A parcela passa da sua margem consignável.")
            client = self._clients[client_id]
            loan = PayrollLoan(
                loan_id=uuid4(),
                principal=amount,
                term_months=term_months,
                state=state,
            )
            client.payroll[loan.loan_id] = loan
            self._engine.receive_loan(client_id, amount)
            self._record(
                client,
                client_id,
                loan,
                CreditEventType.PAYROLL_CONTRACT,
                amount,
                annual_rate=rate,
                term_months=term_months,
            )
            return loan

    def collect_payroll(self, client_id: UUID) -> None:
        """Cobra a parcela de cada consignado devida na virada do mês: ela sai do caixa, do salário que acabou de entrar, e nunca atrasa."""
        with self._lock:
            client = self._clients[client_id]
            day = self._engine.current_date
            for loan in self.payroll_loans(client_id):
                if not loan.due_for_collection(day):
                    continue
                amount = loan.state.due_amount()
                number = loan.state.next_number
                self._engine.pay_payroll_installment(client_id, amount)
                loan.state = loan.state.advance()
                self._record(
                    client,
                    client_id,
                    loan,
                    CreditEventType.PAYROLL_INSTALLMENT,
                    amount,
                    number,
                )
                if loan.is_settled:
                    del client.payroll[loan.loan_id]

    def prepay(
        self, client_id: UUID, loan_id: UUID, amount: Decimal, mode: PrepaymentMode
    ) -> LoanContract:
        amount = money(amount)
        with self._lock:
            loan = self.loan_contract(client_id, loan_id)
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
            loan = self.loan_contract(client_id, loan_id)
            day = self._engine.current_date
            amount = loan.payoff_on(day)
            self._require_cash(client_id, amount)
            remaining = sum((row.payment for row in loan.state.schedule()), ZERO)
            saved = max(remaining - loan.state.balance_on(day), ZERO)
            client = self._clients[client_id]
            self._engine.pay_loan(client_id, amount)
            self._record(client, client_id, loan, CreditEventType.PAYOFF, amount)
            if isinstance(loan, Loan):
                del client.loans[loan_id]
                self._notify(
                    "credit_loan_paid_off",
                    CreditLoanPaidOffEventDTO(
                        loan_number=loan.number, amount=amount, interest_saved=saved
                    ),
                    client_id,
                )
            else:
                del client.payroll[loan_id]
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
        loan: LoanContract,
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
            portfolio_id=UserManager.get_portfolio_id(client_id),
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
        self._changed(client_id)
