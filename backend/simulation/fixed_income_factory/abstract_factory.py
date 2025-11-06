import random
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Callable

from backend.simulation.entities.fixed_income_asset import (
    FixedIncomeAsset,
    RateIndexType,
)


class AbstractFixedIncomeFactory(ABC):
    def create_asset(
        self, rate_index: RateIndexType, current_date: datetime
    ) -> FixedIncomeAsset:
        try:
            return self._strategies[rate_index](current_date)
        except KeyError:
            raise ValueError(
                f"Indexador {rate_index} não suportado por {self.__class__.__name__}"
            )

    @property
    @abstractmethod
    def _strategies(
        self,
    ) -> dict[RateIndexType, Callable[[datetime], FixedIncomeAsset]]:
        """Mapeia indexadores para funções de criação de ativos."""
        pass

    def _generate_maturity(
        self, current_date: datetime, min_years: int, max_years: int
    ) -> datetime:
        """Gera uma data de vencimento aleatória entre N e M anos."""
        delta_years = random.randint(min_years, max_years)
        days_extra = random.randint(0, 365)
        return current_date + timedelta(days=delta_years * 365 + days_extra)

    @property
    def valid_indexes(self) -> list[RateIndexType]:
        return list(self._strategies.keys())
