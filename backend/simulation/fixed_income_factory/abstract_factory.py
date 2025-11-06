from abc import ABC, abstractmethod

from backend.simulation.entities.fixed_income_asset import (
    FixedIncomeAsset,
    RateIndexType,
)


class AbstractFixedIncomeFactory(ABC):
    @abstractmethod
    def create_cdi(self) -> FixedIncomeAsset:
        pass

    @abstractmethod
    def create_ipca(self) -> FixedIncomeAsset:
        pass

    @abstractmethod
    def create_prefixado(self) -> FixedIncomeAsset:
        pass

    @abstractmethod
    def create_selic(self) -> FixedIncomeAsset:
        pass

    @property
    @abstractmethod
    def valid_indexes(self) -> list[RateIndexType]:
        pass
