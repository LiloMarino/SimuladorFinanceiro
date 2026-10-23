from typing import Any

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.models.models import LastSimulationSettings


class LastSimulationSettingsRepository:
    """Guarda somente a última regra usada para criar uma nova partida."""

    @transactional
    def get(self, session: Session) -> dict[str, Any] | None:
        settings = session.get(LastSimulationSettings, 1)
        return settings.settings if settings is not None else None

    @transactional
    def save(self, session: Session, settings: dict[str, Any]) -> None:
        statement = insert(LastSimulationSettings).values(id=1, settings=settings)
        session.execute(
            statement.on_conflict_do_update(
                index_elements=["id"], set_={"settings": statement.excluded.settings}
            )
        )

    @transactional
    def clear(self, session: Session) -> None:
        session.execute(
            delete(LastSimulationSettings).where(LastSimulationSettings.id == 1)
        )
