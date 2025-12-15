from datetime import datetime

from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional


class SnapshotRepository:
    @transactional
    def create_snapshot(self, session: Session, current_date: datetime) -> None:
        pass
