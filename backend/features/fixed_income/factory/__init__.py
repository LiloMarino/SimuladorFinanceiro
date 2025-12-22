import random
from collections.abc import Mapping
from datetime import datetime
from types import MappingProxyType

from backend.core.dto.fixed_income_asset import FixedIncomeType, RateIndexType
from backend.features.fixed_income.factory.abstract_factory import (
    AbstractFixedIncomeFactory,
)
from backend.features.fixed_income.factory.cdb_factory import CDBFactory
from backend.features.fixed_income.factory.lca_factory import LCAFactory
from backend.features.fixed_income.factory.lci_factory import LCIFactory
from backend.features.fixed_income.factory.tesouro_factory import (
    TesouroFactory,
)
from backend.features.simulation.entities.fixed_income_asset import (
    FixedIncomeAsset,
)


class FixedIncomeFactory:
    _registry: Mapping[FixedIncomeType, AbstractFixedIncomeFactory] = MappingProxyType(
        {
            FixedIncomeType.CDB: CDBFactory(),
            FixedIncomeType.LCI: LCIFactory(),
            FixedIncomeType.LCA: LCAFactory(),
            FixedIncomeType.TESOURO_DIRETO: TesouroFactory(),
        }
    )

    @classmethod
    def available_types(cls):
        return list(cls._registry.keys())

    @classmethod
    def get_factory(cls, asset_type: FixedIncomeType) -> AbstractFixedIncomeFactory:
        return cls._registry[asset_type]

    @classmethod
    def generate_assets(
        cls, current_date: datetime, n: int, seed: int | None = None
    ) -> dict[str, FixedIncomeAsset]:
        if seed is not None:
            random.seed(seed)

        combinations: list[tuple[FixedIncomeType, RateIndexType]] = [
            (atype, idx)
            for atype, factory in cls._registry.items()
            for idx in factory.valid_indexes
        ]
        total_combos = len(combinations)

        # Garante distribuição balanceada
        base_count = n // total_combos
        remainder = n % total_combos

        generated: dict[str, FixedIncomeAsset] = {}

        # Cria número fixo por combinação
        for asset_type, rate_index in combinations:
            factory = cls._registry[asset_type]
            for _ in range(base_count):
                asset = factory.create_asset(rate_index, current_date)
                generated[asset.uuid] = asset

        # Restante aleatório porém balanceado
        extras = random.sample(combinations, remainder)
        for asset_type, rate_index in extras:
            factory = cls._registry[asset_type]
            asset = factory.create_asset(rate_index, current_date)
            generated[asset.uuid] = asset

        return generated
