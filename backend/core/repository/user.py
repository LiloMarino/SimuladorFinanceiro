from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.user import UserDTO
from backend.core.models.models import Users


class UserRepository:
    @transactional
    def get_by_client_id(self, session: Session, client_id: str) -> UserDTO | None:
        user = session.query(Users).filter_by(client_id=client_id).first()
        if not user:
            return None

        return UserDTO(
            id=user.id,
            client_id=user.client_id,
            nickname=user.nickname,
        )
