from datetime import date
from decimal import Decimal


class EconomicRepository:
    def get_cdi_rate(self, date: date) -> Decimal:
        return Decimal("0.149")

    def get_ipca_rate(self, date: date) -> Decimal:
        return Decimal("0.0468")

    def get_selic_rate(self, date: date) -> Decimal:
        return Decimal("0.150")
