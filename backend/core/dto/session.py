from dataclasses import dataclass

from backend.core.dto.base import BaseDTO
from backend.core.dto.user import UserDTO


@dataclass(frozen=True, kw_only=True)
class SessionDTO(BaseDTO):
    authenticated: bool
    user: UserDTO | None
