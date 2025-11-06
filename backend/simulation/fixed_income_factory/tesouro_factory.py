import random
from datetime import datetime

from backend.data_provider import get_ipca_rate, get_selic_rate
from backend.simulation.entities.fixed_income_asset import (
    FixedIncomeAsset,
    FixedIncomeType,
    RateIndexType,
)
from backend.simulation.fixed_income_factory.abstract_factory import (
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

    def create_ipca(self, current_date: datetime) -> FixedIncomeAsset:
        maturity_date = self._generate_maturity(current_date, 3, 15)
        maturity_year = maturity_date.year

        # Oscila em torno da diferença SELIC - IPCA (0.5 p.p.)
        delta = 0.005  # 0.5%
        selic_base = get_selic_rate() - get_ipca_rate()
        spread = round(random.uniform(selic_base - delta, selic_base + delta), 4)

        return FixedIncomeAsset(
            name=f"Tesouro IPCA+ {maturity_year}",
            issuer="Tesouro Nacional",
            interest_rate=spread,
            rate_index=RateIndexType.IPCA,
            investment_type=FixedIncomeType.TESOURO_DIRETO,
            maturity_date=maturity_date,
        )

    def create_prefixado(self, current_date: datetime) -> FixedIncomeAsset:
        maturity_date = self._generate_maturity(current_date, 3, 7)
        maturity_year = maturity_date.year

        # Oscila em torno da SELIC (0.5 p.p.)
        delta = 0.005  # 0.5%
        selic_rate = get_selic_rate() - 0.01  # Redução de 1% devido ao longo prazo
        rate = round(random.uniform(selic_rate - delta, selic_rate + delta), 4)

        return FixedIncomeAsset(
            name=f"Tesouro Prefixado {maturity_year}",
            issuer="Tesouro Nacional",
            interest_rate=rate,
            rate_index=RateIndexType.PREFIXADO,
            investment_type=FixedIncomeType.TESOURO_DIRETO,
            maturity_date=maturity_date,
        )

    def create_selic(self, current_date: datetime) -> FixedIncomeAsset:
        maturity_date = self._generate_maturity(current_date, 3, 7)
        maturity_year = maturity_date.year

        spread = round(
            random.uniform(0.0005, 0.002), 4
        )  # Spread sobre Selic (0.05% a 0.2%)

        return FixedIncomeAsset(
            name=f"Tesouro Selic {maturity_year}",
            issuer="Tesouro Nacional",
            interest_rate=spread,
            rate_index=RateIndexType.SELIC,
            investment_type=FixedIncomeType.TESOURO_DIRETO,
            maturity_date=maturity_date,
        )
