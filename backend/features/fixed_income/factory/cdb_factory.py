from datetime import datetime

from backend.core import repository
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.dto.fixed_income_position import FixedIncomeType, RateIndexType
from backend.features.fixed_income.factory.abstract_factory import (
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

    def create_cdi(self, current_date: datetime) -> FixedIncomeAssetDTO:
        maturity_date = self._generate_maturity(current_date, 0, 5)
        rate = self._generate_rate(base_value=1.05, delta=0.15)
        issuer = "Banco XPTO"

        return FixedIncomeAssetDTO(
            name=f"CDB {issuer} {rate * 100:.2f}% CDI",
            issuer=issuer,
            interest_rate=rate,
            rate_index=RateIndexType.CDI,
            investment_type=FixedIncomeType.CDB,
            maturity_date=maturity_date,
        )

    def create_ipca(self, current_date: datetime) -> FixedIncomeAssetDTO:
        maturity_date = self._generate_maturity(current_date, 0, 8)
        base_diff = repository.economic.get_cdi_rate(
            current_date
        ) - repository.economic.get_ipca_rate(current_date)
        rate = self._generate_rate(base_value=base_diff, delta=0.005)
        issuer = "Banco XPTO"

        return FixedIncomeAssetDTO(
            name=f"CDB {issuer} IPCA+ {rate:.2f}%",
            issuer=issuer,
            interest_rate=rate,
            rate_index=RateIndexType.IPCA,
            investment_type=FixedIncomeType.CDB,
            maturity_date=maturity_date,
        )

    def create_prefixado(self, current_date: datetime) -> FixedIncomeAssetDTO:
        maturity_date = self._generate_maturity(current_date, 0, 6)
        base = repository.economic.get_cdi_rate(current_date)
        rate = self._generate_rate(base_value=base, delta=0.005)
        issuer = "Banco XPTO"

        return FixedIncomeAssetDTO(
            name=f"CDB {issuer} Prefixado {rate:.2f}%",
            issuer=issuer,
            interest_rate=rate,
            rate_index=RateIndexType.PREFIXADO,
            investment_type=FixedIncomeType.CDB,
            maturity_date=maturity_date,
        )
