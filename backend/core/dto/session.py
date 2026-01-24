from backend.core.dto.base import BaseDTO
from backend.core.dto.user import UserDTO


class SessionDTO(BaseDTO):
    authenticated: bool
    user: UserDTO | None
