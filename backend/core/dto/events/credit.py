from decimal import Decimal
from uuid import UUID

from backend.core.dto.events.base_event import BaseEventDTO
from backend.core.enum import CreditEventType, CreditGrade, PrepaymentMode


class CreditEventDTO(BaseEventDTO):
    loan_id: UUID
    event_type: CreditEventType
    # Principal no contrato; valor pago nos demais eventos
    amount: Decimal
    # Parcela a que o evento se refere, nos eventos de parcela
    installment_number: int | None = None
    # Só no contrato: juro anual travado, prazo e a nota da assinatura
    annual_rate: Decimal | None = None
    term_months: int | None = None
    grade: CreditGrade | None = None
    # Só na amortização
    prepayment_mode: PrepaymentMode | None = None
