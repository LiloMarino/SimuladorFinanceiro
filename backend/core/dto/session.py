from backend.core.dto.base import BaseDTO
from backend.core.dto.user import UserDTO


class SessionDTO(BaseDTO):
    authenticated: bool
    user: UserDTO | None
    # Há partida em andamento e o usuário ainda não joga nela: escolhe a cor em /api/simulation/join
    pending_join: bool = False
