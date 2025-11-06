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


class CDBFactory(AbstractFixedIncomeFactory):
    @property
    def _strategies(self):
        return {
            RateIndexType.CDI: self.create_cdi,
            RateIndexType.IPCA: self.create_ipca,
            RateIndexType.PREFIXADO: self.create_prefixado,
        }

    def create_cdi(self, current_date: datetime) -> FixedIncomeAsset:
        maturity_date = self._generate_maturity(current_date, 1, 5)
        rate = round(random.uniform(1.05, 1.20), 4)
        issuer = "Banco XPTO"

        return FixedIncomeAsset(
            name=f"CDB {issuer} {rate*100}% CDI",
            issuer=issuer,
            interest_rate=rate,
            rate_index=RateIndexType.CDI,
            investment_type=FixedIncomeType.CDB,
            maturity_date=maturity_date,
        )

    def create_ipca(self, current_date: datetime) -> FixedIncomeAsset:
        maturity_date = self._generate_maturity(current_date, 2, 8)

        # Oscila em torno da diferença CDI - IPCA (0.5 p.p.)
        delta = 0.005  # 0.5%
        selic_base = get_cdi_rate() - get_ipca_rate()
        spread = round(random.uniform(selic_base - delta, selic_base + delta), 4)

        issuer = "Banco XPTO"
        return FixedIncomeAsset(
            name=f"CDB {issuer} IPCA+ {spread*100:.2f}%",
            issuer=issuer,
            interest_rate=spread,
            rate_index=RateIndexType.IPCA,
            investment_type=FixedIncomeType.CDB,
            maturity_date=maturity_date,
        )

    def create_prefixado(self, current_date: datetime) -> FixedIncomeAsset:
        maturity_date = self._generate_maturity(current_date, 2, 6)
        cdi = get_cdi_rate()

        # Oscila em torno da SELIC (0.5 p.p.)
        delta = 0.005  # 0.5%
        rate = round(random.uniform(cdi - delta, cdi + delta), 4)
        issuer = "Banco XPTO"

        return FixedIncomeAsset(
            name=f"CDB {issuer} Prefixado {rate*100:.2f}%",
            issuer=issuer,
            interest_rate=rate,
            rate_index=RateIndexType.PREFIXADO,
            investment_type=FixedIncomeType.CDB,
            maturity_date=maturity_date,
        )
