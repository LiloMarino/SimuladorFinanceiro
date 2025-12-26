from datetime import date


class EconomicRepository:
    def get_cdi_rate(self, date: date):
        return 14.9

    def get_ipca_rate(self, date: date):
        return 4.68

    def get_selic_rate(self, date: date):
        return 15.0
