import random
from datetime import date
from functools import partial

from backend.core.dto.fixed_income_asset import (
    FixedIncomeAssetDTO,
)
from backend.core.enum import FixedIncomeType, IndicatorSeries, RateIndexType
from backend.core.indicators import annual_index_rate
from backend.features.fixed_income.factory.abstract_factory import (
    AbstractFixedIncomeFactory,
)

# Bancos que emitem CDB; o emissor entra no nome do título
ISSUERS = (
    "Banco Inter",
    "XP",
    "Nubank",
    "PicPay",
    "Itaú",
    "Bradesco",
    "Santander",
    "BTG Pactual",
    "C6 Bank",
    "Banco Pan",
)


class CDBFactory(AbstractFixedIncomeFactory):
    """
    Factory para criação de ativos CDB (Certificado de Depósito Bancário).

    Responsável por:
    - Gerar CDBs com indexadores CDI, IPCA e Prefixado
    """

    @property
    def _strategies(self):
        return {
            RateIndexType.CDI: self.create_cdi,
            RateIndexType.IPCA: self.create_ipca,
            RateIndexType.PREFIXADO: self.create_prefixado,
        }

    def create_cdi(self, current_date: date) -> FixedIncomeAssetDTO:
        maturity_date = self._generate_maturity(current_date, 0, 5)
        rate = self._generate_cdi_rate()
        issuer = random.choice(ISSUERS)

        return FixedIncomeAssetDTO(
            name=f"CDB {issuer}",
            issuer=issuer,
            interest_rate=rate,
            rate_index=RateIndexType.CDI,
            investment_type=FixedIncomeType.CDB,
            maturity_date=maturity_date,
        )

    def create_ipca(self, current_date: date) -> FixedIncomeAssetDTO:
        maturity_date = self._generate_maturity(current_date, 0, 8)
        spread = self._generate_ipca_spread(
            current_date,
            spread_index=partial(annual_index_rate, IndicatorSeries.CDI),
        )
        issuer = random.choice(ISSUERS)

        return FixedIncomeAssetDTO(
            name=f"CDB IPCA+ {issuer}",
            issuer=issuer,
            interest_rate=spread,
            rate_index=RateIndexType.IPCA,
            investment_type=FixedIncomeType.CDB,
            maturity_date=maturity_date,
        )

    def create_prefixado(self, current_date: date) -> FixedIncomeAssetDTO:
        maturity_date = self._generate_maturity(current_date, 0, 6)
        rate = self._generate_prefixado_rate(
            current_date, base_index=partial(annual_index_rate, IndicatorSeries.CDI)
        )
        issuer = random.choice(ISSUERS)

        return FixedIncomeAssetDTO(
            name=f"CDB Prefixado {issuer}",
            issuer=issuer,
            interest_rate=rate,
            rate_index=RateIndexType.PREFIXADO,
            investment_type=FixedIncomeType.CDB,
            maturity_date=maturity_date,
        )
