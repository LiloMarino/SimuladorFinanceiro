from datetime import date
from decimal import Decimal
from functools import partial

from backend.core.dto.fixed_income_asset import (
    FixedIncomeAssetDTO,
)
from backend.core.enum import FixedIncomeType, IndicatorSeries, RateIndexType
from backend.core.indicators import annual_index_rate
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

    @staticmethod
    def with_risk_premium(
        asset: FixedIncomeAssetDTO, risk_premium: Decimal
    ) -> FixedIncomeAssetDTO:
        """O título com o prêmio de risco do país somado à taxa: spread, prefixada ou spread da SELIC."""
        if risk_premium <= 0:
            return asset
        return asset.model_copy(
            update={
                "interest_rate": asset.interest_rate + risk_premium,
                "risk_premium": risk_premium,
            }
        )

    def create_ipca(self, current_date: date) -> FixedIncomeAssetDTO:
        maturity_date = self._generate_maturity(current_date, 3, 15)
        maturity_year = maturity_date.year
        spread = self._generate_ipca_spread(
            current_date,
            spread_index=partial(annual_index_rate, IndicatorSeries.SELIC),
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
            base_index=lambda current_date: (
                annual_index_rate(IndicatorSeries.SELIC, current_date) - Decimal("0.01")
            ),  # Redução de 1% devido ao longo prazo
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
