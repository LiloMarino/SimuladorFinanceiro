from datetime import date

from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional


class EconomicRepository:
    @transactional
    def get_cdi_rate(self, session: Session, date: date):
        return 13.71

    @transactional
    def get_ipca_rate(self, session: Session, date: date):
        return 5.17

    @transactional
    def get_selic_rate(self, session: Session, date: date):
        return 15.0
