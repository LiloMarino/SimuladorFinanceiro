from uuid import UUID

from backend.core.dto.base import BaseDTO


class UserDTO(BaseDTO):
    id: int
    client_id: UUID
    nickname: str
