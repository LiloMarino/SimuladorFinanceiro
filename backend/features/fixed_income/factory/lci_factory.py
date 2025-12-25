from datetime import datetime

from backend.core import repository
from backend.core.dto.fixed_income_asset import (
    FixedIncomeAssetDTO,
)
from backend.core.enum import FixedIncomeType, RateIndexType
from backend.features.fixed_income.factory.abstract_factory import (
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

    def create_cdi(self, current_date: datetime) -> FixedIncomeAssetDTO:
        maturity_date = self._generate_maturity(current_date, 0, 6)
        rate = self._generate_rate(base_value=1.0, delta=0.20, multiplier=0.85)
        issuer = "Banco Imobiliário"

        return FixedIncomeAssetDTO(
            name=f"LCI {issuer} {rate * 100:.2f}% CDI",
            issuer=issuer,
            interest_rate=rate,
            rate_index=RateIndexType.CDI,
            investment_type=FixedIncomeType.LCI,
            maturity_date=maturity_date,
        )

    def create_ipca(self, current_date: datetime) -> FixedIncomeAssetDTO:
        maturity_date = self._generate_maturity(current_date, 0, 8)
        base_diff = (
            repository.economic.get_cdi_rate(current_date)
            - repository.economic.get_ipca_rate(current_date)
        ) * 0.85
        rate = self._generate_rate(base_value=base_diff, delta=0.004)
        issuer = "Banco Imobiliário"

        return FixedIncomeAssetDTO(
            name=f"LCI {issuer} IPCA+ {rate:.2f}%",
            issuer=issuer,
            interest_rate=rate,
            rate_index=RateIndexType.IPCA,
            investment_type=FixedIncomeType.LCI,
            maturity_date=maturity_date,
        )

    def create_prefixado(self, current_date: datetime) -> FixedIncomeAssetDTO:
        maturity_date = self._generate_maturity(current_date, 0, 5)
        base = repository.economic.get_cdi_rate(current_date)
        rate = self._generate_rate(base_value=base, delta=0.005, multiplier=0.85)
        issuer = "Banco Imobiliário"

        return FixedIncomeAssetDTO(
            name=f"LCI {issuer} Prefixado {rate:.2f}%",
            issuer=issuer,
            interest_rate=rate,
            rate_index=RateIndexType.PREFIXADO,
            investment_type=FixedIncomeType.LCI,
            maturity_date=maturity_date,
        )
