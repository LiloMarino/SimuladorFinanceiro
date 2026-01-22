"""DTOs para respostas de túnel de rede."""

from dataclasses import dataclass

from backend.core.dto.base import BaseDTO


@dataclass(frozen=True, slots=True, kw_only=True)
class TunnelStatus(BaseDTO):
    """Status atual do túnel de rede."""

    active: bool
    url: str | None
    provider: str | None
