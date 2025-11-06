import random
from datetime import datetime

from backend.data_provider import get_cdi_rate, get_ipca_rate
from backend.simulation.entities.fixed_income_asset import (
    FixedIncomeAsset,
    FixedIncomeType,
    RateIndexType,
)
from backend.simulation.fixed_income_factory.abstract_factory import (
    AbstractFixedIncomeFactory,
)


class LCIFactory(AbstractFixedIncomeFactory):
    @property
    def _strategies(self):
        return {
            RateIndexType.CDI: self.create_cdi,
            RateIndexType.IPCA: self.create_ipca,
            RateIndexType.PREFIXADO: self.create_prefixado,
        }

    def create_cdi(self, current_date: datetime) -> FixedIncomeAsset:
        maturity_date = self._generate_maturity(current_date, 2, 6)
        rate = round(random.uniform(1.00, 1.20), 4) * 0.85
        issuer = "Banco Imobiliário"
        return FixedIncomeAsset(
            name=f"LCI {issuer} {rate*100:.2f}% CDI",
            issuer=issuer,
            interest_rate=rate,
            rate_index=RateIndexType.CDI,
            investment_type=FixedIncomeType.LCI,
            maturity_date=maturity_date,
        )

    def create_ipca(self, current_date: datetime) -> FixedIncomeAsset:
        maturity_date = self._generate_maturity(current_date, 3, 8)
        delta = 0.004
        base_diff = (get_cdi_rate() - get_ipca_rate()) * 0.85
        spread = round(random.uniform(base_diff - delta, base_diff + delta), 4)
        issuer = "Banco Imobiliário"
        return FixedIncomeAsset(
            name=f"LCI {issuer} IPCA+ {spread*100:.2f}%",
            issuer=issuer,
            interest_rate=spread,
            rate_index=RateIndexType.IPCA,
            investment_type=FixedIncomeType.LCI,
            maturity_date=maturity_date,
        )

    def create_prefixado(self, current_date: datetime) -> FixedIncomeAsset:
        maturity_date = self._generate_maturity(current_date, 2, 5)
        delta = 0.005
        base = get_cdi_rate()
        rate = round(random.uniform(base - delta, base + delta), 4) * 0.85
        issuer = "Banco Imobiliário"
        return FixedIncomeAsset(
            name=f"LCI {issuer} Prefixado {rate*100:.2f}%",
            issuer=issuer,
            interest_rate=rate,
            rate_index=RateIndexType.PREFIXADO,
            investment_type=FixedIncomeType.LCI,
            maturity_date=maturity_date,
        )
