from backend.simulation.entities.fixed_income_asset import (
    FixedIncomeAsset,
    RateIndexType,
)
from backend.simulation.fixed_income_factory.abstract_factory import (
    AbstractFixedIncomeFactory,
)


class LCAFactory(AbstractFixedIncomeFactory):
    def create_cdi(self) -> FixedIncomeAsset:
        pass

    def create_ipca(self) -> FixedIncomeAsset:
        pass

    def create_prefixado(self) -> FixedIncomeAsset:
        pass

    def create_selic(self) -> FixedIncomeAsset:
        raise NotImplementedError

    @property
    def valid_indexes(self) -> list[RateIndexType]:
        return [RateIndexType.CDI, RateIndexType.IPCA, RateIndexType.PREFIXADO]
