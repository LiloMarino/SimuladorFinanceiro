import random
from datetime import datetime

from backend.core.repository import RepositoryManager
from backend.features.simulation.entities.fixed_income_asset import (
    FixedIncomeAsset,
    FixedIncomeType,
    RateIndexType,
)
from backend.features.simulation.fixed_income.factory.abstract_factory import (
    AbstractFixedIncomeFactory,
)


class LCAFactory(AbstractFixedIncomeFactory):
    @property
    def _strategies(self):
        return {
            RateIndexType.CDI: self.create_cdi,
            RateIndexType.IPCA: self.create_ipca,
            RateIndexType.PREFIXADO: self.create_prefixado,
        }

    def create_cdi(self, current_date: datetime) -> FixedIncomeAsset:
        maturity_date = self._generate_maturity(current_date, 2, 6)
        rate = self._generate_rate(base_value=1.0, delta=0.20, multiplier=0.85)
        issuer = "Banco Agro"

        return FixedIncomeAsset(
            name=f"LCA {issuer} {rate*100:.2f}% CDI",
            issuer=issuer,
            interest_rate=rate,
            rate_index=RateIndexType.CDI,
            investment_type=FixedIncomeType.LCA,
            maturity_date=maturity_date,
        )

    def create_ipca(self, current_date: datetime) -> FixedIncomeAsset:
        maturity_date = self._generate_maturity(current_date, 3, 8)
        base_diff = (
            RepositoryManager.economic.get_cdi_rate()
            - RepositoryManager.economic.get_ipca_rate()
        ) * 0.85
        rate = self._generate_rate(base_value=base_diff, delta=0.004)
        issuer = "Banco Agro"

        return FixedIncomeAsset(
            name=f"LCA {issuer} IPCA+ {rate:.2f}%",
            issuer=issuer,
            interest_rate=rate,
            rate_index=RateIndexType.IPCA,
            investment_type=FixedIncomeType.LCA,
            maturity_date=maturity_date,
        )

    def create_prefixado(self, current_date: datetime) -> FixedIncomeAsset:
        maturity_date = self._generate_maturity(current_date, 2, 5)
        base = RepositoryManager.economic.get_cdi_rate()
        rate = self._generate_rate(base_value=base, delta=0.005, multiplier=0.85)
        issuer = "Banco Agro"

        return FixedIncomeAsset(
            name=f"LCA {issuer} Prefixado {rate:.2f}%",
            issuer=issuer,
            interest_rate=rate,
            rate_index=RateIndexType.PREFIXADO,
            investment_type=FixedIncomeType.LCA,
            maturity_date=maturity_date,
        )
