from datetime import date

from backend.core import repository
from backend.core.dto.fixed_income_asset import (
    FixedIncomeAssetDTO,
)
from backend.core.enum import FixedIncomeType, RateIndexType
from backend.features.fixed_income.factory.abstract_factory import (
    AbstractFixedIncomeFactory,
)


class TesouroFactory(AbstractFixedIncomeFactory):
    @property
    def _strategies(self):
        return {
            RateIndexType.SELIC: self.create_selic,
            RateIndexType.IPCA: self.create_ipca,
            RateIndexType.PREFIXADO: self.create_prefixado,
        }

    def create_ipca(self, current_date: date) -> FixedIncomeAssetDTO:
        maturity_date = self._generate_maturity(current_date, 3, 15)
        maturity_year = maturity_date.year
        base_diff = repository.economic.get_selic_rate(
            current_date
        ) - repository.economic.get_ipca_rate(current_date)
        rate = self._generate_rate(base_value=base_diff, delta=0.005)

        return FixedIncomeAssetDTO(
            name=f"Tesouro IPCA+ {maturity_year}",
            issuer="Tesouro Nacional",
            interest_rate=rate,
            rate_index=RateIndexType.IPCA,
            investment_type=FixedIncomeType.TESOURO_DIRETO,
            maturity_date=maturity_date,
        )

    def create_prefixado(self, current_date: date) -> FixedIncomeAssetDTO:
        maturity_date = self._generate_maturity(current_date, 3, 7)
        maturity_year = maturity_date.year
        selic_base = (
            repository.economic.get_selic_rate(current_date) - 0.01
        )  # Redução de 1% devido ao longo prazo
        rate = self._generate_rate(base_value=selic_base, delta=0.005)

        return FixedIncomeAssetDTO(
            name=f"Tesouro Prefixado {maturity_year}",
            issuer="Tesouro Nacional",
            interest_rate=rate,
            rate_index=RateIndexType.PREFIXADO,
            investment_type=FixedIncomeType.TESOURO_DIRETO,
            maturity_date=maturity_date,
        )

    def create_selic(self, current_date: date) -> FixedIncomeAssetDTO:
        maturity_date = self._generate_maturity(current_date, 3, 7)
        maturity_year = maturity_date.year
        rate = self._generate_rate(base_value=0.00125, delta=0.00075)  # 0.0005-0.002

        return FixedIncomeAssetDTO(
            name=f"Tesouro Selic {maturity_year}",
            issuer="Tesouro Nacional",
            interest_rate=rate,
            rate_index=RateIndexType.SELIC,
            investment_type=FixedIncomeType.TESOURO_DIRETO,
            maturity_date=maturity_date,
        )
