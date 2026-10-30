from typing import Any

from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.preparation import PartyIdentityDTO
from backend.core.exceptions.http_exceptions import NotFoundError
from backend.core.models.models import Users

MY_PARTY_KEY = "my_party"


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

    def get_my_party(self, user_id: int) -> PartyIdentityDTO | None:
        """O Meu partido salvo no perfil; nulo enquanto o jogador não salvou um."""
        raw = self.get_by_user_id(user_id).get(MY_PARTY_KEY)
        return None if raw is None else PartyIdentityDTO.model_validate(raw)

    def set_my_party(self, user_id: int, party: PartyIdentityDTO) -> None:
        settings = self.get_by_user_id(user_id)
        self.update_by_user_id(
            user_id, {**settings, MY_PARTY_KEY: party.model_dump(mode="json")}
        )
