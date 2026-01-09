from dataclasses import dataclass
from uuid import UUID

from backend.core.dto.base import BaseDTO


@dataclass(frozen=True, kw_only=True)
class UserDTO(BaseDTO):
    id: int
    client_id: UUID
    nickname: str
