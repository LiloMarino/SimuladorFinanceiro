from datetime import date

from backend.core.decorators.transactional_class import transactional_class


@transactional_class
class EconomicRepository:
    def get_cdi_rate(self, date: date):
        return 13.71

    def get_ipca_rate(self, date: date):
        return 5.17

    def get_selic_rate(self, date: date):
        return 15.0
