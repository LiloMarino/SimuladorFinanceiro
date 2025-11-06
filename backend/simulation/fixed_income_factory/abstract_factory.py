from abc import ABC, abstractmethod
from typing import Callable

from backend.simulation.entities.fixed_income_asset import (
    FixedIncomeAsset,
    RateIndexType,
)


class AbstractFixedIncomeFactory(ABC):
    def create_asset(self, rate_index: RateIndexType) -> FixedIncomeAsset:
        try:
            return self._strategies[rate_index]()
        except KeyError:
            raise ValueError(
                f"Indexador {rate_index} não suportado por {self.__class__.__name__}"
            )

    @property
    @abstractmethod
    def _strategies(self) -> dict[RateIndexType, Callable[[], FixedIncomeAsset]]:
        """Mapeia indexadores para funções de criação de ativos."""
        pass

    @property
    def valid_indexes(self) -> list[RateIndexType]:
        return list(self._strategies.keys())
