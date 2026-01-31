from datetime import date

from backend.core import repository
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.logger import setup_logger
from backend.features.fixed_income.factory import FixedIncomeFactory
from backend.features.realtime import notify

logger = setup_logger(__name__)


class FixedIncomeMarket:
    """
    Gerenciador de hall de ativos de renda fixa disponíveis.

    Responsável por:
    - Gerar novos ativos mensalmente usando FixedIncomeFactory
    - Manter catálogo de ativos disponíveis por UUID
    - Notificar players sobre atualizações do hall via realtime
    - Fornecer consultas de ativos disponíveis e busca por UUID
    """

    def __init__(self):
        self._current_month: tuple[int, int] | None = None
        self._assets: dict[str, FixedIncomeAssetDTO] = {}

    def refresh_assets(self, current_date: date):
        current_month = (current_date.year, current_date.month)
        if self._current_month == current_month:
            return

        self._current_month = current_month
        self._generate_assets()

    def get_available_assets(self) -> list[FixedIncomeAssetDTO]:
        return list(self._assets.values())

    def get_asset(self, uuid: str) -> FixedIncomeAssetDTO | None:
        asset = self._assets.get(uuid)
        if asset:
            return asset

        asset = repository.fixed_income.get_asset_by_uuid(uuid)
        return asset

    def _generate_assets(self):
        if self._current_month is None:
            return

        year, month = self._current_month
        current_date = date(year, month, 1)

        self._assets = FixedIncomeFactory.generate_assets(
            current_date=current_date, n=10
        )
        notify(
            "fixed_assets_update",
            {"assets": [asset.to_json() for asset in self.get_available_assets()]},
        )
        logger.info(f"Gerados {len(self._assets)} ativos de renda fixa")
