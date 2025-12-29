from datetime import date


class EconomicRepository:
    def get_cdi_rate(self, date: date):
        return 0.149

    def get_ipca_rate(self, date: date):
        return 0.0468

    def get_selic_rate(self, date: date):
        return 0.150
