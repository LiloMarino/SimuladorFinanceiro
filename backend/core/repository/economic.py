from datetime import date

from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional


class EconomicRepository:
    @transactional
    def get_cdi_rate(self, session: Session, date: date):
        return 14.9

    @transactional
    def get_ipca_rate(self, session: Session, date: date):
        return 4.68

    @transactional
    def get_selic_rate(self, session: Session, date: date):
        return 15.0
