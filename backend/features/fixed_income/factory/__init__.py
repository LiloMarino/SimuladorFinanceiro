import calendar
import random
from collections.abc import Mapping
from datetime import date, timedelta
from decimal import Decimal
from types import MappingProxyType
from uuid import NAMESPACE_URL, uuid5

from backend.core.dto.fixed_income_asset import (
    FixedIncomeAssetDTO,
)
from backend.core.enum import FixedIncomeType, RateIndexType
from backend.features.fixed_income.factory.abstract_factory import (
    AbstractFixedIncomeFactory,
)
from backend.features.fixed_income.factory.cdb_factory import CDBFactory
from backend.features.fixed_income.factory.lca_factory import LCAFactory
from backend.features.fixed_income.factory.lci_factory import LCIFactory
from backend.features.fixed_income.factory.tesouro_factory import (
    TesouroFactory,
)

# CDB de 100% do CDI com liquidez diária: aberto a partida inteira
DAILY_LIQUIDITY_ISSUER = "Nubank"
DAILY_LIQUIDITY_CDI_PCT = Decimal("1")
# Vence um ano depois do fim da partida, para nunca vencer durante ela
DAILY_LIQUIDITY_MATURITY_AFTER_END = timedelta(days=365)

# Oferta rara de liquidez diária acima de 100% do CDI: sai no catálogo do mês
RARE_OFFER_CHANCE = 1 / 3
RARE_OFFER_CDI_PCT_RANGE = (Decimal("1.02"), Decimal("1.10"))
RARE_OFFER_RATE_STEP = Decimal("0.005")
RARE_OFFER_PLAYER_CAP = Decimal("20000")
RARE_OFFER_MATURITY_YEARS = (2, 3)
# (emissor, nome curto que entra no título)
RARE_OFFER_ISSUERS = (
    ("PicPay Bank", "PicPay"),
    ("Banco Inter", "Banco Inter"),
    ("Mercado Pago", "Mercado Pago"),
    ("C6 Bank", "C6 Bank"),
    ("Banco Pan", "Banco Pan"),
)


class FixedIncomeFactory:
    """
    Registry e orquestrador de factories de renda fixa.

    Responsável por:
    - Manter registro de factories por tipo de ativo (CDB, LCI, LCA, Tesouro)
    - Gerar ativos de forma balanceada entre tipos e indexadores
    - Garantir distribuição uniforme de combinações (tipo + indexador)
    - Fornecer interface simplificada para geração em lote
    """

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
        cls, current_date: date, n: int, seed: int | None = None
    ) -> dict[str, FixedIncomeAssetDTO]:
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

        generated: dict[str, FixedIncomeAssetDTO] = {}

        # Cria número fixo por combinação
        for asset_type, rate_index in combinations:
            factory = cls._registry[asset_type]
            for _ in range(base_count):
                asset = factory.create_asset(rate_index, current_date)
                generated[str(asset.asset_uuid)] = asset

        # Restante aleatório porém balanceado
        extras = random.sample(combinations, remainder)
        for asset_type, rate_index in extras:
            factory = cls._registry[asset_type]
            asset = factory.create_asset(rate_index, current_date)
            generated[str(asset.asset_uuid)] = asset

        return generated

    @classmethod
    def daily_liquidity_cdb(
        cls, simulation_id: int, end_date: date
    ) -> FixedIncomeAssetDTO:
        """O CDB de 100% do CDI; o UUID é estável por partida, então a retomada mostra o mesmo título."""
        return FixedIncomeAssetDTO(
            asset_uuid=uuid5(NAMESPACE_URL, f"daily-liquidity-cdb/{simulation_id}"),
            name=f"CDB {DAILY_LIQUIDITY_ISSUER} Liquidez Diária",
            issuer=DAILY_LIQUIDITY_ISSUER,
            investment_type=FixedIncomeType.CDB,
            rate_index=RateIndexType.CDI,
            maturity_date=end_date + DAILY_LIQUIDITY_MATURITY_AFTER_END,
            interest_rate=DAILY_LIQUIDITY_CDI_PCT,
            daily_liquidity=True,
        )

    @classmethod
    def rare_daily_liquidity_offer(
        cls, current_date: date
    ) -> FixedIncomeAssetDTO | None:
        """
        A oferta rara do mês: um CDB acima de 100% do CDI com liquidez diária,
        com teto por jogador, que sai do catálogo no último dia do mês.
        """
        if random.random() >= RARE_OFFER_CHANCE:
            return None

        low, high = RARE_OFFER_CDI_PCT_RANGE
        steps = int((high - low) / RARE_OFFER_RATE_STEP)
        rate = low + RARE_OFFER_RATE_STEP * random.randint(0, steps)
        issuer, short_name = random.choice(RARE_OFFER_ISSUERS)
        min_years, max_years = RARE_OFFER_MATURITY_YEARS
        last_day = calendar.monthrange(current_date.year, current_date.month)[1]
        return FixedIncomeAssetDTO(
            name=f"CDB {short_name} Liquidez Diária",
            issuer=issuer,
            investment_type=FixedIncomeType.CDB,
            rate_index=RateIndexType.CDI,
            maturity_date=current_date
            + timedelta(days=random.randint(min_years * 365, max_years * 365)),
            interest_rate=rate,
            daily_liquidity=True,
            player_cap=RARE_OFFER_PLAYER_CAP,
            offered_until=current_date.replace(day=last_day),
        )
