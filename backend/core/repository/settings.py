from typing import Any

from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.exceptions.http_exceptions import NotFoundError
from backend.core.models.models import Users


class SettingsRepository:
    @transactional
    def get_by_user_id(self, session: Session, user_id: int) -> dict[str, Any]:
        settings = session.query(Users.settings).filter(Users.id == user_id).scalar()
        if settings is None:
            raise NotFoundError("Usuário não encontrado.")
        return settings

    @transactional
    def update_by_user_id(
        self, session: Session, user_id: int, settings: dict[str, Any]
    ) -> None:
        (
            session.query(Users)
            .filter(Users.id == user_id)
            .update(
                {"settings": settings},
                synchronize_session=False,
            )
        )
