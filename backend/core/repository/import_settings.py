from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.import_settings import ImportSettingsDTO
from backend.core.models.models import ImportSettings


class ImportSettingsRepository:
    """As escolhas do host sobre a importação; a base sem linha usa os padrões."""

    @transactional
    def get(self, session: Session) -> ImportSettingsDTO:
        row = session.get(ImportSettings, 1)
        if row is None:
            return ImportSettingsDTO()
        return ImportSettingsDTO(correct_price_errors=row.correct_price_errors)

    @transactional
    def save(self, session: Session, settings: ImportSettingsDTO) -> None:
        statement = insert(ImportSettings).values(
            id=1, correct_price_errors=settings.correct_price_errors
        )
        session.execute(
            statement.on_conflict_do_update(
                index_elements=["id"],
                set_={"correct_price_errors": statement.excluded.correct_price_errors},
            )
        )
