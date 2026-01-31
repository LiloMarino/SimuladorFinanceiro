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
    """
    Factory para criação de títulos do Tesouro Direto.

    Responsável por:
    - Gerar títulos com indexadores SELIC, IPCA e Prefixado
    - Usar nomenclatura padrão do Tesouro (Selic, IPCA+, Prefixado)
    """

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
        spread = self._generate_ipca_spread(
            current_date,
            spread_index=repository.economic.get_selic_rate,
        )

        return FixedIncomeAssetDTO(
            name=f"Tesouro IPCA+ {maturity_year}",
            issuer="Tesouro Nacional",
            interest_rate=spread,
            rate_index=RateIndexType.IPCA,
            investment_type=FixedIncomeType.TESOURO_DIRETO,
            maturity_date=maturity_date,
        )

    def create_prefixado(self, current_date: date) -> FixedIncomeAssetDTO:
        maturity_date = self._generate_maturity(current_date, 3, 7)
        maturity_year = maturity_date.year
        rate = self._generate_prefixado_rate(
            current_date,
            base_index=lambda current_date: repository.economic.get_selic_rate(
                current_date
            )
            - 0.01,  # Redução de 1% devido ao longo prazo
        )

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
        spread = self._generate_selic_spread()

        return FixedIncomeAssetDTO(
            name=f"Tesouro Selic {maturity_year}",
            issuer="Tesouro Nacional",
            interest_rate=spread,
            rate_index=RateIndexType.SELIC,
            investment_type=FixedIncomeType.TESOURO_DIRETO,
            maturity_date=maturity_date,
        )
