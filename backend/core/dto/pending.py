from uuid import UUID

from backend.core.dto.base import BaseDTO
from backend.core.enum import PendingSeverity, PendingType


class PendingDTO(BaseDTO):
    """Uma pendência do jogador; a gravidade e o título vêm do tipo, no registro."""

    # Estável enquanto a pendência vive: é como a tela sabe que uma nasceu
    key: str
    type: PendingType
    severity: PendingSeverity
    title: str
    detail: str
    # Quando ela some, em palavras: vem do registro, igual para todas do tipo
    resolves: str
    # Presente na parcela em atraso: o empréstimo que a ação paga
    loan_id: UUID | None
