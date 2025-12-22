from datetime import datetime

from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.logger import setup_logger
from backend.features.fixed_income.factory import FixedIncomeFactory
from backend.features.realtime import notify

logger = setup_logger(__name__)


class FixedIncomeMarket:
    """Gera e mantém o hall de ativos de renda fixa disponíveis."""

    def __init__(self):
        self._current_month: tuple[int, int] | None = None
        self._assets: dict[str, FixedIncomeAssetDTO] = {}

    def refresh_assets(self, current_date: datetime):
        current_month = (current_date.year, current_date.month)
        if self._current_month == current_month:
            return

        self._current_month = current_month
        self._generate_assets()

    def get_available_assets(self) -> list[FixedIncomeAssetDTO]:
        return list(self._assets.values())

    def get_asset(self, uuid: str) -> FixedIncomeAssetDTO | None:
        return self._assets.get(uuid)

    def _generate_assets(self):
        if self._current_month is None:
            return

        year, month = self._current_month
        current_date = datetime(year, month, 1)

        self._assets = FixedIncomeFactory.generate_assets(
            current_date=current_date, n=10
        )
        notify(
            "fixed_assets_update",
            {"assets": [asset.to_json() for asset in self.get_available_assets()]},
        )
        logger.info(f"Gerados {len(self._assets)} ativos de renda fixa")
