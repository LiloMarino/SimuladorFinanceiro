import random
from datetime import datetime, timedelta

from backend.simulation.entities.fixed_income_asset import (
    FixedIncomeAsset,
    FixedIncomeType,
    RateIndexType,
)
from backend.simulation.fixed_income_factory.abstract_factory import (
    AbstractFixedIncomeFactory,
)
from backend.simulation.fixed_income_factory.cdb_factory import CDBFactory
from backend.simulation.fixed_income_factory.lca_factory import LCAFactory
from backend.simulation.fixed_income_factory.lci_factory import LCIFactory
from backend.simulation.fixed_income_factory.tesouro_factory import TesouroFactory


class FixedIncomeFactory:
    _registry: dict[FixedIncomeType, AbstractFixedIncomeFactory] = {
        FixedIncomeType.CDB: CDBFactory(),
        FixedIncomeType.LCI: LCIFactory(),
        FixedIncomeType.LCA: LCAFactory(),
        FixedIncomeType.TESOURO_DIRETO: TesouroFactory(),
    }

    @classmethod
    def available_types(cls):
        return list(cls._registry.keys())

    @classmethod
    def get_factory(cls, asset_type: FixedIncomeType) -> AbstractFixedIncomeFactory:
        return cls._registry[asset_type]

    @classmethod
    def generate_assets(cls, n: int, seed: int | None = None) -> list[FixedIncomeAsset]:
        if seed is not None:
            random.seed(seed)

        combinations: list[tuple[FixedIncomeType, RateIndexType]] = []
        for asset_type, factory in cls._registry.items():
            for index in factory.valid_indexes:
                combinations.append((asset_type, index))

        total_combos = len(combinations)
        base_count = n // total_combos
        remainder = n % total_combos

        generated: list[FixedIncomeAsset] = []
        names_seen: set[str] = set()

        # Distribui uniformemente
        for asset_type, rate_index in combinations:
            factory = cls._registry[asset_type]
            for _ in range(base_count):
                asset = factory.create_asset(rate_index)
                # garante unicidade
                while asset.name in names_seen:
                    asset = factory.create_asset(rate_index)
                names_seen.add(asset.name)
                generated.append(asset)

        # Distribui o restante aleatoriamente
        extras = random.sample(combinations, remainder)
        for asset_type, rate_index in extras:
            factory = cls._registry[asset_type]
            asset = factory.create_asset(rate_index)
            while asset.name in names_seen:
                asset = factory.create_asset(rate_index)
            names_seen.add(asset.name)
            generated.append(asset)

        return generated
