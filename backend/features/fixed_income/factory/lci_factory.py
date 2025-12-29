from datetime import date

from backend.core import repository
from backend.core.dto.fixed_income_asset import (
    FixedIncomeAssetDTO,
)
from backend.core.enum import FixedIncomeType, RateIndexType
from backend.core.utils import format_percent
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

    def create_cdi(self, current_date: date) -> FixedIncomeAssetDTO:
        maturity_date = self._generate_maturity(current_date, 0, 6)
        rate = self._generate_cdi_rate(multiplier=0.85)
        issuer = "Banco Imobiliário"

        return FixedIncomeAssetDTO(
            name=f"LCI {issuer} {format_percent(rate)} CDI",
            issuer=issuer,
            interest_rate=rate,
            rate_index=RateIndexType.CDI,
            investment_type=FixedIncomeType.LCI,
            maturity_date=maturity_date,
        )

    def create_ipca(self, current_date: date) -> FixedIncomeAssetDTO:
        maturity_date = self._generate_maturity(current_date, 0, 8)
        spread = self._generate_ipca_spread(
            current_date,
            spread_index=repository.economic.get_cdi_rate,
            multiplier=0.85,
        )
        issuer = "Banco Imobiliário"

        return FixedIncomeAssetDTO(
            name=f"LCI {issuer} IPCA+ {format_percent(spread)}",
            issuer=issuer,
            interest_rate=spread,
            rate_index=RateIndexType.IPCA,
            investment_type=FixedIncomeType.LCI,
            maturity_date=maturity_date,
        )

    def create_prefixado(self, current_date: date) -> FixedIncomeAssetDTO:
        maturity_date = self._generate_maturity(current_date, 0, 5)
        rate = self._generate_prefixado_rate(
            current_date, base_index=repository.economic.get_cdi_rate, multiplier=0.85
        )
        issuer = "Banco Imobiliário"

        return FixedIncomeAssetDTO(
            name=f"LCI {issuer} Prefixado {format_percent(rate)}",
            issuer=issuer,
            interest_rate=rate,
            rate_index=RateIndexType.PREFIXADO,
            investment_type=FixedIncomeType.LCI,
            maturity_date=maturity_date,
        )
