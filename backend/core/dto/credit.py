from datetime import date
from decimal import Decimal
from enum import Enum
from uuid import UUID

from backend.core.dto.base import BaseDTO
from backend.core.enum import CreditGrade, PrepaymentMode


class LadderTierDTO(BaseDTO):
    grade: CreditGrade
    min_points: int
    # Pontos ao ano somados à SELIC (0.05 = SELIC + 5); nulo na nota sem crédito
    spread: Decimal | None
    # Fração do patrimônio que a dívida pode chegar a ser
    debt_limit: Decimal


class RatingPartDTO(BaseDTO):
    points: Decimal
    max_points: Decimal


class RatingLeverageDTO(RatingPartDTO):
    # Dívida sobre o patrimônio no fechamento do mês (0.259 = 25,9%); nulo sem patrimônio positivo
    value: Decimal | None


class RatingVolatilityDTO(RatingPartDTO):
    # Volatilidade anual no fechamento do mês; nula com pouco histórico
    value: Decimal | None


class RatingPaymentsDTO(RatingPartDTO):
    # Parcelas que atrasaram nos últimos 12 meses
    late_installments: int


class RatingDTO(BaseDTO):
    grade: CreditGrade
    points: int
    # A nota e os pontos de antes da última mudança; nulos quando nada mudou
    previous_grade: CreditGrade | None
    previous_points: int | None
    # Dia do próximo fechamento mensal da alavancagem e da volatilidade
    next_review: date
    leverage: RatingLeverageDTO
    volatility: RatingVolatilityDTO
    payments: RatingPaymentsDTO
    ladder: list[LadderTierDTO]


class CreditOfferDTO(BaseDTO):
    # Falso na nota D: o crédito novo fica bloqueado
    available: bool
    selic: Decimal
    spread: Decimal | None
    # Juro anual da oferta: o maior entre SELIC + spread e o piso da renda fixa
    annual_rate: Decimal | None
    # Renda fixa mais cara do dia, a que sustenta o piso do juro
    best_fixed_income_rate: Decimal | None
    # Quanto ainda cabe no limite da nota
    max_amount: Decimal
    debt_limit: Decimal
    # Limite de dívida em reais: fração da nota sobre o patrimônio
    debt_limit_amount: Decimal


class OverdueDTO(BaseDTO):
    installment_number: int
    due_date: date
    days_late: int
    installment: Decimal
    fee: Decimal
    interest: Decimal
    total: Decimal


class LoanDTO(BaseDTO):
    id: UUID
    # "Empréstimo N": a ordem em que o jogador contratou
    number: int
    principal: Decimal
    term_months: int
    annual_rate: Decimal
    grade: CreditGrade
    contract_date: date
    installment: Decimal
    paid_installments: int
    total_installments: int
    # Saldo do dia, com as parcelas em atraso dentro dele
    balance: Decimal
    # Multa e mora das parcelas em atraso, à parte do saldo
    overdue_charges: Decimal
    next_due: date | None
    overdue: list[OverdueDTO]


class UpcomingInstallmentDTO(BaseDTO):
    due_date: date
    loan_number: int
    installment_number: int
    total_installments: int
    amount: Decimal


class MonthPaymentsDTO(BaseDTO):
    month: date
    on_time: int
    paid_late: int
    late: int


class SuggestionKind(Enum):
    PAYOFF = "PAYOFF"
    VOLATILITY = "VOLATILITY"
    ON_TIME = "ON_TIME"
    # Caminho de volta da nota D
    RECOVER = "RECOVER"


class SuggestionDTO(BaseDTO):
    kind: SuggestionKind
    target_grade: CreditGrade | None
    # Quitar: quanto pagar e o juro que isso poupa nos empréstimos
    amount: Decimal | None = None
    interest_saved: Decimal | None = None
    # Alavancagem depois de quitar (0.2 = 20%); nula sem patrimônio positivo
    leverage_after: Decimal | None = None
    # Volatilidade anual que leva à próxima nota (0.12 = 12%)
    volatility: Decimal | None = None


class CreditOverviewDTO(BaseDTO):
    # Saldo devedor de todos os empréstimos mais multa e mora
    debt: Decimal
    open_loans: int
    closed_loans: int
    # Patrimônio líquido e os ativos de onde ele sai
    networth: Decimal
    assets: Decimal
    cash: Decimal
    leverage: Decimal | None
    # Parcelas do próximo mês de vencimento
    next_installments_month: date | None
    next_installments_total: Decimal
    next_installments_first: date | None
    next_installments_last: date | None
    cash_covers_next: bool
    rating: RatingDTO
    offer: CreditOfferDTO
    loans: list[LoanDTO]
    upcoming: list[UpcomingInstallmentDTO]
    history: list[MonthPaymentsDTO]
    suggestions: list[SuggestionDTO]
    # Rentabilidade da carteira nos últimos 12 meses; nula com menos de um ano
    portfolio_return_12m: Decimal | None


class InstallmentRowDTO(BaseDTO):
    number: int
    due_date: date
    interest: Decimal
    principal: Decimal
    payment: Decimal
    balance: Decimal


class LoanQuoteDTO(BaseDTO):
    amount: Decimal
    term_months: int
    annual_rate: Decimal
    monthly_rate: Decimal
    installment: Decimal
    total_interest: Decimal
    total_paid: Decimal
    due_day: int
    schedule: list[InstallmentRowDTO]
    # Nulos quando o patrimônio não é positivo
    leverage_before: Decimal | None
    leverage_after: Decimal | None
    # Nota e pontos projetados para o fechamento do mês
    projected_grade: CreditGrade
    projected_points: int
    # Dívida de hoje, quanto cabe no limite e quanto passa dele (0 quando cabe)
    current_debt: Decimal
    excess: Decimal
    cash_after: Decimal


class PrepaymentOptionDTO(BaseDTO):
    mode: PrepaymentMode
    installments_remaining: int
    installment: Decimal
    interest_saved: Decimal


class PrepaymentPreviewDTO(BaseDTO):
    balance: Decimal
    cash: Decimal
    shorten_term: PrepaymentOptionDTO | None
    reduce_installment: PrepaymentOptionDTO | None
    # Quitar: o que falta pagar em parcelas, o juro que ainda não correu e o saldo do dia
    payoff_installments: int
    payoff_remaining_payments: Decimal
    payoff_interest_saved: Decimal
    # Saldo do dia mais as parcelas em atraso com multa e mora
    payoff_amount: Decimal


class ContractLoanRequestDTO(BaseDTO):
    amount: Decimal
    term_months: int


class PrepayLoanRequestDTO(BaseDTO):
    amount: Decimal
    mode: PrepaymentMode
