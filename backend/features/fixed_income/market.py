import logging
from collections.abc import Callable
from datetime import date
from decimal import Decimal

from backend.core import repository
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.features.fixed_income.factory import FixedIncomeFactory
from backend.features.realtime import notify
from backend.features.realtime.schemas import FixedAssetsUpdateEventDTO

logger = logging.getLogger(__name__)


class FixedIncomeMarket:
    """
    Gerenciador de hall de ativos de renda fixa disponíveis.

    Responsável por:
    - Gerar novos ativos mensalmente usando FixedIncomeFactory, com o CDB de liquidez
      diária fixo e, de vez em quando, a oferta rara
    - Manter catálogo de ativos disponíveis por UUID
    - Notificar players sobre atualizações do hall via realtime
    - Fornecer consultas de ativos disponíveis e busca por UUID
    """

    def __init__(
        self,
        simulation_id: int,
        end_date: date,
        risk_premium_on: Callable[[date], Decimal] = lambda _day: Decimal(0),
    ):
        """`risk_premium_on` dá o prêmio de risco do país que o Tesouro soma às taxas do mês."""
        self._simulation_id = simulation_id
        self._end_date = end_date
        self._risk_premium_on = risk_premium_on
        self._current_month: tuple[int, int] | None = None
        self._assets: dict[str, FixedIncomeAssetDTO] = {}
        self._issued_assets: dict[str, FixedIncomeAssetDTO] = {}

    def refresh_assets(self, current_date: date):
        self._issued_assets = {
            uuid: asset
            for uuid, asset in self._issued_assets.items()
            if asset.maturity_date > current_date
        }
        current_month = (current_date.year, current_date.month)
        if self._current_month == current_month:
            return

        self._current_month = current_month
        self._generate_assets()

    def get_available_assets(self) -> list[FixedIncomeAssetDTO]:
        return list(self._assets.values())

    def get_asset(self, uuid: str) -> FixedIncomeAssetDTO | None:
        asset = self._issued_assets.get(uuid)
        if asset:
            return asset

        asset = repository.fixed_income.get_asset_by_uuid(uuid)
        return asset

    def _generate_assets(self):
        if self._current_month is None:
            return

        year, month = self._current_month
        current_date = date(year, month, 1)

        # O CDB de 100% do CDI abre a vitrine; a oferta rara aparece em parte dos meses
        fixed = FixedIncomeFactory.daily_liquidity_cdb(
            self._simulation_id, self._end_date
        )
        rare = FixedIncomeFactory.rare_daily_liquidity_offer(current_date)
        self._assets = {
            str(asset.asset_uuid): asset for asset in (fixed, rare) if asset is not None
        }
        self._assets.update(
            FixedIncomeFactory.generate_assets(
                current_date=current_date,
                n=10,
                risk_premium=self._risk_premium_on(current_date),
            )
        )
        # A renovação da vitrine não invalida uma oferta ainda aberta no navegador.
        self._issued_assets.update(self._assets)
        notify(
            "fixed_assets_update",
            FixedAssetsUpdateEventDTO(assets=self.get_available_assets()).to_json(),
        )
        logger.info(f"Gerados {len(self._assets)} ativos de renda fixa")
