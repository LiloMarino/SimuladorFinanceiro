import random
from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import date, timedelta

from backend.core import repository
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.enum import RateIndexType


class AbstractFixedIncomeFactory(ABC):
    @property
    def valid_indexes(self) -> list[RateIndexType]:
        return list(self._strategies.keys())

    def create_asset(
        self, rate_index: RateIndexType, current_date: date
    ) -> FixedIncomeAssetDTO:
        try:
            return self._strategies[rate_index](current_date)
        except KeyError as e:
            raise ValueError(
                f"Indexador {rate_index} não suportado por {self.__class__.__name__}"
            ) from e

    @property
    @abstractmethod
    def _strategies(
        self,
    ) -> dict[RateIndexType, Callable[[date], FixedIncomeAssetDTO]]:
        """Mapeia indexadores para funções de criação de ativos."""
        pass

    def _generate_maturity(
        self, current_date: date, min_years: int, max_years: int
    ) -> date:
        """Gera uma data de vencimento aleatória entre N e M anos."""
        delta_years = random.randint(min_years, max_years)
        days_extra = random.randint(0, 365)
        return current_date + timedelta(days=delta_years * 365 + days_extra)

    # =========================================================
    # ======== GERADOR BASE (baixo nível)
    # =========================================================
    def _random_rate(
        self,
        base_value: float,
        delta: float,
        multiplier: float = 1.0,
    ) -> float:
        """Gera uma taxa de juros aleatória em torno de base ± delta, com multiplicador opcional."""
        rate = random.uniform(base_value - delta, base_value + delta)
        return round(rate * multiplier, 4)

    # =========================================================
    # ======== GERADORES POR INDEXADOR (alto nível)
    # =========================================================
    def _generate_cdi_rate(
        self,
        multiplier: float = 1.0,
    ) -> float:
        """
        Retorna percentual do CDI (ex: 1.10 = 110% do CDI)
        """
        upper_bound = 1.2
        lower_bound = 1.0
        base_value = (upper_bound + lower_bound) / 2
        return self._random_rate(
            base_value=base_value,
            delta=base_value - lower_bound,
            multiplier=multiplier,
        )

    def _generate_ipca_spread(
        self,
        current_date: date,
        spread_index: Callable[[date], float],
        multiplier: float = 1.0,
    ) -> float:
        """
        Retorna spread real (ex: 0.045 = IPCA + 4.5%)
        """
        spread_base = spread_index(current_date) - repository.economic.get_ipca_rate(
            current_date
        )
        return self._random_rate(spread_base, 0.01, multiplier)

    def _generate_prefixado_rate(
        self,
        current_date: date,
        base_index: Callable[[date], float],
        multiplier: float = 1.0,
    ) -> float:
        """
        Retorna taxa anual do prefixado (ex: 0.15 = 15% ao ano)
        """
        base_rate = base_index(current_date)

        return self._random_rate(base_rate, 0.01, multiplier)

    def _generate_selic_spread(
        self,
    ) -> float:
        """
        Retorna o spread da SELIC (ex: 0.0005 = SELIC + 0.005%)
        """
        return self._random_rate(base_value=0.00125, delta=0.00075)  # 0.0005-0.002
